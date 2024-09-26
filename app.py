from shiny import App, reactive, render, req, ui
from typing import TypedDict
import re, yaml

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.tools import InjectedToolArg, tool
from typing_extensions import Annotated


model = ChatOpenAI(model="gpt-4o")

class ImageDetails(TypedDict):
    description: str
    descriptive_tags: list[str] 
    social_media_tags: list[str] 
    composition: str
    process: str
    source: str


def llm_prompt(style, n_words):
    if style != "":
        description_style = f"This should be written in the style of {style}."
    else:
        description_style = ""

    image_prompt = f"""
    You are ImageAnalyzerGPT.

    You have 6 distinct tasks to complete about this image.

    {description_style} 

    Task 1: title
    A short title for this image.

    Task 1: description
    Your task is to describe images in detail. 
    Use as much detail as possible, describing the foreground, background, and subjects in the image. 
    Use as much descriptive language as possible. 
    This description should be as long as is necessary to fully describe the image use about {n_words} words in this description. 

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
            "number of words",
            value=250,
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
        ui.column(
            12,
            ui.div(
                ui.output_ui("display_image"),
            ),
            ui.div(
                ui.output_ui("chat_container"),
                style="height: 50vh; overflow-y: auto;"
            ),
        ),
        ui.column(
            12,
            ui.output_ui("info_card"),
        ),
    ),
    title = "Image Describer",
)


def parse_to_card(answer: str) -> ui.TagChild:
    """
    Given an answer, which is details about an image in YAML format, returns an image card, which is
    a Shiny UI element (which is essentially HTML).

    This function can handle the answer in its partial forms as it streams in.
    """
    # if answer is ():
    #     return image_card(ImageDetails())

    txt = re.sub(r"^```.*", "", answer, flags=re.MULTILINE)

    image_details: ImageDetails | None = None
    try:
        image_details = yaml.safe_load(txt.replace("#", ""))
    except yaml.YAMLError:
        # If unable to parse the YAML, do a req(False, cancel_output=True), which throws
        # a SilentException; if an output function raises this exception, Shiny will
        # leave the output unchanged from its previous state.
        # req(False, cancel_output=True)
        pass

    if image_details is None:
        return image_card(ImageDetails())
    if not isinstance(image_details, dict):
        # Sometimes at the very beginning the YAML parser will return a string, but to
        # create a card, we need a dictionary.
        return image_card(ImageDetails())

    return image_card(image_details)

def image_card(image_details: ImageDetails) -> ui.TagChild:
    title = None
    if "title" in image_details:
        title = ui.card_header(
            {"class": "bg-dark fw-bold fs-3"},
            image_details["title"],
        )

    tags = None
    if "descriptive_tags" in image_details and image_details["descriptive_tags"]:
        tags = ui.div({"class": "mb-3"})
        for descriptive_tags in image_details["descriptive_tags"]:
            tags.append(ui.span({"class": "badge bg-secondary"}, descriptive_tags), " ")

    if "social_media_tags" in image_details and image_details["social_media_tags"]:
        for social_media_tag in image_details["social_media_tags"]:
            tags.append(ui.span({"class": "badge bg-primary"}, social_media_tag), " ")            

    description = ui.tags.ul({"class": "ps-0"})

    if "description" in image_details and image_details["description"] is not None:
        desc_list = []
        for line in image_details["description"].split("\n"):
            desc_list.append(ui.tags.p(line))

        description.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Description: "),
                *desc_list,
            )
        )

    if "composition" in image_details:
        description.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Composition: "),
                ui.tags.p(image_details["composition"]),
            )
        )

    if "location" in image_details:
        description.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Location: "),
                ui.tags.p(image_details["location"]),
            )
        )

    if "photographer" in image_details:
        description.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Photographer: "),
                ui.tags.p(image_details["photographer"]),
            )
        )

    if "process" in image_details:
        description.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Process: "),
                ui.tags.p(image_details["process"]),
            )
        )

    return ui.card(
        title,
        tags,
        description,
    )

def server(input, output, session):
    chat = ui.Chat("chat")
    card = reactive.value(parse_to_card(""))

    @output
    @render.ui
    def display_image():
        return ui.img(src=input.url(), style="max-width: 100%; max-height: 100%;")

    @output
    @render.ui
    def info_card():
        return card()

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
            card.set(parse_to_card("".join(output)))
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
                card.set(parse_to_card("".join(output)))
                return chunk.content

            stream2 = (update_card(chunk, output) async for chunk in stream)

            await chat.append_message_stream(stream2)

    @render.ui
    @reactive.event(input.go)
    def chat_container():
        return [
            chat.ui()
        ]


app = App(app_ui, server)