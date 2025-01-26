import asyncio
import json
import logging

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

import aiohttp
from typing import Annotated

from livekit.agents import llm
from livekit.agents.multimodal import MultimodalAgent

from browser.controller import BrowserController

# first define a class that inherits from llm.FunctionContext
class AssistantFnc(llm.FunctionContext):
    def __init__(self):
        super().__init__()
        self.bc = None

    @llm.ai_callable()
    async def navigate_url(
        self,
        page: Annotated[
            str, llm.TypeInfo(description="Navigating to the URL and generating Table Of Contents and complete mark-down contents")
        ],
    ):
        """Called when the user sends a link."""
        logger.info(f"generating info for {page}")

        async with aiohttp.ClientSession() as session:
            async with session.get(page) as response:
                if response.status == 200:

                    if not self.bc:
                        self.bc = BrowserController()

                    self.bc.get(page)
                    # toc = await self.bc.generate_table_of_contents()
                    # mainContent = await self.bc.generate_contents()

                    logger.info("Successfully generated TOC and main content.")
                    # return f"The TOC: {toc} \n Complete Content: {mainContent}."
                else:
                    logger.error(f"Failed to get data, status code: {response.status}")
                    raise Exception(f"Failed to get data, status code: {response.status}")

    @llm.ai_callable()
    async def get_toc(
        self,
        website_url: Annotated[
            str, llm.TypeInfo(description="URL of the website to get the Table of Contents")
        ],
    ):
        """
        Called when the user asks about the table of contents of a website. This function will return the table of content for the given website.
        Read only the top-level headings. Do not read addition sub-headings unless requested.
        DO NOT READ ADDITIONAL SUB BULLETS. ONLY READ HIGH LEVEL H1 (#), H2 (##) TAGS.
        """
        logger.info(f"getting TOC for {website_url}")

        if not website_url.startswith(("http://", "https://")):
            website_url = "http://" + website_url
            logger.debug(f"Updated website URL to: {website_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(website_url) as response:
                if response.status == 200:
                    if not self.bc:
                        self.bc = BrowserController()
                    
                    toc = self.bc.get_table_of_contents()

                    return f"The TOC of this {website_url} is {toc}."
                else:
                    logger.error(f"Error fetching TOC for {website_url}: {response}")
                    raise Exception(f"An error occurred while fetching the TOC for {website_url}.")
                
    @llm.ai_callable()
    async def get_contents(
        self,
        content_url: Annotated[
            str, llm.TypeInfo(description="Extracting contents from the webpage")
        ],
    ):
        """Called when the user asks about the main contents of a website. This function will return the contents for the given website."""
        logger.info(f"getting TOC for {content_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(content_url) as response:
                if response.status == 200:
                    if not self.bc:
                        self.bc = BrowserController()
                    
                    contents = self.bc.get_contents()

                    return f"Main contents: {contents}."
                else:
                    logger.error(f"Error fetching contents {response}")
                    raise Exception(f"An error occurred while fetching the TOC for {content_url}.")
                
    # @llm.ai_callable()
    # async def start_reading(
    #     self,
    #     start: Annotated[
    #         str, llm.TypeInfo(description="Start reading the content of the website")
    #     ],
    # ):
    #     """Called when the user asks to read the contents."""
    #     logger.info(f"reading the content from {start}")
        

    #     async with aiohttp.ClientSession() as session:
    #         async with session.get(start) as response:
    #             if response.status == 200:
    #                 content = await response.text()
    #                 return f"Content of the website: \n{content}"
    #             else:
    #                 raise f"Failed to get the content {response.status}"

fnc_ctx = AssistantFnc()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    from livekit.agents import llm

    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(
            "You are a voice assistant created by LiveKit. Your interface with users will be voice. "
            "You should use short and concise responses, and avoiding usage of unpronouncable punctuation. "
            "You are a visual, textual, and auditory agent built to emulate a screen reader. Responses should be concise and exact to the user's request. "
            "EMULATE in your messages a screen reader. Offer helpful, extremely concise (spartan) context at the beginning of a message (e.g. 6 testimonials: 1. foobar) "
            "DO NOT TRUNCATE THE TEXT FROM THE CONTENT YOU'RE READING. STATE THEM IN FULL. ADDITIONAL CONTENT __THE AGENT__ (you) add should be concise."
        ),
    )

    logger.info(f"connecting to room {ctx.room.name}")
    await ctx.connect(auto_subscribe=AutoSubscribe.AUDIO_ONLY)

    # Wait for the first participant to connect
    participant = await ctx.wait_for_participant()
    logger.info(f"starting voice assistant for participant {participant.identity}")
    
    oai = openai.LLM(model="gpt-4o-mini")

    # This project is configured to use Deepgram STT, OpenAI LLM and TTS plugins
    # Other great providers exist like Cartesia and ElevenLabs
    # Learn more and pick the best one for your app:
    # https://docs.livekit.io/agents/plugins
    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=oai,
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
        max_nested_fnc_calls=10,
        allow_interruptions=True,
    )

    agent.start(ctx.room, participant)
    
    @ctx.room.on("data_received")
    def handle_chat(data_packet):
        data_bytes = data_packet.data 
        data_str = data_bytes.decode('utf-8') 
        data_dict = json.loads(data_str)

        msg = data_dict.get("message", "No message found")

        chat_ctx = agent.chat_ctx.copy()
        chat_ctx.append(role="user", text=msg)
        stream = oai.chat(chat_ctx=chat_ctx, fnc_ctx=fnc_ctx)
        asyncio.create_task(agent.say(stream))

    # The agent should be polite and greet the user when it joins :)
    await agent.say("Hey, how can I help you today?", allow_interruptions=True)


if __name__ == "__main__":
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
            prewarm_fnc=prewarm,
        ),
    )
