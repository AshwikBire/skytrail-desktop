"""
Cloud reading option: NVIDIA NIM API (free tier), running Nemotron.
Mirrors horoscope_ai.py's interface but calls the NVIDIA-hosted model instead
of local Ollama — for sharper, faster AI readings when you have internet.
"""
import os
from dotenv import load_dotenv
from openai import OpenAI
from astro_calc import chart_summary_text

load_dotenv()

MODEL_NAME = "nvidia/llama-3.3-nemotron-super-49b-v1"
BASE_URL = "https://integrate.api.nvidia.com/v1"

SYSTEM_PROMPT_EN = (
    "You are an experienced, warm astrologer. You are given a birth chart summary "
    "(planet positions, ascendant, nakshatra if present). Write a short, insightful "
    "reading in English: 2 short paragraphs covering personality/temperament and "
    "current life themes. Be specific to the chart data given, not generic. "
    "No markdown, no headers, no bullet points — just flowing prose."
)

SYSTEM_PROMPT_HI = (
    "आप एक अनुभवी, स्नेहिल ज्योतिषी हैं। आपको एक जन्म कुंडली का सारांश दिया गया है "
    "(ग्रहों की स्थिति, लग्न, और यदि उपलब्ध हो तो नक्षत्र)। हिंदी में एक संक्षिप्त, सारगर्भित "
    "भविष्यफल लिखें: व्यक्तित्व/स्वभाव और वर्तमान जीवन की मुख्य बातों पर 2 छोटे पैराग्राफ। "
    "दी गई कुंडली के अनुसार विशिष्ट रहें, सामान्य बातें न लिखें। कोई मार्कडाउन नहीं — केवल "
    "स्वाभाविक गद्य में लिखें।"
)


def _client():
    api_key = os.environ.get("NVIDIA_API_KEY", "")
    if not api_key or api_key.startswith("nvapi-your-key"):
        return None
    return OpenAI(base_url=BASE_URL, api_key=api_key)


def generate_reading_nemotron(chart, name: str, lang: str = "en") -> str:
    client = _client()
    if client is None:
        if lang == "hi":
            return "[NVIDIA API कुंजी नहीं मिली। .env.example को .env में बदलें और अपनी कुंजी जोड़ें।]"
        return "[No NVIDIA API key found. Copy .env.example to .env and add your key.]"

    summary = chart_summary_text(chart, lang="en")
    system_prompt = SYSTEM_PROMPT_HI if lang == "hi" else SYSTEM_PROMPT_EN
    if lang == "hi":
        user_prompt = f"नाम: {name}\n\nकुंडली सारांश:\n{summary}\n\nकृपया भविष्यफल लिखें।"
    else:
        user_prompt = f"Name: {name}\n\nChart summary:\n{summary}\n\nPlease write the reading."

    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=500,
        )
        return response.choices[0].message.content
    except Exception as e:
        if lang == "hi":
            return f"[त्रुटि: NVIDIA API से संपर्क नहीं हो सका। विवरण: {e}]"
        return f"[Error: could not reach NVIDIA API. Details: {e}]"


def is_nemotron_available() -> tuple[bool, str]:
    client = _client()
    if client is None:
        return False, "No NVIDIA API key found. Copy .env.example to .env and add your key."
    try:
        client.chat.completions.create(
            model=MODEL_NAME, messages=[{"role": "user", "content": "hi"}], max_tokens=1
        )
        return True, "OK"
    except Exception as e:
        return False, f"NVIDIA API error: {e}"
