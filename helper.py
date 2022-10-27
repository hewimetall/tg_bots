from typing import Union
from aiogram.dispatcher.filters.state import State, StatesGroup
from pydantic import BaseModel


class FeedbackForm(BaseModel):
    user_id: str
    username: str = ''
    text: str
    source: str
    media: Union[list[str], None] = []
    link: str

class MenuState(StatesGroup):
    START = State()
    TEXT = State()
    WAIT = State()
    MEDIA = State()
    FINISH = State()
