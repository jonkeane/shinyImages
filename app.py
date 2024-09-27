import time

from shiny import App, reactive, render, ui
from langchain_openai import ChatOpenAI
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import InjectedToolArg, tool
from typing_extensions import Annotated

from card import parse_to_card

model = ChatOpenAI(model="gpt-4o")

@tool(parse_docstring=True)
def exiftool(url: Annotated[str, InjectedToolArg]) -> str:
    """extract exif data

    Args:
        url: url of the image.
    """
    return """
ExifTool Version Number         : 12.97
File Name                       : 50302524873_18a99d6974_b.jpg
Directory                       : /Users/jkeane/Downloads
File Size                       : 143 kB
File Modification Date/Time     : 2024:09:25 07:58:16-05:00
File Access Date/Time           : 2024:09:25 20:53:40-05:00
File Inode Change Date/Time     : 2024:09:25 07:58:16-05:00
File Permissions                : -rw-r--r--
File Type                       : JPEG
File Type Extension             : jpg
MIME Type                       : image/jpeg
Exif Byte Order                 : Big-endian (Motorola, MM)
Artist                          : Jonathan Keane
Copyright                       : All rights reserved
Current IPTC Digest             : d000166aa26947dcc219dc361815c38b
Coded Character Set             : UTF8
Envelope Record Version         : 4
Document Notes                  : https://flickr.com/e/bcl5xB5UvnfuXZGu8ZhTmJaTAGmnvAiSpOPHG54L6us%3D, Email:jkeane@gmail.com, URL:jonkeane.com
Copyright Notice                : All rights reserved
By-line                         : Jonathan Keane
Application Record Version      : 4
JFIF Version                    : 1.02
Resolution Unit                 : None
X Resolution                    : 1
Y Resolution                    : 1
Profile CMM Type                : Linotronic
Profile Version                 : 2.1.0
Profile Class                   : Display Device Profile
Color Space Data                : RGB
Profile Connection Space        : XYZ
Profile Date Time               : 1998:02:09 06:49:00
Profile File Signature          : acsp
Primary Platform                : Microsoft Corporation
CMM Flags                       : Not Embedded, Independent
Device Manufacturer             : Hewlett-Packard
Device Model                    : sRGB
Device Attributes               : Reflective, Glossy, Positive, Color
Rendering Intent                : Perceptual
Connection Space Illuminant     : 0.9642 1 0.82491
Profile Creator                 : Hewlett-Packard
Profile ID                      : 0
Profile Copyright               : Copyright (c) 1998 Hewlett-Packard Company
Profile Description             : sRGB IEC61966-2.1
Media White Point               : 0.95045 1 1.08905
Media Black Point               : 0 0 0
Red Matrix Column               : 0.43607 0.22249 0.01392
Green Matrix Column             : 0.38515 0.71687 0.09708
Blue Matrix Column              : 0.14307 0.06061 0.7141
Device Mfg Desc                 : IEC http://www.iec.ch
Device Model Desc               : IEC 61966-2.1 Default RGB colour space - sRGB
Viewing Cond Desc               : Reference Viewing Condition in IEC61966-2.1
Viewing Cond Illuminant         : 19.6445 20.3718 16.8089
Viewing Cond Surround           : 3.92889 4.07439 3.36179
Viewing Cond Illuminant Type    : D50
Luminance                       : 76.03647 80 87.12462
Measurement Observer            : CIE 1931
Measurement Backing             : 0 0 0
Measurement Geometry            : Unknown
Measurement Flare               : 0.999%
Measurement Illuminant          : D65
Technology                      : Cathode Ray Tube Display
Red Tone Reproduction Curve     : (Binary data 2060 bytes, use -b option to extract)
Green Tone Reproduction Curve   : (Binary data 2060 bytes, use -b option to extract)
Blue Tone Reproduction Curve    : (Binary data 2060 bytes, use -b option to extract)
DCT Encode Version              : 100
APP14 Flags 0                   : [14], Encoded with Blend=1 downsampling
APP14 Flags 1                   : (none)
Color Transform                 : YCbCr
Image Width                     : 1024
Image Height                    : 683
Encoding Process                : Baseline DCT, Huffman coding
Bits Per Sample                 : 8
Color Components                : 3
Y Cb Cr Sub Sampling            : YCbCr4:4:4 (1 1)
Image Size                      : 1024x683
Megapixels                      : 0.699
"""

model = model.bind_tools([exiftool])

