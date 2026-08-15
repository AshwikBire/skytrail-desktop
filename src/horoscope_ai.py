"""
AI Reading Generation - Supports Local (Ollama) and Cloud (Nemotron)
"""

import time
import requests
import socket
import ollama
from openai import OpenAI
from astro_calc import chart_summary_text
from api_key_manager import key_manager
from typing import Dict, Any, Generator

# Model configurations
LOCAL_MODEL = "qwen2.5:3b"
NEMOTRON_MODEL = "nvidia/nemotron-3-super-120b-a12b"
NEMOTRON_API_URL = "https://integrate.api.nvidia.com/v1"

# System prompts
SYSTEM_PROMPT_EN = (
    "You are an experienced, warm astrologer. You are given a birth chart summary "
    "(planet positions, ascendant, nakshatra if present). Write a short, insightful "
    "reading in English: 2 short paragraphs covering personality/temperament and "
    "current life themes. Be specific to the chart data given, not generic. "
    "No markdown, no headers, no bullet points — just flowing prose, as if speaking "
    "warmly to the person."
)

SYSTEM_PROMPT_HI = (
    "आप एक अनुभवी, स्नेहिल ज्योतिषी हैं। आपको एक जन्म कुंडली का सारांश दिया गया है "
    "(ग्रहों की स्थिति, लग्न, और यदि उपलब्ध हो तो नक्षत्र)। हिंदी में एक संक्षिप्त, सारगर्भित "
    "भविष्यफल लिखें: व्यक्तित्व/स्वभाव और वर्तमान जीवन की मुख्य बातों पर 2 छोटे पैराग्राफ। "
    "दी गई कुंडली के अनुसार विशिष्ट रहें, सामान्य बातें न लिखें। कोई मार्कडाउन, हेडर या "
    "बुलेट पॉइंट नहीं — केवल स्वाभाविक, स्नेहपूर्ण गद्य में लिखें।"
)

EXTENDED_PROMPT_EN = (
    "You are an experienced, warm astrologer with deep knowledge of both Vedic and Western astrology. "
    "Based on the birth chart provided, write a comprehensive, insightful reading. "
    "Cover the following aspects:\n"
    "1. Core personality traits and temperament\n"
    "2. Strengths and natural talents\n"
    "3. Areas for growth and life lessons\n"
    "4. Career and life path indications\n"
    "5. Relationships and emotional nature\n\n"
    "Be specific to the chart data given. Write in a warm, personal tone. "
    "No markdown, no bullet points — just flowing prose."
)

EXTENDED_PROMPT_HI = (
    "आप एक अनुभवी, स्नेहिल ज्योतिषी हैं जिन्हें वैदिक और पाश्चात्य दोनों ज्योतिष का गहरा ज्ञान है। "
    "दी गई जन्म कुंडली के आधार पर एक व्यापक, अंतर्दृष्टिपूर्ण भविष्यफल लिखें। "
    "निम्नलिखित पहलुओं को शामिल करें:\n"
    "1. मुख्य व्यक्तित्व लक्षण और स्वभाव\n"
    "2. ताकत और प्राकृतिक प्रतिभाएं\n"
    "3. विकास के क्षेत्र और जीवन पाठ\n"
    "4. करियर और जीवन पथ के संकेत\n"
    "5. रिश्ते और भावनात्मक प्रकृति\n\n"
    "दी गई कुंडली के अनुसार विशिष्ट रहें। स्नेहपूर्ण, व्यक्तिगत शैली में लिखें। "
    "कोई मार्कडाउन, बुलेट पॉइंट नहीं — केवल प्रवाहपूर्ण गद्य।"
)


