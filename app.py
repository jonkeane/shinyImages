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
    Who is the photographer of this image?

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
      This photograph is from Iceland, outside of Vik.
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

        output = []
        def update_card(chunk, output):
            output.append(chunk.content)
            # try to update the card, but don't update if there's a parsing error
            try:
                card_update = parse_to_card("".join(output))
                ui.insert_ui(card_update, "#cardwrapper", immediate = True)
                ui.remove_ui(selector = "#cardwrapper > div:not(:last-child)", immediate = True)
            except ValueError:
                pass
            return chunk.content
        stream2 = (update_card(chunk, output) async for chunk in stream)
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