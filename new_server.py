from flask import Flask
import concurrent.futures
import json
import requests
import time
import threading

app = Flask(__name__)
mutex = threading.RLock()

# === Твои контроллеры (не меняй) ===
LETTERS_PARAMS = {

    'FL': {'url': 'http://192.168.0.106'},
    'FR': {'url': 'http://192.168.0.101'},
    'P':  {'url': 'http://192.168.0.109'},
    'ML': {'url': 'http://192.168.0.107'},
    'MR': {'url': 'http://192.168.0.108'},
    'I':  {'url': 'http://192.168.0.104'}
}

ENABLE_PRESET_REQUEST = {
    "on": True,
    "udpn": {"send": True, "recv": True},
    "ps": 0
}

DISABLE_REQUEST = {"on": False}

# ===================================================================
# НОВАЯ УНИВЕРСАЛЬНАЯ ФУНКЦИЯ — отправляет команду на все контроллеры
# ===================================================================
def send_to_all(request_template):
    def send_to_one(url, req):
        response = requests.post(f"{url}/json/state", json=req, timeout=2)
        if response.status_code != 200:
            print(f"Ошибка на {url}: {response.status_code}")

    with mutex:
        start = time.time()
        with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
            futures = [
                executor.submit(send_to_one, params['url'], request_template.copy())
                for params in LETTERS_PARAMS.values()
            ]
            concurrent.futures.wait(futures)
        print(f"Команда выполнена за {time.time() - start:.3f} сек")

# ===================================================================
# НОВЫЕ РУЧКИ (то, что ты просил)
# ===================================================================
@app.route('/all/preset/<int:preset_id>')
def all_preset(preset_id):
    print(f"Включаем Preset {preset_id} на ВСЕХ сегментах")
    req = ENABLE_PRESET_REQUEST.copy()
    req["ps"] = preset_id
    send_to_all(req)
    return f"Preset {preset_id} включён на всех контроллерах!"

@app.route('/all/off')
def all_off():
    print("Выключаем ВСЁ")
    send_to_all(DISABLE_REQUEST)
    return "Все сегменты выключены!"

# ===================================================================
# Старые ручки (оставляем как были)
# ===================================================================
@app.route('/flag/<group_id>')
def enable_flag(group_id):
    # ... (твой оригинальный код остаётся без изменений)
    # (я не стал его копировать, чтобы не раздувать — он уже работает)
    pass  # ← здесь твой старый код /flag

# (все остальные старые роуты /idle, /init, /concerts/... тоже остаются)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1337, debug=False)   # порт как в твоём оригинале