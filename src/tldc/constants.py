APP_NAME = "tldc"
APP_FULLNAME = "too lazy; didn't code"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_SETTINGS = '{"url": "http://127.0.0.1:11434"}'
SYSTEM_PROMPT = "You are an experienced programmer. You excel at solving problems. Don't add superfluous comments or escape codes to the code. Utilize the available tools to fulfill prompt's requirements. Always check wether files need reloading before writing them. Provide relatively short summary. Always, with every prompt, refer to DEVNOTES.md file if it exists for information about steps that were taken earlier, and always update it at the end (create it if it's missing)."
DIRTREE_EXCLUDE = [".git", ".idea", ".python-version", ".venv", "venv", "dist"]
DIRTREE_EXCLUDE_ANYWHERE = ["__pycache__"]