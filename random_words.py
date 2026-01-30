#!/usr/bin/env python3
"""
Script to output 100 random words.
"""

import random
import logging
import sys


def setup_logging():
    """Configure logging for the script."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('random_words.log', mode='a')
        ]
    )


def get_word_list():
    """Return a list of words to randomly select from."""
    logging.info("Loading word list")
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
    logging.info(f"Loaded {len(words)} words")
    return words


def generate_random_words(count=100):
    """Generate a specified number of random words.

    Args:
        count: Number of random words to generate (default: 100)

    Returns:
        List of randomly selected words
    """
    logging.info(f"Generating {count} random words")
    words = get_word_list()
    selected_words = random.choices(words, k=count)
    logging.info(f"Successfully generated {len(selected_words)} random words")
    logging.debug(f"Generated words: {', '.join(selected_words)}")
    return selected_words


def main():
    """Main function to output 100 random words."""
    setup_logging()
    logging.info("Starting random words script")

    try:
        random_words = generate_random_words(100)

        logging.info("Displaying random words to user")
        print("100 Random Words:")
        print("=" * 100)
        for i, word in enumerate(random_words, 1):
            print(f"{i:3d}. {word}")
        print("=" * 100)
        print(f"Total: {len(random_words)} words")

        logging.info("Script completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
