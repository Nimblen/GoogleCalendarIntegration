import logging

logger = logging.getLogger(__name__)


class GEvent:
    def __init__(self, gcalendar):
        """Инициализация работы с событиями в Google Calendar."""
        self.service = gcalendar.service
        self.data = None
        self.error = None
        logger.info("GEvent initialized")

    def create(self, calendar_id: str, event_data: dict):
        """Создание нового события."""
        try:
            logger.info(f"Creating event: {event_data.get('name', 'New Event')}")
            event = {
                "summary": event_data.get("name", "New Event"),
                "description": event_data.get("description", ""),
                "start": {
                    "dateTime": event_data.get("start_time"),
                    "timeZone": event_data.get("timezone", "GMT+02:00"),
                },
                "end": {
                    "dateTime": event_data.get("end_time"),
                    "timeZone": event_data.get("timezone", "GMT+02:00"),
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": alarm["type"], "minutes": int(alarm["time"])}
                        for alarm in event_data.get("alarm", [])
                    ],
                },
            }
            event_entry = (
                self.service.events()
                .insert(calendarId=calendar_id, body=event)
                .execute()
            )
            self.data = event_entry
            logger.info(f"Event {event_entry['id']} successfully created")
            return event_entry  # Возвращаем объект события
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error creating event: {e}")
            return False

    def delete(self, calendar_id: str, event_id: str):
        """Удаление события по ID."""
        try:
            logger.info(
                f"Deleting event with id: {event_id} from calendar {calendar_id}"
            )
            self.service.events().delete(
                calendarId=calendar_id, eventId=event_id
            ).execute()
            self.data = None
            logger.info(f"Event {event_id} successfully deleted")
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error deleting event {event_id}: {e}")
            return False

    def select(self, calendar_id: str, data: dict):
        """Поиск события по имени."""
        try:
            logger.info(f"Selecting event by name: {data.get('name')}")
            events = self.service.events().list(calendarId=calendar_id).execute()
            for event in events["items"]:
                if data.get("name") in event["summary"]:
                    self.data = event
                    logger.info(f"Event {event['id']} selected")
                    return event.get("id", False)
            logger.warning(f"Event with name {data.get('name')} not found")
            return False
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error selecting event: {e}")
            return False

    def edit(self, calendar_id: str, event_id: str, event_data: dict):
        """Редактирование события."""
        try:
            logger.info(f"Editing event with id: {event_id}")
            event = (
                self.service.events()
                .get(calendarId=calendar_id, eventId=event_id)
                .execute()
            )
            event["summary"] = event_data.get("name", event["summary"])
            event["description"] = event_data.get(
                "description", event.get("description", "")
            )
            updated_event = (
                self.service.events()
                .update(calendarId=calendar_id, eventId=event_id, body=event)
                .execute()
            )
            self.data = updated_event
            logger.info(f"Event {event_id} successfully updated")
            return updated_event
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error editing event {event_id}: {e}")
            return False
