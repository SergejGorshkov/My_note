from celery import shared_task

from users.models import User
from users.services import send_telegram_message


@shared_task
def send_reminder_message():
    """Отправка напоминания о заполнении дневника в Телеграм пользователей"""

    # Получаем всех пользователей, которые хотят получать напоминания и указали в профиле свой чат в Телеграме
    users_to_remind = User.objects.filter(is_recalled_daily=True, tg_chat_id__isnull=False)

    if not users_to_remind:
        return

    # Отправляем напоминание каждому пользователю
    for user in users_to_remind:
        message = (f'Привет, {user.username}, от "My note"! '
                   f'День подходит к концу, не забудь записать самые важные моменты в свой дневник!'
                   f' http://127.0.0.1:8000/')
        send_telegram_message.delay(user.tg_chat_id, message)  # Отправляем сообщение в Телеграм в асинхронном режиме
