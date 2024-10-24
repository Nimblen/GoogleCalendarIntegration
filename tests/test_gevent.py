import pytest

def test_gevent_create(mock_gevent):
    """Тест создания события."""
    mock_gevent.service.events().insert().execute.return_value = {"id": "mocked_event_id"}
    
    event_data = {
        "name": "Test Event",
        "start_time": "2024-10-25T09:00:00+03:00",
        "end_time": "2024-10-25T10:00:00+03:00",
        "timezone": "GMT+03:00",
        "description": "Discussing project progress",
    }
    result = mock_gevent.create("mocked_calendar_id", event_data)
    
    assert result["id"] == "mocked_event_id"


def test_gevent_delete(mock_gevent):
    """Тест удаления события."""
    mock_gevent.service.events().delete().execute.return_value = None
    
    result = mock_gevent.delete("mocked_calendar_id", "mocked_event_id")
    
    assert result is True


def test_gevent_select(mock_gevent):
    """Тест выбора события."""
    mock_gevent.service.events().list().execute.return_value = {
        "items": [{"id": "mocked_event_id", "summary": "Test Event"}]
    }

    result = mock_gevent.select("mocked_calendar_id", {"name": "Test Event"})
    
    assert result == "mocked_event_id"


def test_gevent_edit(mock_gevent):
    """Тест редактирования события."""
    mock_gevent.service.events().get().execute.return_value = {"id": "mocked_event_id", "summary": "Test Event"}
    mock_gevent.service.events().update().execute.return_value = {"id": "mocked_event_id", "summary": "Updated Event"}

    event_data = {"name": "Updated Event", "description": "Updated Description"}
    result = mock_gevent.edit("mocked_calendar_id", "mocked_event_id", event_data)

    assert result["summary"] == "Updated Event"
