from time import sleep


def countdown(sleep_time: int = 10, message="") -> None:
    for s in [1] * sleep_time:
        sleep(0.95)
        print(f"\r{message}:{sleep_time-s}秒待機します。", end="")
    return None
