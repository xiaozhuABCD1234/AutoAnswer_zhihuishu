from playwright.sync_api import (
    sync_playwright,
    Page,
    Playwright,
    Browser,
    # Locator,
    BrowserContext,
)

# from playwright.async_api import async_playwright, Page
from packages.config import cfg
from packages.logger import logger
from packages.crawler import crawl_popular_question, crawl_latest_question
from packages.answer import answer
from packages.utils import load_cookies, save_cookies
import time


def open_browser(playwright: Playwright) -> tuple[Browser, BrowserContext]:
    """启动浏览器并返回浏览器和上下文对象
    Args:
        playwright: Playwright实例
    Returns:
        tuple: 包含浏览器实例和上下文对象的元组
    Raises:
        Exception: 浏览器启动失败时抛出异常
    """
    try:
        # 使用Chromium内核启动浏览器
        launch_kwargs = {
            "channel": cfg.option.driver,
            "headless": False,
            "args": [
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding",
                "--start-minimized",
                "--disable-blink-features=AutomationControlled",
            ],
        }
        if cfg.option.browser_path != "":
            launch_kwargs["executable_path"] = cfg.option.browser_path
        # 启动浏览器
        browser = playwright.chromium.launch(**launch_kwargs)
        # 创建新的浏览器上下文
        context = browser.new_context()
        # 加载反检测脚本（避免被识别为自动化工具）
        with open("scripts/stealth.min.js", "r", encoding="utf-8") as f:
            stealth_js = f.read()
        context.add_init_script(stealth_js)
        # 加载本地Cookie
        cookies = load_cookies("data/cookies.json")
        if cookies:
            context.add_cookies(cookies)
            logger.info("已加载本地Cookie，尝试免密登录")
        else:
            logger.info("未找到本地Cookie，将进行手动登录")
        return browser, context
    except Exception as e:
        logger.error(f"浏览器启动失败: {e}")
        raise


def login(page: Page, context: BrowserContext) -> Page:
    """登录到智慧树网
    Args:
        page: Playwright页面对象
    Returns:
        Page: 登录成功后的页面对象
    Raises:
        TimeoutError: 操作超时时抛出
        Exception: 登录失败时抛出
    """
    try:
        # 访问登录页面（设置30秒超时）
        page.goto("https://passport.zhihuishu.com/login", timeout=30000)
        # 首次检查URL：如果不含"login"，说明Cookie有效
        if "login" not in page.url:
            logger.info("检测到已通过Cookie登录，跳过手动登录")
            return page
        logger.info("Cookie无效或未登录，进行手动登录")

        # 填写用户名和密码
        username_input = page.get_by_role("textbox", name="请输入手机号")
        username_input.fill(str(cfg.account.username), timeout=10000)
        password_input = page.get_by_role("textbox", name="请输入密码")
        password_input.fill(str(cfg.account.password), timeout=10000)

        # 点击登录按钮
        page.get_by_text("登 录").click(timeout=5000)
        logger.warning("请手动完成验证码验证！")  # 需要人工干预验证码

        # 等待网络空闲（最长等待60秒）
        page.wait_for_load_state("networkidle", timeout=60000)
        # 确认登录后再保存Cookie（此时URL已无"login"，确保有效）
        cookies = context.cookies()
        save_cookies(cookies, "data/cookies.json")
        logger.info("已保存有效登录Cookie到: data/cookies.json")
        logger.info("登录成功！")
        return page
    except TimeoutError as e:
        logger.error(f"登录超时: {e}")
        raise
    except Exception as e:
        logger.error(f"登录失败: {e}")
        raise


def main():
    start_time = time.time()  # 总开始时间

    with sync_playwright() as playwright:
        try:
            # 初始化浏览器
            browser, context = open_browser(playwright)

            # 登录操作
            login_page = context.new_page()
            login_start = time.time()  # 登录计时开始
            login(login_page, context)
            logger.info(f"登录耗时: {time.time() - login_start:.2f}秒")  # 记录登录耗时
            login_page.close()

            # 遍历课程
            for index, course_url in enumerate(cfg.option.question_urls):
                course_start = time.time()  # 单课程计时开始
                page = context.new_page()
                try:
                    logger.info(f"开始处理课程 {index+1}/{len(cfg.option.question_urls)}")

                    # 爬取问题计时
                    crawl_start = time.time()

                    questions = crawl_latest_question(page, course_url)
                    logger.info(f"问题爬取耗时: {time.time() - crawl_start:.2f}秒")

                    # 回答问题计时
                    answer_start = time.time()
                    answer(page, questions)
                    logger.info(f"回答处理耗时: {time.time() - answer_start:.2f}秒")

                    logger.info(f"成功完成课程: {course_url}")
                except Exception as e:
                    logger.error(f"课程处理失败: {course_url} - {str(e)}")
                finally:
                    page.close()
                    # 记录单课程耗时
                    logger.info(
                        f"课程{index+1}总耗时: {time.time() - course_start:.2f}秒\n"
                    )

        finally:
            context.close()
            browser.close()
            total_time = time.time() - start_time  # 计算总耗时
            logger.info(f"任务总耗时: {total_time:.2f}秒")
            print(
                f"""
   ╱|、　　　　　　　　　　　ฅ^•ﻌ•^ฅ
  (˚ˎ 。7　　　　　　　　　　喵喵感谢~
   |、˜〵　　　　　　　　　 耗时{total_time:.1f}秒~
   じしˍ,)ノ
问答任务已完成 [✓]
☆ *　. 　☆ ✨ 传送门 ➤https://github.com/xiaozhuABCD1234/AutoAnswer_zhihuishu
　　. ∧＿∧　∩　* ☆ 主人记得给仓库加个星星哦～⭐
* ☆ ( ・∀・)/ .
　. ⊂　　 ノ* ☆
☆ * (つ ノ .☆
　　 (ノ
"""
            )


if __name__ == "__main__":
    main()
