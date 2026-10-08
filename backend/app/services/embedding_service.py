import math
import re
from collections import Counter


def tokenize(text: str) -> list[str]:
    """
    Convert text into simple lowercase word tokens.
    """

    return re.findall(r"\b[a-zA-Z0-9]+\b", text.lower())


def generate_embedding(text: str) -> list[float]:
    """
    Create a lightweight pure-Python text vector.

    This does not use external ML libraries or compiled DLLs.
    """

    tokens = tokenize(text)

    if not tokens:
        return []

    counts = Counter(tokens)
    total = len(tokens)

    vocabulary = sorted(counts.keys())

    vector = []

    for word in vocabulary:
        frequency = counts[word] / total
        vector.append(frequency)

    magnitude = math.sqrt(
        sum(value * value for value in vector)
    )

    if magnitude == 0:
        return vector

    return [
        value / magnitude
        for value in vector
    ]