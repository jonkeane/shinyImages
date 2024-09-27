import re, yaml

from typing import TypedDict
from shiny import ui

class ImageDetails(TypedDict):
    title: str
    description: str
    descriptive_tags: list[str] 
    social_media_tags: list[str] 
    composition: str
    process: str
    photographer: str        

def parse_to_card(answer: str) -> ui.TagChild:
    """
    Given an answer, which is details about an image in YAML format, returns an image card, which is
    a Shiny UI element (which is essentially HTML).

    This function can handle the answer in its partial forms as it streams in.
    """
    txt = re.sub(r"^```.*", "", answer, flags=re.MULTILINE)

    image_details: ImageDetails | None = None
    try:
        image_details = yaml.safe_load(txt.replace("#", ""))
    except yaml.YAMLError:
        # If unable to parse the YAML, do a req(False, cancel_output=True), which throws
        # a SilentException; if an output function raises this exception, Shiny will
        # leave the output unchanged from its previous state.
        # req(False, cancel_output=True)
        raise ValueError

    if image_details is None:
        raise ValueError
    if not isinstance(image_details, dict):
        # Sometimes at the very beginning the YAML parser will return a string, but to
        # create a card, we need a dictionary.
        raise ValueError

    return update_card(image_details)

def update_card(image_details: ImageDetails) -> ui.TagChild:
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

    details = ui.tags.ul({"class": "ps-0"})

    if "description" in image_details and image_details["description"] is not None:
        desc_list = []
        for line in image_details["description"].split("\n"):
            desc_list.append(ui.tags.p(line))

        details.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Description: "),
                *desc_list,
            )
        )

    if "composition" in image_details:
        details.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Composition: "),
                ui.tags.p(image_details["composition"]),
            )
        )

    if "location" in image_details:
        details.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Location: "),
                ui.tags.p(image_details["location"]),
            )
        )

    if "photographer" in image_details:
        details.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Photographer: "),
                ui.tags.p(image_details["photographer"]),
            )
        )

    if "process" in image_details:
        details.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Process: "),
                ui.tags.p(image_details["process"]),
            )
        )

    return ui.card(
        title,
        tags,
        details,
        style = "grid-row-start: 1; grid-column-start: 1;"
    )