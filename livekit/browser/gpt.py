from typing import Optional, Callable
import yaml
from dotenv import load_dotenv
from openai import AsyncOpenAI
import os

load_dotenv(".env.local")


class LLM:
    def __init__(self, model: str = "gpt-4o", send_message: Callable | None = None):
        self.model: str = model
        self.client: AsyncOpenAI = AsyncOpenAI()
        self.send_message = send_message

        prompts_path = os.path.join(os.path.dirname(__file__), "prompts.yml")
        with open(prompts_path, "r") as file:
            self.prompts = yaml.safe_load(file)

    async def table_of_contents(self, html: str, image: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self.prompts["MASTER_SYSTEM"]
            },
            {
                "role": "system",
                "content": self.prompts["TABLE_OF_CONTENTS"]
            },
            {
                "role": "user",
                "content": [
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
            }
        ]

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        response = completion.choices[0].message.content

        return response

    async def contents(self, html: str, toc: str, image: str) -> str:
        messages = [
            {
                "role": "system",
                "content": self.prompts["MASTER_SYSTEM"]
            },
            {
                "role": "system",
                "content": self.prompts["CONTENTS"]
            },
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": html
                    },
                    {
                        "type": "text",
                        "text": toc
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpg;base64,{image}",
                            "detail": "low"
                        }
                    }
                ]
            }
        ]

        completion = await self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )

        response = completion.choices[0].message.content

        return response
