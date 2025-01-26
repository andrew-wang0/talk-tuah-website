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
    tokenize
)
from livekit.agents.pipeline import VoicePipelineAgent
from livekit.plugins import openai, deepgram, silero
from selenium.webdriver.common.by import By

load_dotenv(dotenv_path=".env.local")
logger = logging.getLogger("voice-agent")

import aiohttp
from typing import Annotated, AsyncIterable, Union

from livekit.agents.multimodal import MultimodalAgent

from browser.controller import BrowserController

PAGE: str = "larc.uci.edu"
bc = BrowserController()

prompts_path = os.path.join(os.path.dirname(__file__), "prompts.yml")
with open(prompts_path, "r") as file:
    prompts = yaml.safe_load(file)

# async def scroll_to(assistant: VoicePipelineAgent, text: str | AsyncIterable[str]):
#     global bc
#
#     substring = "[[CONTENT]]"
#
#     print("[[SCROLL_TO]] ATTEMPTING SCROLL")
#
#     print("[[SCROLL_TO]] TEXT TYPE", type(text))
#
#     try:
#         if isinstance(text, AsyncIterable):
#             # Gather the async generator into a single string
#             text = ''.join([chunk async for chunk in text])
#         else:
#             raise TypeError("Unsupported text type; expected str or AsyncIterable[str]")
#
#         print("[[SCROLL_TO]] TEXT", text)
#         # Find the substring and generate the XPath
#         index = text.find(substring) + len(substring) + 2  # Account for substring length, empty string, and start quote: ' "'
#         search = text[index:index+20]
#         print("[[SCROLL_TO]] SEARCH", search)
#         xpath = f"//*[contains(normalize-space(text()), '{search}')]"
#
#         print("[[SCROLL_TO]] SCROLLING TO", xpath)
#
#         # Scroll to the element using XPath
#         bc.scroll_to(by=By.XPATH, value=xpath)
#     except Exception as e:
#         print("[[SCROLL_TO]] ERROR:", e)
#     finally:
#         return text
import asyncio
import logging
from typing import AsyncIterable, Union
from selenium.webdriver.common.by import By

logger = logging.getLogger("voice-agent")


async def scroll_to(assistant, text: Union[str, AsyncIterable[str]]):
    """
    A before_tts_cb that:
      1. If `text` is a string, immediately does substring logic.
      2. If `text` is an async generator, handles multiple calls:
         - If it produces 0 chunks, we skip scrolling (often the first call).
         - Otherwise, we wait for a few chunks, do substring logic,
           then re-yield them all for TTS to speak.
    """
    global bc

    substring = "[[CONTENT]]"

    print("[[SCROLL_TO]] ATTEMPTING SCROLL")
    print("[[SCROLL_TO]] TEXT TYPE", type(text))

    # ----- Case 1: Already a plain string -----
    if isinstance(text, str):
        print("[[SCROLL_TO]] Received a string of length:", len(text))
        try:
            index = text.find(substring)
            if index != -1:
                index += len(substring) + 2
                search = text[index: index + 20]
                xpath = f"//*[contains(normalize-space(text()), '{search}')]"
                print("[[SCROLL_TO]] SCROLLING TO:", xpath)
                bc.scroll_to(by=By.XPATH, value=xpath)
            else:
                print("[[SCROLL_TO]] Substring not found.")
        except Exception as e:
            print("[[SCROLL_TO]] ERROR (string mode):", e)
        finally:
            return text  # Return original string for TTS

    # ----- Case 2: text is an async generator -----
    if isinstance(text, AsyncIterable):
        consumed_chunks = []
        chunk_counter = 0
        scroll_done = False

        async def wrapped_generator():
            nonlocal consumed_chunks, chunk_counter, scroll_done

            async for chunk in text:
                if scroll_done:
                    pass
                # Record that we got a chunk (even if it's empty string).
                chunk_counter += 1
                print(f"[[SCROLL_TO]] Got chunk #{chunk_counter}: {repr(chunk)}")

                # Accumulate chunk
                consumed_chunks.append(chunk)

                # Build partial text so far
                partial_text = "".join(consumed_chunks)
                print("[[SCROLL_TO]] partial_text so far:", partial_text)

                # After a few chunks, try to scroll once
                if not scroll_done:
                    try:
                        index = partial_text.find(substring)
                        if index != -1 and len(partial_text[index:]) > 20:
                            index += len(substring) + 2
                            search = partial_text[index: index + 20]
                            xpath = f"//*[contains(normalize-space(text()), '{search}')]"
                            print("[[SCROLL_TO]] SCROLLING TO:", xpath)
                            bc.scroll_to(by=By.XPATH, value=xpath)
                            scroll_done = True

                        else:
                            print("[[SCROLL_TO]] Substring not found in partial text.")
                    except Exception as e:
                        print("[[SCROLL_TO]] ERROR (generator partial):", e)

                # Yield each chunk so TTS can speak it in real time
                yield chunk

        return wrapped_generator()

    # If here, we got an unexpected type
    raise TypeError("Unsupported text type; expected str or AsyncIterable[str]")
    
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
                    # mainContent = await bc.generate_cosntents()
                    
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
    # agent = VoicePipelineAgent(
    #     vad=ctx.proc.userdata["vad"],
    #     stt=google.STT(),
    #     llm=google.LLM(),
    #     tts=google.TTS(),
    #     chat_ctx=initial_ctx,
    #     fnc_ctx=fnc_ctx,
    #     max_nested_fnc_calls=10,
    #     allow_interruptions=True,
    #     before_tts_cb=scroll_to,
    # )

    agent = VoicePipelineAgent(
        vad=ctx.proc.userdata["vad"],
        stt=deepgram.STT(),
        llm=oai,
        tts=openai.TTS(),
        chat_ctx=initial_ctx,
        fnc_ctx=fnc_ctx,
        max_nested_fnc_calls=10,
        allow_interruptions=True,
        before_tts_cb=scroll_to,
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