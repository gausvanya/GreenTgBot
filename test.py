import requests
from bs4 import BeautifulSoup

def get_service_status(service_name):
    # Замените ссылку на нужную вам страницу Downdetector
    url = f"https://downdetector.com/status/{service_name}/"

    # Заголовки, имитирующие браузер
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Проверка на наличие ошибок

        # Парсим HTML
        soup = BeautifulSoup(response.text, 'html.parser')

        # Ищем статус сервиса
        status_section = soup.find('div', class_='status')  # Убедитесь, что этот селектор верный
        if status_section:
            status = status_section.get_text(strip=True)
            return f"Статус сервиса {service_name}: {status}"
        else:
            return "Не удалось найти информацию о статусе сервиса."

    except requests.exceptions.RequestException as e:
        return f"Произошла ошибка: {e}"

if __name__ == "__main__":
    service_name = "telegram"  # Здесь можно указать нужный сервис (например, 'telegram', 'facebook' и т.д.)
    status = get_service_status(service_name)
    print(status)