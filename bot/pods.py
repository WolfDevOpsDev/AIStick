import runpod
import os
import time

# Ініціалізація API ключа
API_KEY = 'FWVJ9NYD1HNXFUJAU4VGY8TYRGKLGA0L5F9Y1PZR'
HF_TOKEN = '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'  # Введіть ваш токен Hugging Face
runpod.api_key = API_KEY

# Шлях до папки з фото
IMAGES_FOLDER = 'user_photo'

# Конфігурація моделі для навчання
MODEL_NAME = 'flux-1-dev-lora-training'
GPU_TYPE = 'A100'  # Приклад типу GPU, змініть при необхідності
GPU_COUNT = 1


# Функція для завантаження зображень на Runpod
def upload_images(folder_path):
    uploaded_files = []
    image_files = [file for file in os.listdir(folder_path) if file.endswith(('.jpg', '.png'))]

    for image in image_files:
        file_path = os.path.join(folder_path, image)
        file_id = runpod.upload_file(file_path)
        if file_id:
            uploaded_files.append(file_id)
            print(f"Зображення {image} завантажено з ID: {file_id}")
        else:
            print(f"Не вдалося завантажити {image}")

    return uploaded_files


# Завантаження зображень
uploaded_image_ids = upload_images(IMAGES_FOLDER)

# Перевірка наявності завантажених файлів
if not uploaded_image_ids:
    print("Зображення не були завантажені.")
    exit()

# Створення інстанції для запуску навчання
instance = runpod.create_instance(
    model=MODEL_NAME,
    gpu_type=GPU_TYPE,
    gpu_count=GPU_COUNT,
    input_params={
        'image_ids': uploaded_image_ids,
        'templates': {
            'HF_TOKEN': HF_TOKEN  # Передача токену Hugging Face в шаблон
        }
    }
)

# Перевірка чи інстанція створена успішно
if not instance:
    print("Не вдалося створити інстанцію.")
    exit()

print(f"Запущено навчання на інстанції з ID: {instance['id']}")

# Очікування завершення навчання
print("Очікування завершення навчання...")
while True:
    instance_status = runpod.get_instance_status(instance['id'])
    if instance_status['status'] == 'COMPLETED':
        print("Навчання завершено успішно.")
        break
    elif instance_status['status'] == 'FAILED':
        print("Навчання завершилося з помилкою.")
        exit()
    else:
        print(f"Статус: {instance_status['status']}. Очікування...")
        time.sleep(30)  # Чекати 30 секунд перед наступною перевіркою

# Отримання результатів
results = runpod.get_instance_output(instance['id'])
if results:
    trained_image_url = results['trained_image_url']
    print(f"Отримане зображення після навчання доступне за посиланням: {trained_image_url}")
else:
    print("Не вдалося отримати результати навчання.")
