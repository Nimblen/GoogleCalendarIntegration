import logging




# Настройка базового логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    encoding="UTF-8",
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)