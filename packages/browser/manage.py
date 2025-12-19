from playwright.sync_api import Playwright,Browser,BrowserContext,Page

from packages.config import cfg
from packages.logging import logger
from packages.utils import load_cookies,save_cookies

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