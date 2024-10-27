import logging
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
logger = logging.getLogger(__name__)


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
            # Предоставляем полный доступ каждому email из списка 'share'
            share_emails = data.get("share", [])
            share_role = data.get("shareRole", "owner")
            for email in share_emails:
                self.share(calendar_entry["id"], email, share_role)
            self.data = calendar_entry
            logger.info(f"Calendar {calendar_entry['id']} successfully created")
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
            updated_calendar = (
                self.service.calendars()
                .update(calendarId=calendar_id, body=calendar)
                .execute()
            )
            share_role = data.get("shareRole", "owner")
            share_emails = data.get("share", [])
            for email in share_emails:
                self.share(updated_calendar["id"], email, share_role)
            self.data = updated_calendar
            logger.info(f"Calendar {calendar_id} successfully updated")
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