def llm_prompt(style, n_words):
    if style != "":
        description_style = f"IMPORTANT: This whole response should be written in the style of {style}."
    else:
        description_style = ""

    image_prompt = f"""
    You are ImageAnalyzerGPT. {description_style} 

    You have a number of distinct tasks to complete about this image.

    Task 1: title
    A short title for this image.

    Task 1: description
    Your task is to describe images in detail. 
    Use as much detail as possible, describing the foreground, background, and subjects in the image. 
    Use as much descriptive language as possible. 
    This description should be as long as is necessary to fully describe the image.
    This description must be about {n_words * 1.5} tokens long. 

    Task 1: descriptive tags
    Your task is to tag images in detail. Use as many tags as possible and make the tags descriptive. Additionally add in fun conceptual tags for social media.

    Task 1: social media tags
    Your task is to add fun conceptual tags about this image for social media.

    Task 1: composition
    Your task is to comment on the photographic composition

    Task 1: location
    Try to determine the location. Include an estimation of your confidence.

    Task 1: process
    Comment on if this is a digital photo or a analog film photo. 

    Task 1: photographer
    Who is the photographer of this image? You can use the Artist metadata from the tool exiftool to get this information. 

    The YAML should be structured like this:

    ```
    title: Fancy Title
    description: |
      This image has a cat sitting on a chair. 
      
      In the foreground there are balls of yarn and in the background many books.
    descriptive_tags:
      - lighthouse
      - tall structure
      - white building
      - foggy morning
      - mist
      - stone edifice
      - windows
      - crimson dome
      - iron lattice
      - beacon
      - sentinel
      - grassy field
      - wildflowers
      - dew
      - solitude
      - vigilance
    social_media_tags:
      - LighthouseLife
      - FoggyMornings
      - BeaconOfHope
      - SolitudeInNature
      - MistyMystery
      - GuidingLight
      - SereneScenes
    composition: |
      The cat is off to one side. The leading lines of the chair's 
      legs draw attention to the cat
    location: |
      This photograph is from Tibet. I am pretty sure about that.
    photographer: Dorothea Lange
    process: |
      This image appears to be a digital photograph. These are some of the reasons why: ...
    ```

    IMPORTANT: Return the result as YAML in a Markdown code block surrounded with three backticks!
    """

    prompt = ChatPromptTemplate.from_messages(
    [
        SystemMessage(image_prompt),
        MessagesPlaceholder(variable_name="messages"),
    ]
    )
    return prompt


app_ui = ui.page_sidebar(
    ui.sidebar(
        ui.input_text(
            "url",
            "Image URL",
            value="https://live.staticflickr.com/65535/52378413572_14860a5ba1_b.jpg",
        ),
        ui.input_text(
            "style",
            "In the style of",
            value="",
        ),
        ui.input_numeric(
            "n_words",
            "description word limit",
            value=100,
        ),
        ui.input_action_button("go", "Start"),
        ui.tags.script("""
        $(document).ready(function() {
            $(document).on('keypress', function(e) {
                if (e.which == 13) {  // 13 is the Enter key
                    $('#go').click();
                }
            });
        });
        """)
    ),
    ui.layout_columns(
        ui.div(
            ui.output_ui(
                "display_image",
                style="height: 55vh; display: flex; justify-content: center; align-items: center; overflow: hidden;"),
            ui.div(
                ui.output_ui("chat_container"),
                style="height: 34vh; overflow-y: auto; display: flex; flex-direction: column-reverse;"
            ),
            style="display: flex; flex-direction: column; height: 90vh; justify-content: space-between;"
        ),
        ui.div(id = "cardwrapper", style = "display: grid; grid-template-columns: 1fr;"),
        col_widths={"sm": (12), "lg": (6)},
    ),
    title = "Image Describer",
)

def server(input, output, session):
    chat = ui.Chat("chat")

    @output
    @render.ui
    def display_image():
        return ui.img(src=input.url(), style="height: 55vh;")

    @reactive.effect
    @reactive.event(input.go)
    async def start_chat():
        prompt = llm_prompt(input.style(), input.n_words())

        # Start a new conversation
        history = InMemoryChatMessageHistory()
        client = RunnableWithMessageHistory(prompt | model, lambda: history)

        user_prompt = HumanMessage(
            content=[
                {
                    "type": "text",
                    "text": "Describe this image",
                },
                {"type": "image_url", "image_url": {"url": input.url()}},
            ]
        )

        stream = client.astream(user_prompt)

        def call_tool(tool_call):
            print(tool_call)
            tool_call["args"]["url"] = input.url()
            selected_tool = {"exiftool": exiftool}[tool_call["name"].lower()]
            tool_output = selected_tool.invoke(tool_call["args"])
            print(tool_output)
            stream = client.astream(ToolMessage(tool_output, tool_call_id=tool_call["id"]))
            await_stream(stream)
            chat.append_message_stream(stream)

        output = []
        gathered_tools = None
        def update_card(chunk, output, gathered_tools):
            if gathered_tools is None:
                gathered_tools = chunk
            else:
                gathered_tools = gathered_tools + chunk
            if "finish_reason" in chunk.response_metadata and chunk.response_metadata["finish_reason"] == "tool_calls":
                if gathered_tools is not None:
                    print("gathered tools is not none")
                    print(gathered_tools)
                    for tool_call in gathered_tools.tool_calls:
                        call_tool(tool_call)
            output.append(chunk.content)
            # try to update the card, but don't update if there's a parsing error
            try:
                card_update = parse_to_card("".join(output))
                ui.insert_ui(card_update, "#cardwrapper", immediate = True)
                ui.remove_ui(selector = "#cardwrapper > div:not(:last-child)", immediate = True)
            except ValueError:
                pass
            return chunk.content

        stream2 = (update_card(chunk, output, gathered_tools) async for chunk in stream)

        await chat.append_message_stream(stream2)

        # Allow the user to ask follow up questions
        @chat.on_user_submit
        async def _():
            user_message = HumanMessage(content=chat.user_input())
            stream = client.astream(user_message)

            output = []
            def update_card(chunk, output):
                output.append(chunk.content)
                # try to update the card, but don't update if there's a parsing error
                try:
                    card_update = parse_to_card("".join(output))
                    ui.insert_ui(card_update, "#card", immediate = True)
                    ui.remove_ui(selector = "#card > div:not(:last-child)", immediate = True)
                except ValueError:
                    pass
                return chunk.content
            stream2 = (update_card(chunk, output) async for chunk in stream)
            await chat.append_message_stream(stream2)
            
    @output
    @render.ui
    @reactive.event(input.go)
    def chat_container():
        return [
            chat.ui()
        ]


app = App(app_ui, server)