#!/usr/bin/env python3
"""Скрипт для загрузки датасета"""

import urllib.request
import os

url = "https://github.com/mirea-aie-2025/aie-course-meta/raw/main/seminars/S05/S05-hw-dataset.csv"
output_file = "data.csv"

if not os.path.exists(output_file):
    print(f"Загружаем датасет с {url}...")
    urllib.request.urlretrieve(url, output_file)
    print(f"Датасет сохранен в {output_file}")
else:
    print(f"Датасет уже существует: {output_file}")
