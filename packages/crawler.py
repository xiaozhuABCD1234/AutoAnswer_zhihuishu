from playwright.sync_api import (
    sync_playwright,
    Page,
)
from packages.logger import logger

def crawl_popular_question(page: Page, url: str) -> list[str]:
    """爬取热门问题
    Args:
        page: 已登录的页面对象
        url: 目标页面URL
    Returns:
        list[str]: 问题文本列表
    Raises:
        多种异常: 包含超时、元素未找到等错误
    """
    try:
        # 访问目标页面（设置2分钟超时）
        page.goto(url, timeout=120000)
        page.wait_for_load_state("networkidle", timeout=120000)  # 等待网络空闲

        # 等待问题容器加载（最多等待60秒）
        page.wait_for_selector(".question-item", timeout=60000)
        questions = page.query_selector_all(".question-item")

        # 问题容器检测
        if not questions:
            raise ValueError("未检测到题目容器，请检查页面结构！")

        # 解析问题内容
        question_texts = []
        for question_element in questions:
            # 定位问题内容区域
            content_div = question_element.query_selector(
                ".question-content.ZHIHUISHU_QZMD"
            )
            if content_div:
                # 提取纯文本内容并去除首尾空格
                text = content_div.inner_text().strip()
                question_texts.append(text)
            else:
                logger.warning("某个问题项未找到问题内容容器")

        logger.info(f"成功解析 {len(question_texts)} 道热门题目")
        return question_texts

    except TimeoutError as e:
        logger.error(f"页面加载超时: {url} - {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"页面解析错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理页面 {url} 时发生未知错误: {str(e)}")
        raise


def crawl_latest_question(page: Page, url: str) -> list[str]:
    """爬取最新问题（与热门问题逻辑相似，增加排序操作）
    Args:
        page: 已登录的页面对象
        url: 目标页面URL
    Returns:
        list[str]: 问题文本列表
    """
    try:
        page.goto(url, timeout=120000)
        page.wait_for_load_state("networkidle", timeout=120000)
        page.wait_for_selector(".question-item", timeout=60000)

        # 点击"最新"排序标签（核心差异点）
        page.get_by_text("最新").click()
        page.wait_for_load_state("networkidle")  # 等待排序后的内容加载
        page.wait_for_selector(".question-item", timeout=60000)

        # 后续解析逻辑与热门问题相同
        questions = page.query_selector_all(".question-item")
        if not questions:
            raise ValueError("未检测到题目容器，请检查页面结构！")

        question_texts = []
        for question_element in questions:
            content_div = question_element.query_selector(
                ".question-content.ZHIHUISHU_QZMD"
            )
            if content_div:
                text = content_div.inner_text().strip()
                question_texts.append(text)
            else:
                logger.warning("某个问题项未找到问题内容容器")

        logger.info(f"成功解析 {len(question_texts)} 道最新题目")
        return question_texts

    except TimeoutError as e:
        logger.error(f"页面加载超时: {url} - {str(e)}")
        raise
    except ValueError as e:
        logger.error(f"页面解析错误: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"处理页面 {url} 时发生未知错误: {str(e)}")
        raise
