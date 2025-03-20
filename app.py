from pathlib import Path

from shiny import App, reactive, render, ui
from chatlas import ChatOpenAI, content_image_url

import image_details
from prompt import llm_prompt
from offcanvas import offcanvas_ui
import icons

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
            placeholder="e.g., Hemingway, Jane Austen, etc.",
        ),
        ui.input_numeric(
            "n_words",
            "Description word limit",
            value=100,
        ),
        ui.input_action_button(
            "describe",
            "Describe Image",
            class_="btn btn-primary",
            icon=icons.pencil_square,
        ),
    ),
    offcanvas_ui(
        "chat_offcanvas",
        "Refine image description",
        ui.output_ui("chat_container"),
    ),
    ui.layout_columns(
        ui.output_ui("image_container"),
        ui.output_ui("card_container", fill=True, fillable=True),
        col_widths={"sm": (12), "lg": (6)},
    ),
    ui.tags.link(rel="stylesheet", href="style.css"),
    ui.tags.script(src="keypress.js"),
    fillable=True,
    title="AI Assisted Image Describer",
)


def server(input, output, session):
    chat = ui.Chat("chat")
    chat_client = ChatOpenAI(model="gpt-4o")

    card_title = ui.MarkdownStream("card_title")
    card_body = ui.MarkdownStream("card_body")

    @reactive.effect
    def _():
        chat_client.system_prompt = llm_prompt(input.style(), input.n_words())

    @render.ui
    def image_container():
        return ui.img(src=input.url())
    
    @render.ui
    def card_container():
        if input.describe() == 0:
            return ui.card(
                {"class": "text-muted"},
                "No description yet (press 'Enter')"
            )
        else:
            return ui.card(
                ui.card_header(
                    {"class": "bg-dark fw-bold fs-3"},
                    ui.output_markdown_stream("card_title")
                ),
                ui.output_markdown_stream("card_body", auto_scroll=False),
            )

    # As .append_message_stream() is iterating through the generator, accumulate contents
    # so we can parse it, extract the image details, and update the card title and body.
    async def stream_wrapper(stream):
        all_content: str = ""
        async with card_body.stream_context() as body:
            async with card_title.stream_context() as title:
                async for chunk in stream:
                    all_content += chunk
                    details = image_details.extract(all_content)
                    await title.replace(details.get("title"))
                    await body.replace(image_details.card_body_ui(details))
                    yield chunk

    # Start/update description
    @reactive.effect
    @reactive.event(input.describe)
    async def _():
        stream = await chat_client.stream_async(
            "Describe this image",
            content_image_url(input.url())
        )
        await chat.append_message_stream(stream_wrapper(stream))

    # Allow the user to ask follow up questions
    @chat.on_user_submit
    async def _(user_input: str):
        stream = await chat_client.stream_async(user_input)
        await chat.append_message_stream(stream_wrapper(stream))

    @render.ui
    def chat_container():
        if input.describe() == 0:
            return "A chat will appear here once there is a description"
        else:
            return ui.chat_ui("chat", messages=["**Hi!** Tell me how I can help refine the description.\n\n"])

 
app = App(app_ui, server, static_assets=Path(__file__).parent / "www")
