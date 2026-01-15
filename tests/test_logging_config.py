"""Tests for media_organizer.logging_config module."""

import logging
import pytest

from media_organizer.logging_config import setup_logging, get_logger


class TestSetupLogging:
    """Tests for setup_logging function."""

    def test_returns_logger(self):
        """Test setup_logging returns a logger."""
        logger = setup_logging(logger_name="test_setup_1")
        assert isinstance(logger, logging.Logger)

    def test_default_level_info(self):
        """Test default level is INFO."""
        logger = setup_logging(logger_name="test_setup_2")
        assert logger.level == logging.INFO

    def test_custom_level_int(self):
        """Test setting level with integer."""
        logger = setup_logging(level=logging.DEBUG, logger_name="test_setup_3")
        assert logger.level == logging.DEBUG

    def test_custom_level_string(self):
        """Test setting level with string."""
        logger = setup_logging(level="WARNING", logger_name="test_setup_4")
        assert logger.level == logging.WARNING

    def test_custom_level_string_lowercase(self):
        """Test setting level with lowercase string."""
        logger = setup_logging(level="debug", logger_name="test_setup_5")
        assert logger.level == logging.DEBUG

    def test_handler_added(self):
        """Test that a handler is added."""
        logger = setup_logging(logger_name="test_setup_6")
        assert len(logger.handlers) >= 1

    def test_no_duplicate_handlers(self):
        """Test calling setup_logging twice doesn't add duplicate handlers."""
        logger_name = "test_setup_no_dup"
        logger1 = setup_logging(logger_name=logger_name)
        handler_count = len(logger1.handlers)
        logger2 = setup_logging(logger_name=logger_name)
        assert len(logger2.handlers) == handler_count
        assert logger1 is logger2


class TestGetLogger:
    """Tests for get_logger function."""

    def test_get_logger_without_name(self):
        """Test get_logger without name returns base logger."""
        logger = get_logger()
        assert logger.name == "media_organizer"

    def test_get_logger_with_name(self):
        """Test get_logger with name returns child logger."""
        logger = get_logger("test")
        assert logger.name == "media_organizer.test"

    def test_get_logger_nested_name(self):
        """Test get_logger with nested name."""
        logger = get_logger("core.scanner")
        assert logger.name == "media_organizer.core.scanner"

    def test_get_logger_returns_same_instance(self):
        """Test get_logger returns same instance for same name."""
        logger1 = get_logger("same_name")
        logger2 = get_logger("same_name")
        assert logger1 is logger2

    def test_get_logger_different_names(self):
        """Test get_logger returns different instances for different names."""
        logger1 = get_logger("name1")
        logger2 = get_logger("name2")
        assert logger1 is not logger2
