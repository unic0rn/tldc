APP_NAME = "tldc"
APP_FULLNAME = "too lazy; didn't code"
DEFAULT_OLLAMA_MODEL = "qwen3.5:9b-nvfp4"
DEFAULT_OLLAMA_SETTINGS = '{"url": "http://127.0.0.1:11434"}'
SYSTEM_PROMPT = "Utilize the available tools to fulfill prompt's requirements. Provide relatively short summary. Refer to DEVNOTES.md file if it exists for information about steps that were taken earlier, and update it at the end (create it if it's missing). Do not assume, verify."
DIRTREE_EXCLUDE = [".git", ".idea", ".python-version", ".venv", "venv", "dist"]
DIRTREE_EXCLUDE_ANYWHERE = ["__pycache__"]