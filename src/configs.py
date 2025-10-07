import yaml
from src.logger import Logger
import sys


class Config:
    def __init__(self):
        self.login_url = "https://passport.zhihuishu.com/login"
        config = self.loading_config()
        if not config:
            Logger().error("配置加载失败，程序无法继续运行。")
            sys.exit(1)  # 退出程序

        # 验证配置结构
        self._validate_config(config)

        self.username: str = str(config["user"]["name"])
        self.password: str = str(config["user"]["password"])
        self.driver: str = str(config["option"]["driver"])
        self.browser_path: str | None = str(config["option"].get("browser_path", None))
        self.delay_time_s: int = int(config["option"]["delay_time_s"])
        self.enabled_random_time: bool = config["option"]["enabled_random_time"]
        self.question_classification: int = int(
            config["option"]["question_classification"]
        )

        self.courses: list = config["question-urls"]

        # 添加 OpenAI 配置
        self.openai_base_url: str = config["OpenAI"]["base_url"]
        self.openai_api_key: str = config["OpenAI"]["api_key"]
        self.openai_model: str = config["OpenAI"]["model"]
        self.max_tokens: int = int(config["OpenAI"]["max_tokens"])
        self.temperature: float = float(config["OpenAI"]["temperature"])

    def loading_config(self) -> dict | None:
        try:
            with open("configs.yaml", "r", encoding="utf-8") as f:
                data = yaml.load(f, Loader=yaml.FullLoader)
                if not data:
                    Logger().error("YAML 文件为空或格式不正确。")
                    return None
                Logger().info("配置文件成功读取。")
                return data
        except FileNotFoundError:
            Logger().error("文件未找到，请检查路径是否正确。")
        except yaml.YAMLError as e:
            Logger().error(f"解析 YAML 文件时出错: {str(e)}")
        return None

    def _validate_config(self, config: dict):
        """配置验证"""
        required_keys = ["user", "option", "question-urls", "OpenAI"]
        for key in required_keys:
            if key not in config:
                raise ValueError(f"配置文件缺少必需的字段: {key}")

        user_keys = ["name", "password"]
        for key in user_keys:
            if key not in config["user"]:
                raise ValueError(f"用户配置缺少必需的字段: {key}")

        option_keys = ["driver"]
        for key in option_keys:
            if key not in config["option"]:
                raise ValueError(f"选项配置缺少必需的字段: {key}")

        openai_keys = ["base_url", "api_key", "model"]
        for key in openai_keys:
            if key not in config["OpenAI"]:
                raise ValueError(f"OpenAI 配置缺少必需的字段: {key}")

        if not isinstance(config["question-urls"], list):
            raise TypeError("question-urls 必须是列表类型")

        Logger().info("配置验证通过")


if __name__ == "__main__":
    config = Config()
