from celery import shared_task

from users.models import User
from users.services import send_telegram_message


@shared_task
def send_reminder_message():
    """Отправка напоминания о заполнении дневника в Телеграм пользователей"""

    # Получаем всех пользователей, которые хотят получать напоминания и указали в профиле свой чат в Телеграме
    users_to_remind = User.objects.filter(is_recalled_daily=True, tg_chat_id__isnull=False)

    for user in users_to_remind:
        message = f'Привет от "My note"! День подходит к концу, не забудь записать самые важные моменты в свой дневник!'
        send_telegram_message(user.tg_chat_id, message)


def should_send_reminder(habit, current_date, current_time):
    """Проверяет, нужно ли отправлять напоминание для привычки"""
    # Проверяем точное совпадение по времени
    habit_time_minutes = habit.time.hour * 60 + habit.time.minute
    current_time_minutes = current_time.hour * 60 + current_time.minute

    if habit_time_minutes != current_time_minutes:
        return False  # Если время не совпадает, то не нужно отправлять напоминание

    # Проверяем периодичность (в днях), если время совпадает
    days_since_creation = (current_date - habit.created_at.date()).days  # Количество дней с момента создания привычки

    if days_since_creation % habit.periodicity != 0:
        return False  # Если периодичность не совпадает, то не нужно отправлять напоминание

    return True  # Если время и периодичность совпадают, то нужно отправлять напоминание
