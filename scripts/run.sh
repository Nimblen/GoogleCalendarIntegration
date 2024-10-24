#!/bin/bash



# Запуск скрипта установки зависимостей
chmod +x scripts/setup.sh
./scripts/setup.sh

# Запуск основного файла
python main.py
