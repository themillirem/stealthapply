"""Configuration defaults for StealthApply."""

# Ollama API settings
OLLAMA_BASE_URL: str = "http://localhost:11434"
OLLAMA_DEFAULT_MODEL: str = "qwen3:32b"
OLLAMA_TIMEOUT: int = 120  # seconds

# App settings
APP_TITLE: str = "StealthApply 🎯"
APP_WIDTH: int = 1000
APP_HEIGHT: int = 700

# UI Colors (dark theme)
BG_DARK: str = "#1e1e2e"
BG_PANEL: str = "#2a2a3e"
BG_CARD: str = "#313145"
FG_TEXT: str = "#cdd6f4"
FG_MUTED: str = "#6c7086"
ACCENT_BLUE: str = "#89b4fa"
ACCENT_GREEN: str = "#a6e3a1"
ACCENT_RED: str = "#f38ba8"
ACCENT_YELLOW: str = "#f9e2af"
ACCENT_MAUVE: str = "#cba6f7"

# Submission settings
SUBMISSION_DELAY_MS: int = 500  # delay between submissions (ms) to avoid rate limiting
