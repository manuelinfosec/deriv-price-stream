"""Helper functions"""

import random


def generate_random_number(seed: int | None = None) -> int:
    """Generates random based on the given seed"""
    if seed:
        random.seed(seed)
    # Generate a random number in the range of 0 to 10 million
    return random.randrange(10_000_000)
