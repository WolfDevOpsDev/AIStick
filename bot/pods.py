import requests
import os
import base64
import time

# Ініціалізація змінних
API_KEY = 'FWVJ9NYD1HNXFUJAU4VGY8TYRGKLGA0L5F9Y1PZR'
HEADERS = {
    'Authorization': f'Bearer {API_KEY}'
}
IMAGES_FOLDER = 'user_photo'
MODEL_NAME = 'flux-1-dev-lora-training'
GPU_TYPE = 'A100'
GPU_COUNT = 1

# Функція для кодування зображень у base64
def encode_images_as_base64(folder_path):
    encoded_files = {}
    image_files = [file for file in os.listdir(folder_path) if file.endswith(('.jpg', '.png'))]

    for image in image_files:
        file_path = os.path.join(folder_path, image)
        with open(file_path, 'rb') as f:
            encoded_content = base64.b64encode(f.read()).decode('utf-8')
            encoded_files[image] = encoded_content

    return encoded_files

# Кодування зображень
encoded_images = encode_images_as_base64(IMAGES_FOLDER)

# Створення інстанції з використанням закодованих зображень
def create_instance_with_encoded_images():
    instance_creation_url = "https://api.runpod.ai/v2/504mwzo4qlzqiz/run"  # Використання правильного ендпоінту
    payload = {
        "model": MODEL_NAME,
        "gpu_type": GPU_TYPE,
        "gpu_count": GPU_COUNT,
        "input_params": {
            "images": encoded_images  # Передача закодованих зображень у запиті
        }
    }
    response = requests.post(instance_creation_url, json=payload, headers=HEADERS)
    if response.status_code == 200:
        instance = response.json()
        return instance
    else:
        print(f"Не вдалося створити інстанцію: {response.status_code} {response.text}")
        return None

# Спроба створити інстанцію
instance = create_instance_with_encoded_images()

# Перевірка чи інстанція створена успішно
if not instance:
    print("Не вдалося створити інстанцію.")
    exit()

print(f"Запущено навчання на інстанції з ID: {instance['id']}")

# Очікування завершення навчання
print("Очікування завершення навчання...")
while True:
    instance_status_url = f"https://api.runpod.ai/v2/504mwzo4qlzqiz/status/{instance['id']}"
    status_response = requests.get(instance_status_url, headers=HEADERS)
    if status_response.status_code == 200:
        status_data = status_response.json()
        if status_data['status'] == 'COMPLETED':
            print("Навчання завершено успішно.")
            break
        elif status_data['status'] == 'FAILED':
            print("Навчання завершилося з помилкою.")
            exit()
        else:
            print(f"Статус: {status_data['status']}. Очікування...")
            time.sleep(30)
    else:
        print(f"Не вдалося отримати статус: {status_response.status_code} {status_response.text}")
        time.sleep(30)
