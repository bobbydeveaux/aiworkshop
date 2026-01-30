#!/usr/bin/env python3
"""
Tests for random_words.py script
"""

import unittest
import logging
import io
from unittest.mock import patch
from random_words import get_word_list, generate_random_words, setup_logging


class TestRandomWords(unittest.TestCase):
    """Test cases for random words generator."""

    def test_word_list_not_empty(self):
        """Test that word list is not empty."""
        words = get_word_list()
        self.assertGreater(len(words), 0, "Word list should not be empty")

    def test_word_list_contains_strings(self):
        """Test that word list contains only strings."""
        words = get_word_list()
        for word in words:
            self.assertIsInstance(word, str, f"{word} should be a string")

    def test_generate_100_words_default(self):
        """Test that generate_random_words returns exactly 100 words by default."""
        random_words = generate_random_words()
        self.assertEqual(len(random_words), 100, "Should generate exactly 100 words by default")

    def test_generate_50_words(self):
        """Test that generate_random_words returns exactly 50 words when specified."""
        random_words = generate_random_words(50)
        self.assertEqual(len(random_words), 50, "Should generate exactly 50 words")

    def test_generate_custom_count(self):
        """Test that generate_random_words can generate different counts."""
        for count in [10, 25, 50, 150]:
            random_words = generate_random_words(count)
            self.assertEqual(len(random_words), count, f"Should generate exactly {count} words")

    def test_generated_words_are_strings(self):
        """Test that all generated words are strings."""
        random_words = generate_random_words(100)
        for word in random_words:
            self.assertIsInstance(word, str, f"{word} should be a string")

    def test_generated_words_from_word_list(self):
        """Test that generated words are from the word list."""
        word_list = get_word_list()
        random_words = generate_random_words(100)
        for word in random_words:
            self.assertIn(word, word_list, f"{word} should be from the word list")

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

    @patch('random_words.logging')
    def test_get_word_list_logs_info(self, mock_logging):
        """Test that get_word_list logs appropriate info messages."""
        get_word_list()

        # Verify logging calls
        mock_logging.info.assert_any_call("Loading word list")
        # Check that it logs the count (should be 100 words)
        mock_logging.info.assert_any_call("Loaded 100 words")

    @patch('random_words.logging')
    def test_generate_random_words_logs_info(self, mock_logging):
        """Test that generate_random_words logs appropriate info messages."""
        generate_random_words(5)

        # Verify logging calls
        mock_logging.info.assert_any_call("Generating 5 random words")
        mock_logging.info.assert_any_call("Successfully generated 5 random words")


if __name__ == '__main__':
    unittest.main()
