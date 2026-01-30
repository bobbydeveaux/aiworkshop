#!/usr/bin/env python3
"""
Tests for random_colors.py script
"""

import unittest
import logging
import io
from unittest.mock import patch
from random_colors import get_color_list, generate_random_colors, setup_logging


class TestRandomColors(unittest.TestCase):
    """Test cases for random colors generator."""

    def test_color_list_not_empty(self):
        """Test that color list is not empty."""
        colors = get_color_list()
        self.assertGreater(len(colors), 0, "Color list should not be empty")

    def test_color_list_contains_strings(self):
        """Test that color list contains only strings."""
        colors = get_color_list()
        for color in colors:
            self.assertIsInstance(color, str, f"{color} should be a string")

    def test_color_list_contains_red_and_blue(self):
        """Test that color list contains red and blue."""
        colors = get_color_list()
        self.assertIn("red", colors, "Color list should contain 'red'")
        self.assertIn("blue", colors, "Color list should contain 'blue'")
        self.assertEqual(len(colors), 2, "Color list should contain exactly 2 colors")

    def test_generate_1_color_default(self):
        """Test that generate_random_colors returns exactly 1 color by default."""
        random_colors = generate_random_colors()
        self.assertEqual(len(random_colors), 1, "Should generate exactly 1 color by default")

    def test_generate_5_colors(self):
        """Test that generate_random_colors returns exactly 5 colors when specified."""
        random_colors = generate_random_colors(5)
        self.assertEqual(len(random_colors), 5, "Should generate exactly 5 colors")

    def test_generate_custom_count(self):
        """Test that generate_random_colors can generate different counts."""
        for count in [1, 3, 10, 25]:
            random_colors = generate_random_colors(count)
            self.assertEqual(len(random_colors), count, f"Should generate exactly {count} colors")

    def test_generated_colors_are_strings(self):
        """Test that all generated colors are strings."""
        random_colors = generate_random_colors(10)
        for color in random_colors:
            self.assertIsInstance(color, str, f"{color} should be a string")

    def test_generated_colors_from_color_list(self):
        """Test that generated colors are from the color list."""
        color_list = get_color_list()
        random_colors = generate_random_colors(20)
        for color in random_colors:
            self.assertIn(color, color_list, f"{color} should be from the color list")

    def test_generated_colors_only_red_or_blue(self):
        """Test that generated colors are only red or blue."""
        random_colors = generate_random_colors(50)
        for color in random_colors:
            self.assertIn(color, ["red", "blue"], f"{color} should be either 'red' or 'blue'")

    def test_setup_logging_configures_logger(self):
        """Test that setup_logging configures the logger correctly."""
        # Clear existing handlers
        logger = logging.getLogger()
        logger.handlers.clear()

        # Setup logging
        setup_logging()

        # Check that handlers are configured
        self.assertGreater(len(logger.handlers), 0, "Logger should have handlers after setup")
        self.assertEqual(logger.level, logging.INFO, "Logger level should be INFO")

    @patch('random_colors.logging')
    def test_get_color_list_logs_info(self, mock_logging):
        """Test that get_color_list logs appropriate info messages."""
        get_color_list()

        # Verify logging calls
        mock_logging.info.assert_any_call("Loading color list")
        # Check that it logs the count (should be 2 colors)
        mock_logging.info.assert_any_call("Loaded 2 colors")

    @patch('random_colors.logging')
    def test_generate_random_colors_logs_info(self, mock_logging):
        """Test that generate_random_colors logs appropriate info messages."""
        generate_random_colors(3)

        # Verify logging calls
        mock_logging.info.assert_any_call("Generating 3 random color(s)")
        mock_logging.info.assert_any_call("Successfully generated 3 random color(s)")

    def test_randomness_over_multiple_generations(self):
        """Test that multiple generations produce both red and blue over time."""
        # Generate many colors to statistically ensure we get both red and blue
        all_colors = []
        for _ in range(100):
            colors = generate_random_colors(1)
            all_colors.extend(colors)

        # With 100 generations, we should have both colors (very high probability)
        unique_colors = set(all_colors)
        self.assertGreaterEqual(len(unique_colors), 2,
                               "Over 100 generations, should see both red and blue colors")
        self.assertIn("red", unique_colors, "Should generate red over multiple runs")
        self.assertIn("blue", unique_colors, "Should generate blue over multiple runs")


if __name__ == '__main__':
    unittest.main()