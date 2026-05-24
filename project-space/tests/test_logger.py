#!/usr/bin/env python3
"""logger.py 单元测试"""

import logging
from pathlib import Path
import sys
import tempfile
import os

import pytest

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from utils.logger import get_logger


class TestGetLogger:
    """get_logger 函数测试"""

    def test_get_logger_returns_logger_instance(self):
        logger = get_logger('test_module', '2026-05-23')
        assert logger.name == 'test_module'
        assert logger.level == logging.INFO
        assert len(logger.handlers) == 1

    def test_get_logger_has_file_handler(self):
        logger = get_logger('handler_test', '2026-05-23')
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.FileHandler)

    def test_get_logger_handlers_cleared_on_reinit(self):
        logger1 = get_logger('clear_test', '2026-05-23')
        initial_handler_count = len(logger1.handlers)

        logger2 = get_logger('clear_test', '2026-05-23')
        assert len(logger2.handlers) == initial_handler_count

    def test_get_logger_different_names(self):
        logger_a = get_logger('module_a', '2026-05-23')
        logger_b = get_logger('module_b', '2026-05-23')
        assert logger_a.name == 'module_a'
        assert logger_b.name == 'module_b'

    def test_get_logger_formatter_format(self):
        logger = get_logger('format_check', '2026-05-23')
        handler = logger.handlers[0]
        formatter = handler.formatter
        assert formatter is not None
        format_str = formatter._fmt
        assert '%(name)s' in format_str
        assert 'levelname' in format_str
        assert '%(message)s' in format_str
