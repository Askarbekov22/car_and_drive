from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message

from services.access_service import (
    can_open_section,
    get_user_role,
    ROLE_MANAGER
)


SECTION_BUTTONS = {
    "🚗 Машины": "cars",
    "👤 Водители": "drivers",
    "🔄 Смена": "shifts",
    "🚨 ДТП": "accidents",
    "📊 Отчёты": "reports",
}


REPORT_BUTTONS = [
    "📅 Сегодня",
    "📅 Вчера",
    "📅 Текущая неделя",
    "📅 Текущий месяц",
    "📊 Скачать Excel",
    "🔄 Актуальные смены",
    "🧾 Последние смены",
]


class AccessMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[
            [Message, Dict[str, Any]],
            Awaitable[Any]
        ],
        event: Message,
        data: Dict[str, Any]
    ):

        if not event.from_user:
            return await handler(event, data)

        text = event.text

        if not text:
            return await handler(event, data)

        user_id = event.from_user.id

        if text in SECTION_BUTTONS:

            section = SECTION_BUTTONS[text]

            if not can_open_section(
                user_id,
                section
            ):

                await event.answer(
                    "⛔ У вас нет доступа к этому разделу."
                )

                return

        role = get_user_role(user_id)

        if role == ROLE_MANAGER:

            if text in REPORT_BUTTONS:

                if text != "📅 Сегодня":

                    await event.answer(
                        "⛔ Менеджеру доступен только сегодняшний отчет."
                    )

                    return

        return await handler(event, data)