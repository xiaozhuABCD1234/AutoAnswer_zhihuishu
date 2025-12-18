# app/core/config.py
from __future__ import annotations

import os
import tomllib
from pathlib import Path
from string import Template
from typing import Final, List

import dotenv
from pydantic import BaseModel, Field, field_validator

# ---------- 路径常量 ----------
TOML_PATH: Final = Path(__file__).resolve().parent.with_name("config.toml")

# ---------- 通用校验 ----------
LOG_LEVELS: Final = {
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


# ==========================
# 配置模型
# ==========================
class AccountCfg(BaseModel):
    username: str = Field(default="", description="登录账号；优先读环境变量 USERNAME")
    password: str = Field(default="", description="登录密码；优先读环境变量 PASSWORD")


class OptionCfg(BaseModel):
    driver: str = Field(default="edge", description="浏览器驱动类型")
    browser_path: str = Field(
        default="", description="浏览器可执行文件绝对路径；空则自动发现"
    )
    delay_time_s: int = Field(default=10, ge=0, description="操作延迟基准（秒）")
    enabled_random_time: bool = Field(default=True, description="是否启用随机延时")
    question_urls: List[str] = Field(
        default_factory=lambda: [],
        description="待刷题页面地址列表",
    )


class LLMCfg(BaseModel):
    base_url: str = Field(
        default="https://api.deepseek.com/v1", description="API 基地址"
    )
    api_key: str = Field(
        default="${OPENAI_API_KEY}",
        description="API Key；优先读环境变量 OPENAI_API_KEY",
    )
    model: str = Field(default="deepseek-chat", description="模型名称")
    max_tokens: int = Field(default=500, gt=0, description="最大生成 token 数")
    temperature: float = Field(default=1.3, ge=0, le=2, description="采样温度")


class LogCfg(BaseModel):
    level: str = Field(default="DEBUG", description="控制台日志级别")
    file_level: str = Field(default="WARNING", description="文件日志级别")
    file_path: str = Field(default="log/app.log", description="日志文件路径")
    colorful_output: bool = Field(default=True, description="是否彩色控制台输出")
    rotation: str = Field(default="10 MB", description="单文件最大尺寸")
    retention: int = Field(default=5, ge=0, description="保留历史文件数")
    time_format: str = Field(default="%Y-%m-%d %H:%M:%S", description="时间戳格式")

    @field_validator("level", "file_level", mode="before")
    @classmethod
    def _check_level(cls, v: str) -> str:
        lv = v.upper().strip()
        if lv not in LOG_LEVELS:
            raise ValueError(f"非法日志级别 {v!r}，允许值: {LOG_LEVELS}")
        return lv


# ---------- 顶层容器 ----------
class Config(BaseModel):
    account: AccountCfg = AccountCfg()
    option: OptionCfg = OptionCfg()
    llm: LLMCfg = LLMCfg()
    log: LogCfg = LogCfg()


# ==========================
# 单例加载
# ==========================
def load_cfg() -> Config:
    """加载并返回全局单例配置"""
    env_path = TOML_PATH.with_name(".env")
    dotenv.load_dotenv(env_path, override=True)

    raw = TOML_PATH.read_text(encoding="utf-8")
    resolved = Template(raw).safe_substitute(os.environ)  # 替换 ${XXX}
    return Config.model_validate(tomllib.loads(resolved))


cfg: Final[Config] = load_cfg()
