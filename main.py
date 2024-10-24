import json
import logging
from auth.gapiworkspace import GAPIWorkspace
from gcalendar.gcalendar import GCalendar
from event.gevent import GEvent

import conf  # Импорт базовой конфигурации логирования

logger = logging.getLogger(__name__)


def load_oauth_credentials():
    """Загрузка данных OAuth из файла client_secret.json"""
    try:
        with open(".env/client_secret.json") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("OAuth credentials file not found.")
        raise


def initialize_gapi():
    """Инициализация авторизации через Google API"""
    IDuserOAuth = load_oauth_credentials()
    credsfile = ".env/creds.json"
    return GAPIWorkspace(IDuserOAuth, filename=credsfile)


def create_calendars(calendar_service):
    """Создание нескольких календарей"""
    cal1_data = {
        "name": "Work Calendar",
        "description": "Calendar for work events",
        "timezone": "GMT+03:00",
    }
    cal2_data = {
        "name": "Personal Calendar",
        "description": "Calendar for personal events",
        "timezone": "GMT+03:00",
    }

    cal1 = calendar_service.create(cal1_data)
    cal2 = calendar_service.create(cal2_data)

    if cal1 and cal2:
        logger.info(f"Successfully created calendars: {cal1['id']}, {cal2['id']}")
        return cal1, cal2
    else:
        logger.error("Failed to create one or more calendars")
        raise Exception("Calendar creation failed")


def select_and_edit_calendar(calendar_service, calendar_name):
    """Выбор календаря по имени и его редактирование"""
    selected_calendar = calendar_service.select({"name": calendar_name})
    if selected_calendar:
        logger.info(f"Selected calendar: {selected_calendar['id']}")
    else:
        logger.error(f"Calendar {calendar_name} not found")
        raise Exception("Calendar not found")

    # Редактирование выбранного календаря
    updated_data = {
        "name": "Updated " + calendar_name,
        "description": f"Updated description for {calendar_name}",
        "timezone": "GMT+02:00",
    }
    updated_calendar = calendar_service.edit(selected_calendar["id"], updated_data)
    if updated_calendar:
        logger.info(f"Successfully updated calendar: {updated_calendar['id']}")
        return updated_calendar
    else:
        logger.error(f"Failed to update calendar: {selected_calendar['id']}")
        raise Exception("Calendar update failed")


def create_and_edit_event(calendar_service, calendar_id):
    """Создание и редактирование события в календаре"""
    event_service = GEvent(calendar_service)

    # Создание события
    event_data = {
        "name": "Team Meeting",
        "description": "Discuss project progress",
        "start_time": "2024-10-25T09:00:00+03:00",
        "end_time": "2024-10-25T10:00:00+03:00",
        "alarm": [{"type": "popup", "time": "10"}],  # Напоминание за 10 минут
    }
    created_event = event_service.create(calendar_id, event_data)
    if created_event:
        logger.info(f"Successfully created event: {created_event['id']}")
    else:
        logger.error("Failed to create event")
        raise Exception("Event creation failed")

    # Редактирование события
    updated_event_data = {
        "name": "Updated Team Meeting",
        "description": "Updated discussion points for the project",
        "alarm": [{"type": "popup", "time": "15"}],  # Обновляем напоминание за 15 минут
    }
    updated_event = event_service.edit(
        calendar_id, created_event["id"], updated_event_data
    )
    if updated_event:
        logger.info(f"Successfully updated event: {updated_event['id']}")
        return updated_event
    else:
        logger.error(f"Failed to update event: {created_event['id']}")
        raise Exception("Event update failed")


def delete_calendars(calendar_service, calendars):
    """Удаление нескольких календарей"""
    for calendar in calendars:
        if calendar_service.delete(calendar["id"]):
            logger.info(f"Successfully deleted calendar: {calendar['id']}")
        else:
            logger.error(f"Failed to delete calendar: {calendar['id']}")
            raise Exception(f"Failed to delete calendar {calendar['id']}")


def main():
    """Основная логика программы"""
    try:
        # Инициализация Google API
        gapi_workspace = initialize_gapi()
        calendar_service = GCalendar(gapi_workspace)

        # Шаг 1: Создание нескольких календарей
        cal1, cal2 = create_calendars(calendar_service)

        # Шаг 2: Выбор и редактирование календаря
        updated_calendar = select_and_edit_calendar(calendar_service, "Work Calendar")

        # Шаг 3: Создание и редактирование события
        updated_event = create_and_edit_event(calendar_service, updated_calendar["id"])

        # Шаг 4: Удаление всех календарей
        delete_calendars(calendar_service, [cal1, cal2])

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
