import pytest
from unittest.mock import MagicMock
from gcalendar.gcalendar import GCalendar
from event.gevent import GEvent
from google.oauth2.credentials import Credentials


@pytest.fixture
def mock_gcalendar(mocker):
    """Фикстура для создания мок-объекта GCalendar."""
    gapi_workspace = MagicMock()
    
    # Создаем мок-объект Credentials
    mocked_creds = MagicMock(spec=Credentials)
    mocked_creds.valid = True
    mocked_creds.authorize = MagicMock()

    gapi_workspace.get_credentials.return_value = mocked_creds
    
    gcalendar = GCalendar(gapi_workspace)
    gcalendar.service = MagicMock()  # Мокируем сервис API
    return gcalendar


@pytest.fixture
def mock_gevent(mock_gcalendar):
    """Фикстура для создания мок-объекта GEvent."""
    gevent = GEvent(mock_gcalendar)
    gevent.service = MagicMock()  # Мокируем сервис API
    return gevent