class AIHoroscopeGenerator:
    """Generate horoscope readings using AI (Local or Cloud)"""
    
    def __init__(self):
        self.local_model = LOCAL_MODEL
        self.nemotron_client = None
        self._init_nemotron()
        self.last_error = None
    
    def _init_nemotron(self):
        """Initialize Nemotron client if API key exists"""
        api_key = key_manager.get_nemotron_key()
        if api_key:
            try:
                self.nemotron_client = OpenAI(
                    base_url=NEMOTRON_API_URL,
                    api_key=api_key,
                    timeout=60.0
                )
                return True
            except Exception as e:
                self.nemotron_client = None
                self.last_error = f"Failed to initialize Nemotron: {e}"
                return False
        return False
    
    def _check_ollama_connection(self) -> tuple[bool, str]:
        """Check if Ollama is running and accessible"""
        try:
            # Try to connect to Ollama
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                return True, "Connected"
            return False, f"Status: {response.status_code}"
        except requests.exceptions.ConnectionError:
            return False, "Ollama not running (Connection refused)"
        except requests.exceptions.Timeout:
            return False, "Connection timeout"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def _check_model_available(self) -> tuple[bool, str]:
        """Check if the required model is available"""
        try:
            response = requests.get("http://localhost:11434/api/tags", timeout=3)
            if response.status_code == 200:
                data = response.json()
                models = data.get("models", [])
                model_names = [m.get("name", "") for m in models]
                
                # Check if qwen2.5:3b or any qwen model is available
                for name in model_names:
                    if "qwen" in name.lower():
                        return True, f"Found: {name}"
                
                if model_names:
                    return False, f"No qwen model. Available: {', '.join(model_names[:3])}"
                return False, "No models found. Run: ollama pull qwen2.5:3b"
            return False, "Cannot check models"
        except:
            return False, "Cannot connect to Ollama"
    
    def generate_reading(self, chart, name: str, lang: str = "en", 
                        mode: str = "local", extended: bool = False) -> str:
        """Generate AI reading for the chart"""
        summary = chart_summary_text(chart, lang="en")
        system_prompt, user_prompt = self._build_prompts(
            summary, name, lang, extended
        )
        
        if mode == "nemotron":
            return self._generate_nemotron(system_prompt, user_prompt, lang)
        else:
            return self._generate_local(system_prompt, user_prompt, lang)
    
    def _build_prompts(self, summary: str, name: str, lang: str, extended: bool):
        """Build system and user prompts"""
        if lang == "hi":
            system_prompt = EXTENDED_PROMPT_HI if extended else SYSTEM_PROMPT_HI
            user_prompt = f"नाम: {name}\n\nकुंडली सारांश:\n{summary}\n\nकृपया भविष्यफल लिखें।"
        else:
            system_prompt = EXTENDED_PROMPT_EN if extended else SYSTEM_PROMPT_EN
            user_prompt = f"Name: {name}\n\nChart summary:\n{summary}\n\nPlease write the reading."
        
        return system_prompt, user_prompt
    
    def _generate_local(self, system_prompt: str, user_prompt: str, lang: str) -> str:
        """Generate reading using local Ollama model"""
        # Check if Ollama is running
        connected, msg = self._check_ollama_connection()
        
        if not connected:
            if lang == "hi":
                return (
                    "⚠️ Ollama कनेक्ट नहीं हो पा रहा है।\n\n"
                    "कृपया निम्न चरणों का पालन करें:\n"
                    "1. एक नया कमांड प्रॉम्प्ट खोलें\n"
                    "2. 'ollama serve' चलाएं\n"
                    "3. Ollama सर्वर चालू होने के बाद 'ollama pull qwen2.5:3b' चलाएं\n"
                    "4. फिर इस ऐप पर वापस आकर पुनः प्रयास करें\n\n"
                    f"📌 विवरण: {msg}"
                )
            return (
                "⚠️ Cannot connect to Ollama.\n\n"
                "Please follow these steps:\n"
                "1. Open a new command prompt\n"
                "2. Run 'ollama serve'\n"
                "3. After Ollama starts, run 'ollama pull qwen2.5:3b'\n"
                "4. Then come back to this app and try again\n\n"
                f"📌 Details: {msg}"
            )
        
        # Check if model is available
        model_available, model_msg = self._check_model_available()
        
        if not model_available:
            if lang == "hi":
                return (
                    f"⚠️ मॉडल उपलब्ध नहीं है।\n\n"
                    f"कृपया चलाएं: ollama pull qwen2.5:3b\n\n"
                    f"📌 {model_msg}"
                )
            return (
                f"⚠️ Model not available.\n\n"
                f"Please run: ollama pull qwen2.5:3b\n\n"
                f"📌 {model_msg}"
            )
        
        try:
            response = ollama.chat(
                model=self.local_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                options={
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "num_predict": 600,
                    "num_ctx": 2048
                },
            )
            content = response["message"]["content"]
            content = content.replace('**', '').replace('##', '').replace('*', '')
            content = content.replace('#', '').replace('- ', '').replace('• ', '')
            return content
            
        except Exception as e:
            if lang == "hi":
                return f"❌ त्रुटि: {str(e)}"
            return f"❌ Error: {str(e)}"
    
    def _generate_nemotron(self, system_prompt: str, user_prompt: str, lang: str) -> str:
        """Generate reading using NVIDIA Nemotron"""
        if not self.nemotron_client:
            if not self._init_nemotron():
                if lang == "hi":
                    return (
                        "❌ Nemotron API कुंजी कॉन्फ़िगर नहीं की गई है।\n\n"
                        "कृपया 'Settings' → 'API Settings' पर जाकर अपनी Nemotron API कुंजी सेट करें।\n"
                        "मुफ्त कुंजी प्राप्त करें: https://build.nvidia.com"
                    )
                return (
                    "❌ Nemotron API key not configured.\n\n"
                    "Please set up your API key in 'Settings' → 'API Settings'.\n"
                    "Get a free key from: https://build.nvidia.com"
                )
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = self.nemotron_client.chat.completions.create(
                model=NEMOTRON_MODEL,
                messages=messages,
                temperature=1.0,
                top_p=0.95,
                max_tokens=16384,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": True
                    },
                    "reasoning_budget": 16384
                },
                stream=False
            )
            
            content = response.choices[0].message.content
            content = content.replace('**', '').replace('##', '').replace('*', '')
            content = content.replace('#', '').replace('- ', '').replace('• ', '')
            return content
            
        except Exception as e:
            error_msg = str(e)
            if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
                if lang == "hi":
                    return "❌ Nemotron API कुंजी अमान्य है। कृपया 'Settings' → 'API Settings' पर जाकर जांचें।"
                return "❌ Invalid Nemotron API key. Please check in 'Settings' → 'API Settings'."
            elif "rate" in error_msg.lower():
                if lang == "hi":
                    return "⏳ दर सीमा पार हो गई। कृपया कुछ समय बाद पुनः प्रयास करें।"
                return "⏳ Rate limit exceeded. Please try again later."
            else:
                if lang == "hi":
                    return f"❌ त्रुटि: {str(e)}"
                return f"❌ Error: {str(e)}"


