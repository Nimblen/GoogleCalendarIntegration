import os
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from typing import Optional, Dict

# Настройка логирования
logger = logging.getLogger(__name__)


class GAPIWorkspace:
    def __init__(self, IDuserOAuth: Dict, filename: Optional[str] = None):
        """Авторизация через Google API с использованием OAuth."""
        self.creds: Optional[Credentials] = None
        self.filename: Optional[str] = filename

        logger.info("Initializing GAPIWorkspace")

        # Если файл с токенами существует, загружаем токены
        if filename and os.path.exists(filename):
            self.creds = Credentials.from_authorized_user_file(filename)
            logger.info("Loaded credentials from file")

        # Если токены недействительны или их нет, запускаем процесс авторизации
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                logger.info("Token expired, refreshing")
                self.creds.refresh(Request())
            else:
                logger.info("No valid credentials found, starting OAuth flow")
                flow = InstalledAppFlow.from_client_config(
                    IDuserOAuth, ["https://www.googleapis.com/auth/calendar"]
                )
                self.creds = flow.run_local_server(port=8000)

            # Сохраняем токены, если файл указан
            if filename:
                with open(filename, "w") as token_file:
                    token_file.write(self.creds.to_json())
                    logger.info(f"Saved credentials to {filename}")

    def get_credentials(self) -> Optional[Credentials]:
        """Возвращает авторизационные данные."""
        logger.info("Returning credentials")
        return self.creds
