from pydantic import BaseModel
from typing import Optional


class TokenUsage(BaseModel):
    """
    Token使用情况模型
    """
    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    model: Optional[str] = None
    input_text: Optional[str] = None
    output_text: Optional[str] = None
