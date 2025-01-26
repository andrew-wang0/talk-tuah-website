import asyncio
import json
import logging
import os
import yaml

from dotenv import load_dotenv
from livekit.agents import (
    AutoSubscribe,
    JobContext,
    JobProcess,
    WorkerOptions,
    cli,
    llm,
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero
from selenium.webdriver.common.by import By

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

import aiohttp
from typing import Annotated, AsyncIterable

from livekit.agents.multimodal import MultimodalAgent

from browser.controller import BrowserController

PAGE: str = "larc.uci.edu"
bc = BrowserController()

prompts_path = os.path.join(os.path.dirname(__file__), "prompts.yml")
with open(prompts_path, "r") as file:
    prompts = yaml.safe_load(file)

def scroll_to(assistant: VoicePipelineAgent, text: str | AsyncIterable[str]):
    global bc
    
    print("[[SCROLL_TO]] ATTEMPTING SCROLL")

    try:
        xpath = f"//*[contains(text(), '{text}')]"
        bc.scroll_to(by=By.XPATH, value=xpath)
    except Exception as e:
        print("[[SCROLL_TO]] ERROR:", e)
    finally:
        return text
    
class AssistantFnc(llm.FunctionContext):
    global bc
    
    def __init__(self):
        super().__init__()

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
                    bc.get(page)
                    # toc = await bc.generate_table_of_contents()
                    # mainContent = await bc.generate_contents()
                    
                    global PAGE
                    PAGE = page

                    logger.info("Successfully generated TOC and main content.")
                    return("CONFIRM TO THE USER THAT YOU ARE DONE.")
                    # return f"The TOC: {toc} \n Complete Content: {mainContent}."
                else:
                    logger.error(f"Failed to get data, status code: {response.status}")
                    raise Exception(f"Failed to get data, status code: {response.status}")

    @llm.ai_callable()
    async def get_toc(
        self,
    ):
        """
        """
        logger.info(f"getting TOC")
        
        global PAGE
        if not PAGE:
            return "Page not set. What page do you want to navigate to?"

        try:            
            toc = bc.get_table_of_contents()

            return f"The TOC is {toc}."
        except:
            logger.error(f"Error fetching TOC")
            raise Exception(f"An error occurred while fetching the TOC.")
    
    get_toc.__doc__ = prompts["TABLE_OF_CONTENTS"]
                
    @llm.ai_callable()
    async def get_contents(
        self,
    ):
        """Called when the user asks about the main contents of a website. This function will return the contents for the given website."""
        logger.info(f"getting page contents")
        
        global PAGE
        if not PAGE:
            return "Page not set. What page do you want to navigate to?"

        try:            
            contents = bc.get_contents()
            
            return f"Page contents: {contents}."
        except:
            logger.error(f"Error fetching contents")
            raise Exception(f"An error occurred while fetching the contents.")
        

fnc_ctx = AssistantFnc()

def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()

async def entrypoint(ctx: JobContext):
    initial_ctx = llm.ChatContext().append(
        role="system",
        text=(prompts["SYSTEM"]),
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
        # before_tts_cb=scroll_to,
    )

    agent.start(ctx.room, participant)
    
    @ctx.room.on("data_received")
    def handle_chat(data_packet):
        data_bytes = data_packet.data 
        data_str = data_bytes.decode('utf-8') 
        data_dict = json.loads(data_str)

        msg = data_dict.get("message", "No message found")

        agent.interrupt()
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
