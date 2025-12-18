import random
import time
import os
import json

def get_random(n: int) -> int:
    random.seed(time.time())
    return random.randint(int(n / 2), int(n * 1.5))

def load_cookies(file_path: str):
    """加载本地Cookie文件"""
    if not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            cookies = json.load(f)
        # 新增：校验Cookie是否为空或无效
        if not cookies or not isinstance(cookies, list) or len(cookies) == 0:
            print("Cookie文件内容为空或无效")
            return None
        return cookies
    except json.JSONDecodeError:
        print("Cookie文件格式错误（非有效JSON）")
        return None
    except Exception as e:
        print(f"加载Cookie失败: {e}")
        return None

def save_cookies(cookies, file_path: str):
    """保存Cookie到本地文件"""
    # 创建目录（如果不存在）
    dir_path = os.path.dirname(file_path)
    if dir_path and not os.path.exists(dir_path):
        os.makedirs(dir_path, exist_ok=True)
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(cookies, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"保存Cookie失败: {e}")

        
# start_time = time.time()  # 总开始时间
# time.sleep(1)
# total_time = time.time() - start_time  # 计算总耗时

# print(
#     f"""
#    ╱|、　　　　　　　　　　　ฅ^•ﻌ•^ฅ
#   (˚ˎ 。7　　　　　　　　　　喵喵感谢~
#    |、˜〵　　　　　　　　　 耗时{total_time:.1f}秒~
#    じしˍ,)ノ
# 问答任务已完成 [✓]
# ☆ *　. 　☆ ✨ 传送门 ➤https://github.com/xiaozhuABCD1234/AutoAnswer_zhihuishu
# 　　. ∧＿∧　∩　* ☆ 主人记得给仓库加个星星哦～⭐
# * ☆ ( ・∀・)/ .
# 　. ⊂　　 ノ* ☆
# ☆ * (つ ノ .☆
# 　　 (ノ
# """
# )
