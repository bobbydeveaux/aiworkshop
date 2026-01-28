#!/usr/bin/env python3
"""
Script to output 50 random words.
"""

import random


def get_word_list():
    """Return a list of words to randomly select from."""
    words = [
        "apple", "banana", "cherry", "dragon", "eagle", "falcon", "giraffe", "hamster",
        "iguana", "jaguar", "kangaroo", "leopard", "monkey", "newt", "octopus", "penguin",
        "quail", "rabbit", "snake", "tiger", "umbrella", "viper", "walrus", "xerus",
        "yak", "zebra", "anchor", "bridge", "castle", "diamond", "emerald", "fortress",
        "galaxy", "harbor", "island", "jungle", "knight", "lantern", "mountain", "nebula",
        "ocean", "palace", "quarry", "river", "summit", "temple", "universe", "valley",
        "waterfall", "xenon", "yacht", "zephyr", "adventure", "bravery", "courage", "destiny",
        "energy", "freedom", "glory", "harmony", "infinity", "justice", "knowledge", "liberty",
        "mystery", "nobility", "opportunity", "passion", "quality", "reason", "serenity", "truth",
        "unity", "victory", "wisdom", "excellence", "youth", "zenith", "art", "beauty",
        "creativity", "discovery", "elegance", "fantasy", "grace", "hope", "imagination", "joy",
        "kindness", "light", "magic", "nature", "optimism", "peace", "quest", "radiance",
        "strength", "tranquility", "understanding", "virtue", "wonder", "xanadu", "yearning", "zeal"
    ]
    return words


def generate_random_words(count=50):
    """Generate a specified number of random words.

    Args:
        count: Number of random words to generate (default: 50)

    Returns:
        List of randomly selected words
    """
    words = get_word_list()
    return random.choices(words, k=count)


def main():
    """Main function to output 50 random words."""
    random_words = generate_random_words(50)

    print("50 Random Words:")
    print("=" * 50)
    for i, word in enumerate(random_words, 1):
        print(f"{i:2d}. {word}")
    print("=" * 50)
    print(f"Total: {len(random_words)} words")


if __name__ == "__main__":
    main()
