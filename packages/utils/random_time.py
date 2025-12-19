import random
import time

def get_random(n: int) -> int:
    random.seed(time.time())
    return random.randint(int(n / 2), int(n * 1.5))