from pathlib import Path
from openai import OpenAI

from packages.config import cfg
from packages.logging import logger
from packages.models.token_usage import TokenUsage

client = OpenAI(
    api_key=cfg.llm.api_key,
    base_url=cfg.llm.base_url,
)

# 统一用 Path，Windows/Linux 都能用
PACKAGE_DIR = Path(__file__).resolve().parent
Q_PROMPT_FILE = PACKAGE_DIR / "prompts" / "questions.md"
A_PROMPT_FILE = PACKAGE_DIR / "prompts" / "answer.md"
Q_system_prompt = Q_PROMPT_FILE.read_text(encoding="utf-8")
A_system_prompt = A_PROMPT_FILE.read_text(encoding="utf-8")


def gen_questions(topic: str, question_number: int = 5) -> tuple[list[str], TokenUsage]:
    logger.info(f"生成问题 - 主题: {topic[:15]}{'...' if len(topic) > 15 else ''}")

    response = client.chat.completions.create(
        model=cfg.llm.model,  # 按需换成 gpt-4
        messages=[
            {"role": "system", "content": Q_system_prompt},
            {
                "role": "user",
                "content": f"主题:{topic},question_number:{question_number}",
            },
        ],
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens,
    )

    # 记录token使用情况
    prompt_tokens = (
        response.usage.prompt_tokens
        if hasattr(response, "usage") and response.usage
        else 0
    )
    completion_tokens = (
        response.usage.completion_tokens
        if hasattr(response, "usage") and response.usage
        else 0
    )
    total_tokens = (
        response.usage.total_tokens
        if hasattr(response, "usage") and response.usage
        else 0
    )

    logger.info(
        f"问题生成 - Token使用: 输入({prompt_tokens}) + 输出({completion_tokens}) = 总计({total_tokens})"
    )

    raw: str = str(response.choices[0].message.content)

    # 记录生成的问题预览
    questions = [line.strip() for line in raw.splitlines() if line.strip()]
    for i, q in enumerate(questions[:3]):  # 只记录前3个问题的预览
        logger.info(f"生成问题[{i+1}]预览: {q[:15]}{'...' if len(q) > 15 else ''}")

    usage_info = TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        model=cfg.llm.model,
        input_text=f"主题:{topic},question_number:{question_number}",
        output_text=raw
    )

    return questions, usage_info


def gen_answer(question: str, context: str = "") -> tuple[str, TokenUsage]:
    """
    针对智慧树单题生成高质量回答。
    :param question: 学生提出的问题
    :param context:  可选上下文，如章节、教材原文或老师提示
    :return:         纯答案文本和用量信息的元组
    """
    logger.info(
        f"生成回答 - 问题: {question[:15]}{'...' if len(question) > 15 else ''}"
    )

    user_prompt = f"问题：{question}"
    if context:
        user_prompt += f"\n上下文：{context}"

    response = client.chat.completions.create(
        model=cfg.llm.model,
        messages=[
            {"role": "system", "content": A_system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=cfg.llm.temperature,
        max_tokens=cfg.llm.max_tokens,
    )

    # 记录token使用情况
    prompt_tokens = (
        response.usage.prompt_tokens
        if hasattr(response, "usage") and response.usage
        else 0
    )
    completion_tokens = (
        response.usage.completion_tokens
        if hasattr(response, "usage") and response.usage
        else 0
    )
    total_tokens = (
        response.usage.total_tokens
        if hasattr(response, "usage") and response.usage
        else 0
    )

    logger.info(
        f"回答生成 - Token使用: 输入({prompt_tokens}) + 输出({completion_tokens}) = 总计({total_tokens})"
    )

    raw = response.choices[0].message.content

    # 记录生成的回答预览
    answer_preview = raw.strip() if raw else ""
    logger.info(
        f"生成回答预览: {answer_preview[:15]}{'...' if len(answer_preview) > 15 else ''}"
    )
    
    usage_info = TokenUsage(
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        total_tokens=total_tokens,
        model=cfg.llm.model,
        input_text=user_prompt,
        output_text=raw
    )

    return raw.strip() if raw else "", usage_info


if __name__ == "__main__":
    questions, q_usage = gen_questions("马克思主义基本原理", 5)
    for q in questions:
        print("问题：" + q)
        answer, a_usage = gen_answer(q)
        print("回答：" + answer)
        print(f"问题Token: {q_usage}, 回答Token: {a_usage}")
        print("-" * 10)
