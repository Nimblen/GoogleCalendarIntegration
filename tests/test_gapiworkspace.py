import pytest
from unittest.mock import patch, MagicMock
from auth.gapiworkspace import GAPIWorkspace
from google.oauth2.credentials import Credentials

def test_gapiworkspace_creds_from_file(mocker):
    """Тест загрузки токенов из файла."""
    mocker.patch("os.path.exists", return_value=True)
    
    # Создаем мок-объект Credentials
    mocked_creds = MagicMock(spec=Credentials)
    mocked_creds.valid = True

    mocker.patch("google.oauth2.credentials.Credentials.from_authorized_user_file", return_value=mocked_creds)

    gapi = GAPIWorkspace({"mock": "oauth_data"}, filename="mock_creds.json")
    assert gapi.get_credentials() == mocked_creds


def test_gapiworkspace_creds_no_file(mocker):
    """Тест создания нового токена, если файл не существует."""
    mocker.patch("os.path.exists", return_value=False)
    mock_flow = mocker.patch("google_auth_oauthlib.flow.InstalledAppFlow.from_client_config")
    mock_flow.return_value.run_local_server = MagicMock(return_value="new_creds")

    gapi = GAPIWorkspace({"mock": "oauth_data"})
    assert gapi.get_credentials() == "new_creds"
