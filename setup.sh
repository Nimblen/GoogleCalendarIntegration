#!/bin/bash

# Обновление и установка Python 3.9.2
sudo apt update
sudo apt install -y python3.9 python3.9-venv python3.9-dev python3-pip

# Создание виртуального окружения
python3.9 -m venv venv
source venv/bin/activate

# Обновление pip и установка зависимостей
pip install --upgrade pip
pip install -r requirements.txt

echo "Setup completed. To run the project, use: source venv/bin/activate && python main.py"
