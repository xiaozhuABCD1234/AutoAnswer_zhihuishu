from playwright.sync_api import (
    sync_playwright,
    Page,
    Playwright,
    Browser,
    # Locator,
    BrowserContext,
)
import time

# from playwright.async_api import async_playwright, Page
from packages.config import cfg
from packages.logging.log import logger
from packages.crawler import crawl_popular_question, crawl_latest_question
from packages.answer import answer
from packages.browser import open_browser, login


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
            for index, course_url in enumerate(cfg.option.Q_A_urls):
                course_start = time.time()  # 单课程计时开始
                page = context.new_page()
                try:
                    logger.info(f"开始处理课程 {index+1}/{len(cfg.option.Q_A_urls)}")

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
