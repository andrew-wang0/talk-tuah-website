from typing import List, Dict, Any, Optional, cast, Callable
import yaml
from dotenv import load_dotenv
from openai import AsyncOpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletionSystemMessageParam, \
    ChatCompletionUserMessageParam, ChatCompletionAssistantMessageParam
import os

load_dotenv(".env.local")

class LLM:
    def __init__(self, model: str = "gpt-4o", send_message: Callable | None = None):
        self.model: str = model
        self.client: AsyncOpenAI = AsyncOpenAI()
        self.messages: List[ChatCompletionMessageParam] = []
        self.send_message = send_message

        prompts_path = os.path.join(os.path.dirname(__file__), "prompts.yml")
        with open(prompts_path, "r") as file:
            self.prompts = yaml.safe_load(file)

        system_message: Dict[str, Any] = {
            "role": "system",
            "content": self.prompts["MASTER_SYSTEM"]
        }

        self.messages.append(cast(ChatCompletionSystemMessageParam, system_message))

    async def table_of_contents(self, html: str, image: Optional[str] = None) -> str:
        system_message: Dict[str, Any] = {
            "role": "system",
            "content": self.prompts["TABLE_OF_CONTENTS"]
        }
        self.messages.append(cast(ChatCompletionSystemMessageParam, system_message))

        if image:
            content: List[Dict[str, Any]] = [
                {
                    "type": "text",
                    "text": html
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpg;base64,{image}",
                        "detail": "low"
                    }
                }
            ]
        else:
            content = [{
                "type": "text",
                "text": html
            }]

        user_message: Dict[str, Any] = {
            "role": "user",
            "content": content
        }
        self.messages.append(cast(ChatCompletionUserMessageParam, user_message))

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=self.messages
        )

        response = completion.choices[0].message.content

        assistant_message: Dict[str, Any] = {
            "role": "assistant",
            "content": response
        }
        self.messages.append(cast(ChatCompletionAssistantMessageParam, assistant_message))

        return response