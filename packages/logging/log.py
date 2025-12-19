import sys
from loguru import logger
from pathlib import Path
from packages.config import cfg

# 移除默认的 stderr 处理器
logger.remove()

# 控制台日志（带颜色）
logger.add(
    sys.stderr,
    level=cfg.log.level,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>",
    colorize=True,
)

# 文件日志（按 10 MB 轮换，保留 5 个）
logger.add(
    Path("logs/app.log"),
    rotation=cfg.log.rotation,
    retention=cfg.log.retention,
    level=cfg.log.level,
    encoding="utf-8",
    backtrace=True,
    diagnose=True,
)

# 可选：JSON 结构化日志
# logger.add("logs/app.json", serialize=True, rotation="10 MB", retention=5)

__all__ = ["logger"]
