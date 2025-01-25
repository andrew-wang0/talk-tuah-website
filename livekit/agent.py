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

    def __init__(self):
        super().__init__()
        self.bc = None

    # the llm.ai_callable decorator marks this function as a tool available to the LLM
    # by default, it'll use the docstring as the function's description
    @llm.ai_callable()
    async def get_toc(
        self,
        # by using the Annotated type, arg description and type are available to the LLM
        website_url: Annotated[
            str, llm.TypeInfo(description="URL of the website to get the Table of Contents")
        ],
    ):
        """Called when the user asks about the table of contents of a website. This function will return the table of content for the given website."""
        logger.info(f"getting TOC for {website_url}")

        if not website_url.startswith(("http://", "https://")):
            website_url = "http://" + website_url
            logger.debug(f"Updated website URL to: {website_url}")

        async with aiohttp.ClientSession() as session:
            async with session.get(website_url) as response:
                if response.status == 200:
                    html_content = await response.text()
                    # response from the function call is returned to the LLM
                    # as a tool response. The LLM's response will include this data

                    if not self.bc:
                        self.bc = BrowserController()
                    
                    await self.bc.get(website_url)
                    TOC = await self.bc.table_of_contents()

                    return f"The TOC of this {website_url} is {TOC}."
                else:
                    logger.error(f"Error fetching TOC for {website_url}: {e}")
                    raise Exception(f"An error occurred while fetching the TOC for {website_url}.")

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
            "You were created as a demo to showcase the capabilities of LiveKit's agents framework."
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
