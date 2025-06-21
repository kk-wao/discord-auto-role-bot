import subprocess
import time
import datetime
import requests

LOG_FILE = "watchdog_log.txt"
BOT_COMMAND = ["python3", "main.py"]
CHECK_URL = "http://localhost:8080"
CHECK_INTERVAL = 60  # 秒ごとに監視
RESTART_DELAY = 5

def log(msg):
    now = datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{now} {msg}\n")
    print(f"{now} {msg}")

def flask_alive():
    try:
        res = requests.head(CHECK_URL, timeout=5)
        return res.status_code == 200
    except Exception as e:
        log(f"Flask応答失敗: {e}")
        return False

while True:
    log("Botプロセスを起動します。")
    try:
        proc = subprocess.Popen(BOT_COMMAND)

        # 監視ループ
        while True:
            time.sleep(CHECK_INTERVAL)
            if proc.poll() is not None:
                log(f"Botが予期せず終了しました（exit code: {proc.returncode}）")
                break
            if not flask_alive():
                log("Flaskが応答していません。Botを強制再起動します。")
                proc.terminate()
                proc.wait(timeout=10)
                break
    except Exception as e:
        log(f"例外発生: {e}")

    log(f"{RESTART_DELAY}秒待機後に再起動します。")
    time.sleep(RESTART_DELAY)


