import json
import logging
import os
from typing import Optional, Dict
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    encoding="UTF-8",
    handlers=[logging.FileHandler("app.log"), logging.StreamHandler()],
)


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


class GCalendar:
    def __init__(self, gapi_workspace):
        """Инициализация сервиса Google Calendar."""
        self.service = build(
            "calendar", "v3", credentials=gapi_workspace.get_credentials()
        )
        self.data = None
        self.error = None
        logger.info("GCalendar initialized")

    def create(self, data: dict):
        """Создание нового календаря."""
        try:
            logger.info(f"Creating calendar: {data.get('name', 'New Calendar')}")
            calendar = {
                "summary": data.get("name", "New Calendar"),
                "description": data.get("description", ""),
                "timeZone": data.get("timezone", "GMT+02:00"),
            }
            calendar_entry = self.service.calendars().insert(body=calendar).execute()
            self.data = calendar_entry
            logger.info(f"Calendar {calendar_entry['id']} successfully created")

            # Предоставляем полный доступ каждому email из списка 'share'
            share_emails = data.get("share", [])
            share_role = data.get("role", "owner")
            for email in share_emails:
                self.share(calendar_entry["id"], email, share_role)

            return calendar_entry  # Возвращаем полный объект календаря
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error creating calendar: {e}")
            return False

    def delete(self, calendar_id: str):
        """Удаление календаря по ID."""
        try:
            logger.info(f"Deleting calendar with id: {calendar_id}")
            self.service.calendars().delete(calendarId=calendar_id).execute()
            self.data = None
            logger.info(f"Calendar {calendar_id} successfully deleted")
            return True
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error deleting calendar {calendar_id}: {e}")
            return False

    def select(self, data: dict):
        """Выбор календаря по имени."""
        try:
            logger.info(f"Selecting calendar by name: {data.get('name')}")
            calendars = self.service.calendarList().list().execute()
            for calendar in calendars["items"]:
                if data.get("name") == calendar["summary"]:
                    self.data = calendar
                    logger.info(f"Calendar {calendar['id']} selected")
                    return calendar.get("id", False)
            logger.warning(f"Calendar with name {data.get('name')} not found")
            return False
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error selecting calendar: {e}")
            return False

    def edit(self, calendar_id: str, data: dict):
        """Редактирование календаря."""
        try:
            logger.info(f"Editing calendar with id: {calendar_id}")
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            calendar["summary"] = data.get("name", calendar["summary"])
            calendar["description"] = data.get(
                "description", calendar.get("description", "")
            )
            share_role = data.get("shareRole", "owner")
            updated_calendar = (
                self.service.calendars()
                .update(calendarId=calendar_id, body=calendar)
                .execute()
            )
            self.data = updated_calendar
            logger.info(f"Calendar {calendar_id} successfully updated")

            # Предоставляем полный доступ каждому email из списка 'share'
            share_emails = data.get("share", [])
            for email in share_emails:
                self.share(calendar_id, email, share_role)

            return updated_calendar
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error updating calendar {calendar_id}: {e}")
            return False

    def eventlist(self, calendar_id: str, data: dict):
        """Получение списка событий."""
        try:
            logger.info(f"Retrieving event list for calendar {calendar_id}")
            events_result = (
                self.service.events()
                .list(
                    calendarId=calendar_id,
                    timeMin=data["from"],
                    timeMax=data.get("till", None),
                    maxResults=data.get("limit", 10),
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events = events_result.get("items", [])
            logger.info(f"Found {len(events)} events for calendar {calendar_id}")
            return events
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error retrieving event list for calendar {calendar_id}: {e}")
            return []

    def get(self, calendar_id: str):
        """Получение информации о календаре по ID."""
        try:
            logger.info(f"Retrieving information for calendar {calendar_id}")
            calendar = self.service.calendars().get(calendarId=calendar_id).execute()
            self.data = calendar
            logger.info(
                f"Information for calendar {calendar_id} successfully retrieved"
            )
            return self.data
        except Exception as e:
            self.error = str(e)
            logger.error(
                f"Error retrieving information for calendar {calendar_id}: {e}"
            )
            return False

    def share(self, calendar_id: str, email: str, role: str = "owner"):
        """
        Делится доступом к календарю с указанным email.

        :param calendar_id: ID календаря, которым делятся.
        :param email: Email пользователя, которому предоставляется доступ.
        :param role: Уровень доступа ("reader", "writer", "owner"). По умолчанию "owner".
        """
        try:
            logger.info(f"Sharing calendar {calendar_id} with {email}, role: {role}")
            rule = {
                "scope": {
                    "type": "user",
                    "value": email,
                },
                "role": role,
            }
            
            # Проверка существующего правила для пользователя
            try:
                existing_rule = self.service.acl().get(calendarId=calendar_id, ruleId=f"user:{email}").execute()
                # Обновляем, если уже существует
                existing_rule['role'] = role
                acl_rule = self.service.acl().update(calendarId=calendar_id, ruleId=existing_rule['id'], body=existing_rule).execute()
                logger.info(f"Updated existing ACL rule for {email} on calendar {calendar_id}.")
            except HttpError as e:
                # Добавляем новое правило, если не найдено
                if e.resp.status == 404:  # правило не найдено
                    acl_rule = self.service.acl().insert(calendarId=calendar_id, body=rule).execute()
                    logger.info(f"Inserted new ACL rule for {email} on calendar {calendar_id}.")
                else:
                    raise  # если ошибка не 404, пробрасываем исключение

            return acl_rule
        except Exception as e:
            self.error = str(e)
            logger.error(f"Error sharing calendar {calendar_id} with {email}: {e}")
            return False


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
                "colorId": event_data.get("color", ""),
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


# Использование Google API


def load_oauth_credentials():
    """Загрузка данных OAuth из файла client_secret.json"""
    try:
        with open("./client_secret.json") as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error("OAuth credentials file not found.")
        raise


def initialize_gapi():
    """Инициализация авторизации через Google API"""
    IDuserOAuth = load_oauth_credentials()
    credsfile = "./creds.json"
    return GAPIWorkspace(IDuserOAuth, filename=credsfile)


def create_calendar(calendar_service):
    """Создание календарей"""
    cal1_data = {
        "name": "Calendar 3",
        "description": "Calendar for work events",
        "timezone": "GMT+03:00",
        "share": ["i.see@mail.ru"],
    }
    # cal2_data = {
    #     "name": "Personal Calendar",
    #     "description": "Calendar for personal events",
    #     "timezone": "GMT+03:00",
    # }

    cal1 = calendar_service.create(cal1_data)
    # cal2 = calendar_service.create(cal2_data)

    if cal1:  # and cal2:
        logger.info(f"Successfully created calendars: {cal1['id']}")
        return cal1
    else:
        logger.error("Failed to create one or more calendars")
        raise Exception("Calendar creation failed")


def select_and_edit_calendar(calendar_service, calendar_name):
    """Выбор календаря по имени и его редактирование"""
    selected_calendar = calendar_service.select({"name": calendar_name})
    if selected_calendar:
        logger.info(f"Selected calendar: {selected_calendar}")
    else:
        logger.error(f"Calendar {calendar_name} not found")
        raise Exception("Calendar not found")

    # Редактирование выбранного календаря
    updated_data = {
        "name": "Updated " + calendar_name,
        "description": f"Updated description for {calendar_name}",
        "timezone": "GMT+02:00",
        "share": ["i.see@mail.ru"],
        "shareRole": "reader",
    }
    updated_calendar = calendar_service.edit(selected_calendar, updated_data)
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
        "color": "5",
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
        calendars = (
            calendar_service.service.calendarList().list().execute().get("items")
        )  # получение всех календарей
        logger.info(f"количество календарей: {len(calendars)}")

        # удаление всех календарей, которые можно удалить
        # for calendar in calendars:
        #     if not calendar.get("primary", False) and calendar.get("accessRole") == "owner":
        #         delete_calendars(calendar_service, [calendar])

        #Шаг 1: Создание нескольких календарей
        cal1 = create_calendar(calendar_service)

        # Шаг 2: Выбор и редактирование календаря
        updated_calendar = select_and_edit_calendar(calendar_service, cal1["summary"])

        # # # Шаг 3: Создание и редактирование события
        updated_event = create_and_edit_event(calendar_service, updated_calendar["id"])

        # Шаг 4: Удаление календарей
        delete_calendars(calendar_service, [cal1])

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")


if __name__ == "__main__":
    main()
