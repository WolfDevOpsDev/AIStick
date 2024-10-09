from flask import Flask, render_template_string, jsonify
import requests

app = Flask(__name__)

API_URL = 'https://app.assist.cam/v1/current/day/cars/?date=2024-10-02'
API_KEY = 'YA7NxysJ'


@app.route('/')
def index():
    # Викликаємо API
    headers = {
        'accept': 'application/json',
        'X-Api-Key': API_KEY
    }

    try:
        response = requests.get(API_URL, headers=headers)
        response.raise_for_status()  # Перевіряємо, чи немає помилок
        data = response.json()
    except requests.exceptions.RequestException as e:
        return f"Error fetching data: {e}"

    # Простіший шаблон без окремого HTML-файлу
    template = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>API Fetch Example</title>
    </head>
    <body>
        <h1>API Response:</h1>
        <pre>{{ data }}</pre>
    </body>
    </html>
    """
    return render_template_string(template, data=data)


if __name__ == '__main__':
    app.run(debug=True)
