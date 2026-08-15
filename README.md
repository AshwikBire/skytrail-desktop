# SkyTrail Desktop

Vedic & Western astrology app with a holographic UI, bilingual (English/Hindi),
fully offline — no API keys, no cloud costs. Uses the same local Ollama model
as your Jarvis project for AI-generated readings.

## What it does
- Computes real birth charts (planetary positions, ascendant, nakshatra for Vedic)
  using `pyswisseph` (Swiss Ephemeris) — accurate offline, no downloaded data files needed
- Toggle between **Vedic** (sidereal, Lahiri ayanamsa) and **Western** (tropical) systems
- Toggle between **English** and **Hindi** for the whole UI, chart labels, and AI reading
- Holographic zodiac wheel — planets glow at their actual positions, matching the
  Jarvis visual style
- AI-generated personality/life-theme reading from the local model, in the chosen language
- Quick-pick presets for Pune, Amravati, Mumbai, Delhi, Bengaluru (lat/long/timezone)

## Requirements
Same as Jarvis: Python 3.12, Ollama installed with `qwen2.5:3b` pulled.
If you already set these up for Jarvis, you're 90% done — this app reuses that.

## Setup (if you haven't done Jarvis setup already)
1. Install Python 3.12 from python.org (check "Add to PATH")
2. Install Ollama from ollama.com/download
3. `ollama pull qwen2.5:3b` (skip if already pulled for Jarvis)

## Running it
Double-click `run_skytrail.bat` — it handles venv creation, dependency install,
and Ollama check automatically, every time. Or from a terminal:
```
run_skytrail.bat
```

## Using the app
1. Enter name, birth date (DD-MM-YYYY), birth time (24hr HH:MM)
2. Enter latitude/longitude/timezone offset, or pick a preset city
3. Choose Vedic or Western at the top
4. Choose EN or हिं for language
5. Click Generate — the wheel populates instantly, the AI reading takes a
   few seconds (same local model speed as Jarvis)

## Two AI reading sources, switchable
- **AI: LOCAL** — Ollama + qwen2.5:3b, offline, free forever
- **AI: NEMOTRON** — NVIDIA's free cloud API, needs internet, sharper readings

Toggle with the buttons in the top header, next to the language toggle.

### One-time Nemotron setup (optional)
1. Get a free key at **build.nvidia.com** (no card needed)
2. Rename `.env.example` to `.env` in the `skytrail-desktop` folder
3. Paste your key in, replacing `nvapi-your-key-here`
4. If you already set this up for Jarvis, you can reuse the same key — just
   copy your Jarvis `.env` file into this folder too

**Never share your API key in chat — it stays local to your PC.**

## Notes on accuracy
- Uses pyswisseph's built-in Moshier calculation model — no need to download
  ephemeris data files, works fully offline out of the box, accurate to a
  fraction of a degree for personal chart reading (not observatory-grade,
  but well within astrology practice standards)
- Vedic ascendant uses whole-sign houses; Western uses Placidus
- Rahu is the mean lunar node; Ketu is calculated as exactly opposite Rahu

## Project structure
```
skytrail-desktop/
├── requirements.txt
├── run_skytrail.bat
├── README.md
└── src/
    ├── main.py               # App window, form, toggles, wiring
    ├── astro_calc.py         # Chart computation (pyswisseph)
    ├── holographic_wheel.py  # Custom-painted zodiac wheel widget
    ├── horoscope_ai.py       # Local AI reading generation
    └── translations.py       # English/Hindi label dictionary
```
