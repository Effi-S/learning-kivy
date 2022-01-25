"""This module holds simple utility functions."""
import re
from typing import Iterable
from difflib import SequenceMatcher
from kivymd.uix.textfield import MDTextField


def similarity(a: str, b: str) -> float:
    """Get similarity between 2 strings based on diff-lib's SequenceMatcher ratio"""
    return SequenceMatcher(None, str(a), str(b)).ratio()


def sort_by_similarity(iterable: Iterable[str], target: str) -> Iterable:
    """Sort an iterable based on it's similarity to a given target.
    Sorts most-similary to least similary"""
    ret = sorted(iterable, key=lambda x: similarity(x, target), reverse=True)
    return ret


class RTLMDTextField(MDTextField):
    """TextField Input that allows rtl."""
    _reg = re.compile(r'[a-zA-Z]')

    def insert_text(self, s, from_undo=False):
        if s.isalpha() and not self._reg.findall(s):
            self.text = s + self.text
            return super().insert_text('', from_undo=from_undo)
        return super().insert_text(s, from_undo=from_undo)