def generate_reading(chart, name: str, lang: str = "en", 
                    mode: str = "local", extended: bool = False) -> str:
    """Convenience function to generate reading"""
    generator = AIHoroscopeGenerator()
    return generator.generate_reading(chart, name, lang, mode, extended)


def test_nemotron_key(api_key: str) -> Dict[str, Any]:
    """Test if a Nemotron API key is valid"""
    try:
        start_time = time.time()
        client = OpenAI(
            base_url=NEMOTRON_API_URL,
            api_key=api_key,
            timeout=30.0
        )
        
        response = client.chat.completions.create(
            model=NEMOTRON_MODEL,
            messages=[
                {"role": "user", "content": "Hello, respond with exactly 'OK'"}
            ],
            temperature=0.1,
            max_tokens=10,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False
                },
                "reasoning_budget": 100
            }
        )
        
        elapsed_time = time.time() - start_time
        
        return {
            "success": True,
            "model": NEMOTRON_MODEL,
            "response_time": elapsed_time,
            "response": response.choices[0].message.content[:50] if response.choices else "OK",
        }
        
    except Exception as e:
        error_msg = str(e)
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            return {"success": False, "error": "Invalid API key"}
        elif "rate" in error_msg.lower():
            return {"success": False, "error": "Rate limit exceeded"}
        else:
            return {"success": False, "error": error_msg}


def is_ollama_available() -> tuple[bool, str]:
    """Check if Ollama is available"""
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json()
            model_names = [m.get("name", "") for m in models.get("models", [])]
            if any("qwen" in n.lower() for n in model_names):
                return True, f"✅ Ollama connected with qwen model"
            elif model_names:
                return False, f"⚠️ Ollama connected but no qwen model. Available: {', '.join(model_names[:3])}"
            else:
                return False, "⚠️ Ollama connected but no models found. Run: ollama pull qwen2.5:3b"
        return False, "⚠️ Ollama not responding"
    except requests.exceptions.ConnectionError:
        return False, "⚠️ Cannot connect to Ollama. Run: ollama serve"
    except Exception as e:
        return False, f"⚠️ Error: {str(e)}"