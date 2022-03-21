from enum import Enum
from typing import Optional, List, Tuple

from pydantic import BaseModel


class SocItemDesc(BaseModel):
    id: Optional[str]
    text: str
    label: Optional[str]


class SocModel(BaseModel):
    id: str
    name: str
    full_name: Optional[str]
    desc: List[SocItemDesc] = []

    def __hash__(self):
        return hash(self.id)

    def get_full_name(self):
        return self.full_name or self.name


class SocType(SocModel):
    alias: str
    mbti: str
    model: List[str]

    def get_full_name(self):
        return f'{super().get_full_name()} ({self.alias}, {self.mbti})'


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
    emoji: Optional[str]


class SocDichotomyValue(Enum):
    sensor = 'сенсор'
    intuit = 'интуит'
    logic = 'логик'
    etic = 'этик'
    rac = 'рац'
    irrac = 'иррац'
    exter = 'экстер'
    inter = 'интер'


class SocDichotomyName(Enum):
    IS = 'интуит-сенсор'
    LE = 'логик-этик'
    RI = 'рац-иррац'
    IE = 'интер-экстер'


class SocDichotomy(SocModel):
    pass
