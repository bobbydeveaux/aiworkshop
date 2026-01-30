#!/usr/bin/env python3
"""
Script to output random red or blue colors.
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
            logging.FileHandler('random_colors.log', mode='a')
        ]
    )


def get_color_list():
    """Return a list of colors to randomly select from."""
    logging.info("Loading color list")
    colors = ["red", "blue"]
    logging.info(f"Loaded {len(colors)} colors")
    return colors


def generate_random_colors(count=1):
    """Generate a specified number of random colors.

    Args:
        count: Number of random colors to generate (default: 1)

    Returns:
        List of randomly selected colors (red or blue)
    """
    logging.info(f"Generating {count} random color(s)")
    colors = get_color_list()
    selected_colors = random.choices(colors, k=count)
    logging.info(f"Successfully generated {len(selected_colors)} random color(s)")
    logging.debug(f"Generated colors: {', '.join(selected_colors)}")
    return selected_colors


def main():
    """Main function to output random red or blue color."""
    setup_logging()
    logging.info("Starting random colors script")

    try:
        random_colors = generate_random_colors(1)
        color = random_colors[0]

        logging.info("Displaying random color to user")
        print(f"Random Color: {color}")

        logging.info("Script completed successfully")
    except Exception as e:
        logging.error(f"An error occurred: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()