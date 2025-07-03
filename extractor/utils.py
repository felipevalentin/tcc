import functools
import html
import re
import time

import log
from bs4 import BeautifulSoup
from pydantic import ValidationError

logger = log.get_logger(__name__)


def clean_html_text(input_text: str) -> str:
    """
    Cleans HTML text by removing tags and normalizing whitespace.

    Args:
        input_text: The input HTML text.

    Returns:
        The cleaned text.
    """
    text_without_html = BeautifulSoup(input_text, "html.parser").get_text()
    text_unescaped = html.unescape(text_without_html)
    text_normalized_x00 = re.sub(r"\x00", "", text_unescaped)
    text_normalized_fffd = re.sub(r"\uFFFD", "", text_normalized_x00)
    text_normalized_new_lines = re.sub(r"\n{2, }", "\n\n", text_normalized_fffd)
    text_normalized_spaces = re.sub(r" +", " ", text_normalized_new_lines)
    return text_normalized_spaces.strip().strip("\n").strip("\r")
