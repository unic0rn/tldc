import re
import json
import requests
from ..assistant import Assistant, register
from ..constants import SYSTEM_PROMPT
from ..logger import logger

class Ollama(Assistant):
    def __init__(self, model, provider, settings, db, dirtree):
        super().__init__(model, provider, settings, db, dirtree)
        self.url = json.loads(settings)["url"]

    def _call_ollama(self, messages, tools=None):
        data = {
            "model": self.model,
            "messages": messages,
            "options": {
                "temperature": 0.15,
#                "top_p": 0.9,
                "min_p": 0.01,
#                "top_k": 40,
                "num_ctx": 32768
            },
            "stream": False
        }
        if tools:
            data["tools"] = tools
        try:
            response = requests.post(f"{self.url}/api/chat", json=data)
            response.raise_for_status()
            return response.json()
        except requests.HTTPError as e:
            if tools and response.status_code == 400:
                # Retry without tools
                data_no_tools = data.copy()
                del data_no_tools['tools']
                response = requests.post(f"{self.url}/api/chat", json=data_no_tools)
                response.raise_for_status()
                return response.json()
            else:
                raise

    def prompt(self, prompt):
        # Load history
        messages = []
        for row in self.db.get_history(self.dirtree.cwd):
            messages.append(json.loads(row['message']))
        tools = [self._format_tool(t) for t in self.tool_definitions]
        # If no history, add system prompt
        tools_str = ""
        for tool in tools:
            tools_str += f"name: {tool['function']['name']}\ndescription: {tool['function']['description']}\nparameters: {tool['function']['parameters']['properties']}\nrequired: {tool['function']['parameters'].get('required')}\n\n"
        if not messages:
            messages.append({"role": "system", "content": SYSTEM_PROMPT+"\n\nYou have access to the following programmatic tools to interact with the system:\n\n"+tools_str+"\nCRITICAL EXECUTION RULES:\n- To execute a tool, you MUST use the exact prefix [tool_call:] and suffix [:tool_call] wrapped around a valid JSON object.:\n[tool_call:]\n{\"name\": \"TOOL_NAME\", \"arguments\": {\"PARAM_NAME\": \"VALUE\"}}\n[:tool_call]\n\n- Do not write any conversational text before or after the tool block."})
        # Add user prompt
        user_msg = {"role": "user", "content": prompt}
        messages.append(user_msg)
        self.db.add_history(self.dirtree.cwd, json.dumps(user_msg))
        # Chat loop for tools
        while True:
            response_data = self._call_ollama(messages)
            message = response_data["message"]
            message_content = message.get("content", "")
            message_thinking = message.get("thinking", "")
            message_fixed = message.copy()
            if message_fixed.get("thinking") != None:
                del message_fixed["thinking"]
                message_fixed["content"] = f"<|think|>\n{message_thinking}\n<|think|>\n{message_content}"
            messages.append(message_fixed)
            self.db.add_history(self.dirtree.cwd, json.dumps(message_fixed))
            tool_match = re.search(r'\[tool_call:\](.*?)\[:tool_call\]', message["content"], re.DOTALL)
            if message_thinking != "":
                logger(message_thinking, "thinking")
            if tool_match:
                try:
                    tool_json = json.loads(tool_match.group(1).strip())
                    function_name = tool_json.get("name")
                    function_args = tool_json.get("arguments")
                    if isinstance(function_args, str):
                        function_args = json.loads(function_args)
                    request = self.request_classes[function_name](**function_args)
                    result = json.dumps(self.tools_map[function_name](self, request))
                    tool_msg = {
                        "role": "user",
                        "content": f"[tool_response:]\n{result}\n[:tool_response]"
                    }
                    messages.append(tool_msg)
                    self.db.add_history(self.dirtree.cwd, json.dumps(tool_msg))
                except json.JSONDecodeError:
                    logger(f"AI output invalid JSON schema inside the tags.", "warn")
                    error_msg = {
                        "role": "user",
                        "content": f"<tool_response>\nInvalid JSON schema inside the tags.\n</tool_response>"
                    }
                    messages.append(error_msg)
            elif message["content"] != "":
                return message["content"]

    def _format_tool(self, tool_def):
        return {
            "type": "function",
            "function": {
                "name": tool_def.function.name,
                "description": tool_def.function.description,
                "parameters": json.loads(tool_def.function.parameters)
            }
        }

register("ollama", Ollama)