# 🎯 StealthApply

**Privacy-first, AI-powered resume submission tool for SolidWorks Engineers in Minneapolis–St. Paul.**

StealthApply lets you upload your resume, select target companies from a curated list, and batch-submit applications with locally-generated, tailored cover notes — all without sending a single byte of your personal data to the cloud.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📄 Resume Upload | Supports PDF and DOCX formats |
| ✅ Company Selector | 17+ pre-loaded SolidWorks roles in the Twin Cities |
| 🤖 Local LLM | Ollama integration — cover notes generated on your machine |
| 🚀 Batch Submission | One-click submission to all selected companies |
| 🧾 Transaction Receipt | In-memory receipt with optional save-to-disk |
| 🔒 Privacy Mode | Nothing written to disk without your explicit consent |
| ⚙️ Settings Dialog | Configure Ollama URL and model at runtime |
| 🌑 Dark Theme | Catppuccin Mocha-inspired UI |

---

## 🖥️ Screenshots

> Upload your resume → Select companies → Execute → View receipt

---

## 📋 Requirements

- **Python 3.11+**
- **[Ollama](https://ollama.ai)** (optional — enables AI cover note generation)
  - Recommended model: `qwen3:32b` or any model you prefer
- macOS, Linux, or Windows (tkinter required — included with most Python installs)

---

## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/themillirem/stealthapply.git
cd stealthapply
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS/Linux
# venv\Scripts\activate         # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. (Optional) Start Ollama with a local model

```bash
# Install Ollama from https://ollama.ai, then:
ollama pull qwen3:32b
ollama serve
```

### 5. Run StealthApply

```bash
python -m stealthapply.main
# or
bash run.sh
```

---

## 🏗️ Project Structure

```
stealthapply/
├── stealthapply/
│   ├── __init__.py       # Package metadata
│   ├── main.py           # Entry point — launches the GUI
│   ├── gui.py            # Full tkinter GUI (dark theme, all panels)
│   ├── config.py         # App-wide constants (colors, defaults, timeouts)
│   ├── job_scraper.py    # Job listings dataclass + 17 static Twin Cities roles
│   ├── resume_parser.py  # PDF/DOCX text extraction (PyPDF2, python-docx)
│   ├── llm_client.py     # Ollama API client for cover note generation
│   └── submitter.py      # Batch submission logic + SubmissionReceipt
├── requirements.txt
├── setup.py
├── run.sh
├── .gitignore
└── README.md
```

---

## 🏢 Pre-loaded Companies

All roles are SolidWorks mechanical engineering positions in the Minneapolis–St. Paul metro:

| Company | Role | Location |
|---|---|---|
| Medtronic | Mechanical Design Engineer | Fridley, MN |
| Boston Scientific | Product Development Engineer | Maple Grove, MN |
| Graco Inc. | Senior Mechanical Engineer | Minneapolis, MN |
| The Toro Company | Design Engineer | Bloomington, MN |
| Polaris Industries | Mechanical Engineer | Medina, MN |
| 3M | R&D Engineer | Maplewood, MN |
| Eaton Corporation | Product Design Engineer | Eden Prairie, MN |
| Donaldson Company | Mechanical Design Engineer | Minneapolis, MN |
| Watlow Electric | Application Engineer | Winona, MN |
| Innovex | Senior Design Engineer | Bloomington, MN |
| Textron Arctic Cat | Product Engineer | Thief River Falls, MN |
| Taylor Made Solutions | Mechanical Engineer | Burnsville, MN |
| IDEX Corporation | Design Engineer | Bloomington, MN |
| Roper Technologies | Mechanical Design Engineer | Minneapolis, MN |
| Colder Products Company | Application Engineer | St. Paul, MN |
| Strattec Security | Mechanical Engineer | Plymouth, MN |
| API Technologies | Mechanical Design Engineer | Eden Prairie, MN |

---

## 🤖 Local LLM Integration

StealthApply uses [Ollama](https://ollama.ai) to run a language model **entirely on your machine**. No API keys. No cloud. No data leaves your computer.

**How it works:**
1. Your resume text is passed to the local model along with the job description
2. The model generates a 2–3 sentence tailored cover note for each application
3. The cover note is included in your transaction receipt
4. If Ollama is offline, the app falls back gracefully and still processes all submissions

**Supported models** (anything Ollama supports):
- `qwen3:32b` (default, recommended)
- `llama3:8b` (faster, lighter)
- `mistral:7b`
- Any model in your local Ollama library

Configure via **⚙ Settings** in the app or edit `stealthapply/config.py`.

---

## 🔒 Privacy Design

StealthApply was built with a privacy-first architecture:

- ✅ Resume text is processed **in memory only**
- ✅ LLM inference runs **locally via Ollama** — no cloud API calls
- ✅ Transaction receipts exist **in memory** until you explicitly click "Save Receipt"
- ✅ "Clear All" wipes all in-memory state immediately
- ✅ No analytics, no telemetry, no network calls except to your local Ollama instance
- ✅ Token/secret scanning compliant — no credentials hardcoded

---

## ⚙️ Configuration

Edit `stealthapply/config.py` to change defaults:

```python
OLLAMA_BASE_URL = "http://localhost:11434"   # Your Ollama server
OLLAMA_DEFAULT_MODEL = "qwen3:32b"           # Model to use
OLLAMA_TIMEOUT = 120                          # Seconds before timeout
SUBMISSION_DELAY_MS = 500                     # Delay between submissions
```

Or change at runtime via **⚙ Settings** in the app.

---

## 🛠️ Development

```bash
# Install in editable mode
pip install -e .

# Run directly
python -m stealthapply.main
```

### Adding More Companies

Edit `stealthapply/job_scraper.py` and append to `STATIC_JOBS`:

```python
JobListing(
    company="Your Company",
    title="Mechanical Engineer",
    location="Minneapolis, MN",
    url="https://yourcompany.com/careers",
    description="Brief description of the role and requirements.",
)
```

---

## 📦 Building a Standalone Executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name StealthApply stealthapply/main.py
# Output: dist/StealthApply
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) for making local LLMs dead simple
- [Catppuccin](https://github.com/catppuccin/catppuccin) for the color palette inspiration
- Every SolidWorks engineer grinding through the job search 💪
