#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
utils/logger.py — 统一日志模块

所有脚本通过 get_logger() 获取日志记录器，日志统一写入 output/{date}/run.log
通过日志格式中的 %(name)s 区分不同模块的日志
"""

import logging
from pathlib import Path


def get_logger(name: str, date: str) -> logging.Logger:
    """获取日志记录器

    Args:
        name: 模块名称（如 'publish2lark', 'push2group'），用于日志格式中标识来源
        date: 日期字符串（YYYY-MM-DD）

    Returns:
        配置好的 Logger 实例

    日志路径：output/{date}/run.log（所有模块共用一个文件，通过 name 区分）
    """
    project_root = Path(__file__).parent.parent.parent
    log_dir = project_root / 'output' / date
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / 'run.log'

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = logging.FileHandler(log_file, encoding='utf-8')
    handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)-8s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ))
    logger.addHandler(handler)

    return logger
