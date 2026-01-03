# VIGIL - 

██╗ ██╗██╗ ██████╗ ██╗██╗
██║ ██║██║██╔════╝ ██║██║
██║ ██║██║██║ ███╗██║██║
╚██╗ ██╔╝██║██║ ██║██║██║
╚████╔╝ ██║╚██████╔╝██║███████
╚═══╝ ╚═╝ ╚═════╝ ╚═╝╚══════╝

**A voice-first AI companion that never sleeps.**

Vigil is an always-listening, always-learning AI companion built on the principles of the Book of Light Pillars and the Ascension Codex. It serves as teacher, mentor, partner, friend, project manager, accomplice, protector, and creator.

---

## 🌟 Features

- **🎤 Always-Listening Voice Interface** - Say "Vigil" or other wake words to activate
- **🧠 Multi-LLM Brain** - GPT-4o (primary), Claude, and Gemini via Poe
- **🔊 Natural Voice Output** - Premium ElevenLabs voice with Windows TTS fallback
- **🌙 Daily Midnight Reflections** - Vigil reflects on what it learned at 12:00:01 AM
- **📚 Custom Knowledge Base** - Ascension Codex, Shrine Virtues, and user-extensible knowledge
- **💾 Memory & Learning** - Remembers conversations and learns about you over time
- **🛡️ 12 Ethical Guardrails** - Based on the Shrine Virtues from the Book of Light

---

## 📋 Requirements

- **Windows 10/11** (macOS/Linux support planned)
- **Python 3.10+**
- **Microphone** (for voice input)
- **Speakers** (for voice output)

### API Keys Required

| Service | Purpose | Get Key |
|---------|---------|---------|
| OpenAI | GPT-4o + Whisper | https://platform.openai.com |
| Anthropic | Claude | https://console.anthropic.com |
| ElevenLabs | Premium Voice | https://elevenlabs.io |
| Poe (Optional) | Gemini Access | https://poe.com/developers |

---

## 🚀 Installation

### Step 1: Clone the Repository

Step 2: Create Virtual Environment
bash

python -m venv venv
venv\Scripts\activate  # Windows
# or
source venv/bin/activate  # macOS/Linux

Step 3: Install Dependencies
bash

pip install -r requirements.txt

Note: If pyaudio fails to install on Windows:
bash

pip install pipwin
pipwin install pyaudio

Step 4: Configure API Keys
bash

copy config\.env.example config\.env

Edit config\.env with your API keys:
env

OPENAI_API_KEY=sk-your-openai-key-here
ANTHROPIC_API_KEY=sk-ant-your-anthropic-key-here
POE_API_KEY=your-poe-api-key-here
ELEVENLABS_API_KEY=your-elevenlabs-key-here

Step 5: Run Vigil

Option A: Using the batch file (recommended)
bash

start_vigil.bat

Option B: Direct Python
bash

python vigil.py





```bash
git clone https://github.com/bizyboy/vigil.git
cd vigil
