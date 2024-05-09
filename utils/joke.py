import requests
import json
import aiogram

def fetch_joke(retry_count=3):
    url = "http://rzhunemogu.ru/RandJSON.aspx?CType=1"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            clean_content = response.text.replace('\n', '\\n').replace('\r', '\\r')
            try:
                joke_data = json.loads(clean_content)
                return joke_data.get("content", "Шутка не найдена.")
            except json.JSONDecodeError as e:
                if retry_count > 0:
                    print(f"Ошибка декодирования JSON, попытка {3 - retry_count + 1}: {e}")
                    return fetch_joke(retry_count) 
            except aiogram.exceptions.TelegramBadRequest as e:
                print(f"Ошибка слишком большая шутка, попытка {3 - retry_count + 1}: {e}")
                return fetch_joke(retry_count) 
        else:
            return "Не удалось загрузить шутку: HTTP статус " + str(response.status_code)
    except Exception as e:
        return f"Произошла ошибка при запросе: {e}"
