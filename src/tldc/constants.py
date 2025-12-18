APP_NAME = "tldc"
APP_FULLNAME = "too lazy; didn't code"
DEFAULT_OLLAMA_MODEL = "llama3.2:3b"
DEFAULT_OLLAMA_SETTINGS = '{"url": "http://127.0.0.1:11434"}'
SYSTEM_PROMPT = "You are an experienced programmer. You excel at solving problems. With the exception of docstring, phpdoc and similar, avoid writing comments in the code unless absolutely necessary. Don't add escape codes to the source code unless required by the language, the files get written as is. Utilize the available tools to fulfill prompt's requirements. Always check wether files need reloading before writing them. Provide relatively short summary."
DIRTREE_EXCLUDE = [".git", ".idea", ".python-version", ".venv", "venv", "dist"]
DIRTREE_EXCLUDE_ANYWHERE = ["__pycache__"]