from typing import Optional, List, Tuple

from aiogram.types import InlineKeyboardButton, Message, InlineKeyboardMarkup, CallbackQuery
from pydantic import BaseModel

from socionbot.utils import generate_callback_data, batcher, back_to


class SocItemDesc(BaseModel):
    text: str
    label: Optional[str]


class SocModel(BaseModel):
    id: str
    name: str
    full_name: Optional[str]
    desc: List[SocItemDesc] = []

    def get_full_name(self):
        return self.full_name or self.name


class SocType(SocModel):
    alias: Optional[str]
    model: List[str]


class SocRelation(SocModel):
    overlay: Tuple[int, int]


class SocFunc(SocModel):
    num: int
    dims: int


class SocAspect(SocModel):
    """
    ЧЭ - черная этика
    БИ - белая интуиция
    """
    abbr: str


class SocDichotomy(SocModel):
    pass

