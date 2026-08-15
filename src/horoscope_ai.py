"""
AI Reading Generation - Supports Local (Ollama) and Cloud (Nemotron)
"""

import time
import ollama
from openai import OpenAI
from astro_calc import chart_summary_text
from api_key_manager import key_manager
from typing import Dict, Any, Generator

# Model configurations
LOCAL_MODEL = "qwen2.5:3b"
NEMOTRON_MODEL = "nvidia/nemotron-3-super-120b-a12b"  # Updated model
NEMOTRON_API_URL = "https://integrate.api.nvidia.com/v1"

# System prompts for different languages
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

# Extended prompts for more detailed readings
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
                    timeout=60.0  # Longer timeout for reasoning model
                )
                return True
            except Exception as e:
                self.nemotron_client = None
                self.last_error = f"Failed to initialize Nemotron: {e}"
                return False
        return False
    
    def generate_reading(self, chart, name: str, lang: str = "en", 
                        mode: str = "local", extended: bool = False) -> str:
        """
        Generate AI reading for the chart
        
        Args:
            chart: BirthChart object
            name: Person's name
            lang: "en" or "hi"
            mode: "local" or "nemotron"
            extended: If True, generate more detailed reading
        """
        # Get chart summary
        summary = chart_summary_text(chart, lang="en")
        
        # Build prompts
        system_prompt, user_prompt = self._build_prompts(
            summary, name, lang, extended
        )
        
        # Generate based on mode
        if mode == "nemotron":
            return self._generate_nemotron(system_prompt, user_prompt, lang)
        else:
            return self._generate_local(system_prompt, user_prompt, lang)
    
    def generate_reading_stream(self, chart, name: str, lang: str = "en", 
                               mode: str = "local", extended: bool = False) -> Generator:
        """
        Generate AI reading with streaming response
        """
        summary = chart_summary_text(chart, lang="en")
        system_prompt, user_prompt = self._build_prompts(
            summary, name, lang, extended
        )
        
        if mode == "nemotron":
            yield from self._generate_nemotron_stream(system_prompt, user_prompt, lang)
        else:
            yield self._generate_local(system_prompt, user_prompt, lang)
    
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
            
            # Clean up any markdown
            content = content.replace('**', '').replace('##', '').replace('*', '')
            content = content.replace('#', '').replace('- ', '').replace('• ', '')
            
            return content
            
        except Exception as e:
            if lang == "hi":
                return (
                    f"[त्रुटि: लोकल मॉडल से संपर्क नहीं हो सका। "
                    f"सुनिश्चित करें कि Ollama चल रहा है। "
                    f"विवरण: {e}]\n\n"
                    f"टिप: 'ollama serve' चलाएं और फिर प्रयास करें।"
                )
            return (
                f"[Error: could not reach local model. Make sure Ollama is running. "
                f"Details: {e}]\n\n"
                f"Tip: Run 'ollama serve' and try again."
            )
    
    def _generate_nemotron(self, system_prompt: str, user_prompt: str, lang: str) -> str:
        """Generate reading using NVIDIA Nemotron with reasoning capabilities"""
        # Check if client is initialized
        if not self.nemotron_client:
            if not self._init_nemotron():
                if lang == "hi":
                    return (
                        "त्रुटि: Nemotron API कुंजी कॉन्फ़िगर नहीं की गई है।\n\n"
                        "कृपया 'Settings' → 'API Settings' पर जाकर अपनी Nemotron API कुंजी सेट करें।\n"
                        "मुफ्त कुंजी प्राप्त करें: https://build.nvidia.com"
                    )
                return (
                    "Error: Nemotron API key not configured.\n\n"
                    "Please set up your API key in 'Settings' → 'API Settings'.\n"
                    "Get a free key from: https://build.nvidia.com"
                )
        
        try:
            # Combine system and user messages
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            # Use the correct Nemotron-3 Super model with reasoning
            response = self.nemotron_client.chat.completions.create(
                model=NEMOTRON_MODEL,
                messages=messages,
                temperature=1.0,
                top_p=0.95,
                max_tokens=16384,
                extra_body={
                    "chat_template_kwargs": {
                        "enable_thinking": True  # Enable reasoning/thinking
                    },
                    "reasoning_budget": 16384  # Budget for reasoning tokens
                },
                stream=False
            )
            
            content = response.choices[0].message.content
            
            # Clean up any markdown
            content = content.replace('**', '').replace('##', '').replace('*', '')
            content = content.replace('#', '').replace('- ', '').replace('• ', '')
            
            return content
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle specific errors
            if "authentication" in error_msg or "api key" in error_msg:
                if lang == "hi":
                    return (
                        "त्रुटि: Nemotron API कुंजी अमान्य है।\n\n"
                        "कृपया 'Settings' → 'API Settings' पर जाकर अपनी API कुंजी जांचें।\n"
                        "मुफ्त कुंजी प्राप्त करें: https://build.nvidia.com"
                    )
                return (
                    "Error: Invalid Nemotron API key.\n\n"
                    "Please check your API key in 'Settings' → 'API Settings'.\n"
                    "Get a free key from: https://build.nvidia.com"
                )
            
            elif "rate" in error_msg:
                if lang == "hi":
                    return (
                        "त्रुटि: दर सीमा पार हो गई। कृपया कुछ समय बाद पुनः प्रयास करें।\n\n"
                        "Nemotron की मुफ्त योजना में सीमित अनुरोध हैं।"
                    )
                return (
                    "Error: Rate limit exceeded. Please try again later.\n\n"
                    "The free Nemotron tier has limited requests."
                )
            
            elif "model" in error_msg and "not found" in error_msg:
                if lang == "hi":
                    return (
                        f"त्रुटि: मॉडल '{NEMOTRON_MODEL}' उपलब्ध नहीं है।\n\n"
                        f"कृपया जांचें कि आपके NVIDIA खाते में इस मॉडल तक पहुंच है।"
                    )
                return (
                    f"Error: Model '{NEMOTRON_MODEL}' is not available.\n\n"
                    f"Please check if you have access to this model in your NVIDIA account."
                )
            
            else:
                if lang == "hi":
                    return f"त्रुटि: Nemotron के साथ भविष्यफल उत्पन्न करने में समस्या: {e}"
                return f"Error generating reading with Nemotron: {e}"
    
    def _generate_nemotron_stream(self, system_prompt: str, user_prompt: str, lang: str) -> Generator:
        """Generate reading with streaming for real-time output"""
        if not self.nemotron_client:
            if not self._init_nemotron():
                yield "Error: Nemotron API key not configured."
                return
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            stream = self.nemotron_client.chat.completions.create(
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
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            yield f"\n\nError: {str(e)}"
    
    def get_ai_status(self) -> Dict[str, Any]:
        """Get status of all AI providers"""
        status = {
            "local": {
                "available": False,
                "model": self.local_model,
                "message": ""
            },
            "nemotron": {
                "available": False,
                "model": NEMOTRON_MODEL,
                "message": ""
            }
        }
        
        # Check local (Ollama)
        try:
            models = ollama.list()
            model_names = [m.get("model", m.get("name", "")) for m in models.get("models", [])]
            if any(self.local_model.split(":")[0] in n for n in model_names):
                status["local"]["available"] = True
                status["local"]["message"] = f"✅ {self.local_model} available"
            else:
                status["local"]["message"] = f"⚠️ {self.local_model} not pulled. Run: ollama pull {self.local_model}"
        except Exception as e:
            status["local"]["message"] = f"❌ Ollama not reachable: {e}"
        
        # Check Nemotron
        has_key = key_manager.has_key("nemotron")
        if has_key:
            api_key = key_manager.get_nemotron_key()
            if api_key:
                status["nemotron"]["available"] = True
                status["nemotron"]["message"] = f"✅ Nemotron API key configured (Model: {NEMOTRON_MODEL})"
            else:
                status["nemotron"]["message"] = "❌ Nemotron API key missing"
        else:
            status["nemotron"]["message"] = "ℹ️ Nemotron API key not configured"
        
        return status


def generate_reading(chart, name: str, lang: str = "en", 
                    mode: str = "local", extended: bool = False) -> str:
    """
    Convenience function to generate reading
    """
    generator = AIHoroscopeGenerator()
    return generator.generate_reading(chart, name, lang, mode, extended)


def generate_reading_stream(chart, name: str, lang: str = "en", 
                          mode: str = "local", extended: bool = False) -> Generator:
    """
    Convenience function to generate reading with streaming
    """
    generator = AIHoroscopeGenerator()
    yield from generator.generate_reading_stream(chart, name, lang, mode, extended)


def test_nemotron_key(api_key: str) -> Dict[str, Any]:
    """
    Test if a Nemotron API key is valid with the correct model
    
    Returns:
        Dict with success, model, response_time, and any error
    """
    try:
        start_time = time.time()
        client = OpenAI(
            base_url=NEMOTRON_API_URL,
            api_key=api_key,
            timeout=30.0
        )
        
        # Test with the actual Nemotron-3 model
        response = client.chat.completions.create(
            model=NEMOTRON_MODEL,
            messages=[
                {"role": "user", "content": "Hello, respond with exactly 'OK'"}
            ],
            temperature=0.1,
            max_tokens=10,
            extra_body={
                "chat_template_kwargs": {
                    "enable_thinking": False  # Disable thinking for quick test
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
            "message": f"✅ Nemotron-3 Super model is working!"
        }
        
    except Exception as e:
        error_msg = str(e)
        
        if "authentication" in error_msg.lower() or "api key" in error_msg.lower():
            return {
                "success": False,
                "error": "Invalid API key - authentication failed. Please check your key."
            }
        elif "rate" in error_msg.lower():
            return {
                "success": False,
                "error": "Rate limit exceeded. Please try again later."
            }
        elif "model" in error_msg.lower() and "not found" in error_msg.lower():
            return {
                "success": False,
                "error": f"Model '{NEMOTRON_MODEL}' not available. Check your NVIDIA account access."
            }
        elif "timeout" in error_msg.lower():
            return {
                "success": False,
                "error": "Connection timeout. Please check your internet connection."
            }
        else:
            return {
                "success": False,
                "error": f"Error: {error_msg}"
            }


def is_ollama_available() -> tuple[bool, str]:
    """
    Check if Ollama is available and has the required model
    
    Returns:
        (is_available, message)
    """
    try:
        models = ollama.list()
        model_names = [m.get("model", m.get("name", "")) for m in models.get("models", [])]
        
        if not model_names:
            return False, "No models found in Ollama. Run: ollama pull " + LOCAL_MODEL
        
        if any(LOCAL_MODEL.split(":")[0] in n for n in model_names):
            return True, f"✅ {LOCAL_MODEL} available"
        else:
            return False, f"Model '{LOCAL_MODEL}' not found. Run: ollama pull {LOCAL_MODEL}"
            
    except Exception as e:
        return False, f"Can't reach Ollama: {e}\n\nMake sure Ollama is running:\nWindows: 'ollama serve' in cmd\nmacOS/Linux: 'ollama serve' in terminal"


def get_available_models() -> Dict[str, Dict]:
    """
    Get all available AI models and their status
    """
    status = {
        "local": {
            "name": "Ollama (Local)",
            "model": LOCAL_MODEL,
            "status": "checking...",
            "available": False
        },
        "nemotron": {
            "name": "NVIDIA Nemotron-3 Super (Cloud)",
            "model": NEMOTRON_MODEL,
            "status": "checking...",
            "available": False,
            "features": ["Reasoning/Thinking", "16384 tokens", "Streaming"]
        }
    }
    
    # Check local
    available, msg = is_ollama_available()
    status["local"]["available"] = available
    status["local"]["status"] = msg
    
    # Check Nemotron
    has_key = key_manager.has_key("nemotron")
    if has_key:
        status["nemotron"]["available"] = True
        status["nemotron"]["status"] = "✅ API key configured"
    else:
        status["nemotron"]["available"] = False
        status["nemotron"]["status"] = "ℹ️ No API key configured"
    
    return status