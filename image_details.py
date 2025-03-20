import re
import yaml

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


def extract(answer: str) -> ImageDetails:
    """
    Given an the LLM response, extract details about an image in YAML format.

    This function can handle the answer in its partial forms as it streams in.
    """
    txt = re.sub(r"^```.*", "", answer, flags=re.MULTILINE)

    image_details: ImageDetails | None = None
    try:
        image_details = yaml.safe_load(txt.replace("#", ""))
    except yaml.YAMLError:
        pass
    
    if isinstance(image_details, dict):
        return image_details
    else:
        return {}


def card_body_ui(x: ImageDetails):
    "Image details UI for the card *body*."

    result = ui.TagList()

    descriptive_tags = x.get("descriptive_tags") or []
    social_media_tags = x.get("social_media_tags") or []
    tags = descriptive_tags + social_media_tags
    if tags:
        tags_ui = ui.div(
            {"class": "mb-3"},
            *(
                ui.TagList(ui.span({"class": "badge bg-secondary"}, i), " ")
                for i in tags
            )
        )
        result.append(tags_ui)

    result.append(ui.tags.ul({"class": "ps-0"}))

    description = x.get("description")
    composition = x.get("composition")
    location = x.get("location")
    photographer = x.get("photographer")
    process = x.get("process")

    if description:
        result.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Description: "),
                ui.markdown(description)
            )
        )

    if composition:
        result.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Composition: "),
                ui.markdown(composition)
            )
        )

    if location:
        result.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Location: "),
                ui.markdown(location)
            )
        )

    if photographer:
        result.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Photographer: "),
                ui.markdown(photographer)
            )
        )

    if process:
        result.append(
            ui.tags.div(
                {"class": "list-group-item pb-1"},
                ui.span({"class": "fw-bold"}, "Process: "),
                ui.markdown(process)
            )
        )

    return result
