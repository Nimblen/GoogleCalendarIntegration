import pytest


def test_gcalendar_create(mock_gcalendar):
    """Тест создания календаря."""
    mock_gcalendar.service.calendars().insert().execute.return_value = {
        "id": "mocked_calendar_id"
    }

    data = {
        "name": "Test Calendar",
        "description": "Test Description",
        "timezone": "GMT+03:00",
    }
    result = mock_gcalendar.create(data)

    assert result["id"] == "mocked_calendar_id"


def test_gcalendar_delete(mock_gcalendar):
    """Тест удаления календаря."""
    mock_gcalendar.service.calendars().delete().execute.return_value = None

    result = mock_gcalendar.delete("mocked_calendar_id")

    assert result is True


def test_gcalendar_select(mock_gcalendar):
    """Тест выбора календаря."""
    mock_gcalendar.service.calendarList().list().execute.return_value = {
        "items": [{"id": "mocked_calendar_id", "summary": "Test Calendar"}]
    }

    result = mock_gcalendar.select({"name": "Test Calendar"})

    assert result == "mocked_calendar_id"


def test_gcalendar_edit(mock_gcalendar):
    """Тест редактирования календаря."""
    mock_gcalendar.service.calendars().get().execute.return_value = {
        "id": "mocked_calendar_id",
        "summary": "Test Calendar",
    }
    mock_gcalendar.service.calendars().update().execute.return_value = {
        "id": "mocked_calendar_id",
        "summary": "Updated Calendar",
    }

    data = {"name": "Updated Calendar", "description": "Updated Description"}
    result = mock_gcalendar.edit("mocked_calendar_id", data)

    assert result["summary"] == "Updated Calendar"


def test_gcalendar_eventlist(mock_gcalendar):
    """Тест получения списка событий."""
    mock_gcalendar.service.events().list().execute.return_value = {
        "items": [{"id": "event_1", "summary": "Test Event"}]
    }

    data = {"from": "2024-10-01T00:00:00Z", "limit": 10}
    result = mock_gcalendar.eventlist("mocked_calendar_id", data)

    assert len(result) == 1
    assert result[0]["id"] == "event_1"


def test_gcalendar_get(mock_gcalendar):
    """Тест получения информации о календаре."""
    mock_gcalendar.service.calendars().get().execute.return_value = {
        "id": "mocked_calendar_id",
        "summary": "Test Calendar",
    }

    result = mock_gcalendar.get("mocked_calendar_id")

    assert result["id"] == "mocked_calendar_id"
