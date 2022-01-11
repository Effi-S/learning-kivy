"""This module holds simple utility functions."""
from typing import Iterable
from difflib import SequenceMatcher


def similarity(a: str, b: str) -> float:
    """Get similarity between 2 strings based on diff-lib's SequenceMatcher ratio"""
    return SequenceMatcher(None, str(a), str(b)).ratio()


def sort_by_similarity(iterable: Iterable[str], target: str) -> Iterable:
    """Sort an iterable based on it's similarity to a given target.
    Sorts most-similary to least similary"""
    ret = sorted(iterable, key=lambda x: similarity(x, target), reverse=True)
    return ret
