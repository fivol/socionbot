import json
from typing import Dict, Tuple

from socionbot.theory_models import *


THEORY_PATH = 'socionbot/theory'


class ModelA:
    def __init__(self):
        self._aspects: List[Optional[str]] = [None for _ in range(8)]

    def set_aspect(self, num: int, aspect: str):
        self._aspects[num - 1] = aspect

    def get_aspect(self, num: int) -> Optional[str]:
        return self._aspects[num - 1]

    def __setitem__(self, key: int, value: str):
        self.set_aspect(key, value)

    def __getitem__(self, key: int):
        return self.get_aspect(key)

    def where(self, aspect: str):
        return self._aspects.index(aspect) + 1

    @classmethod
    def emoji_by_aspect(cls, aspect):
        _emoji_by_aspect = {
            'БИ': '△',
            'ЧИ': '▲',
            'БС': '○',
            'ЧС': '●',
            'БЭ': '○',
            'ЧЭ': '',
            'БЛ': '○',
            'ЧЛ': '○',
        }
        return _emoji_by_aspect[aspect]

    def __str__(self):
        text = ''
        text += f'|{self[1]} {self[2]}|\n'
        text += f'|{self[4]} {self[3]}|\n'
        text += f'|{self[6]} {self[5]}|\n'
        text += f'|{self[7]} {self[8]}|'
        return text


class SocTheoryFileAdapter:
    def __init__(self, file_name: str, model: type(SocModel)):
        self.file_name = file_name
        self.model: type(SocModel) = model
        self.items: Dict[str, model] = self.parse_file()

    def parse_file(self):
        items = {}
        file_items = self.read_file(self.file_name)
        for item in file_items:
            items[item['id']] = self.model.parse_obj(item)
        assert len(file_items) == len(items), 'Have repeat "id" in the same file'
        return items

    @classmethod
    def read_file(cls, file_name: str):
        with open(f'{THEORY_PATH}/{file_name}.json', 'r') as f:
            return json.loads(f.read())

    def get_by_id(self, name: str) -> SocModel:
        return self.items[name]

    def get_all_items(self) -> List[SocModel]:
        return list(self.items.values())


class SocEngine:
    def __init__(self):
        self.types = SocTheoryFileAdapter('types', SocType)
        self.functions = SocTheoryFileAdapter('functions', SocFunc)
        self.relations = SocTheoryFileAdapter('relations', SocRelation)
        self.aspects = SocTheoryFileAdapter('aspects', SocAspect)
        self.dichotomies = SocTheoryFileAdapter('dichotomies', SocDichotomy)
        self.theory_items = {
            'type': self.types,
            'aspect': self.aspects,
            'relation': self.relations,
            'func': self.functions,
            'dichotomy': self.dichotomies
        }
        self._relation_by_overlay: Dict[Tuple[int, int], SocRelation] = {}
        self._calculate_relation_by_overlay_map()

    def _calculate_relation_by_overlay_map(self):
        for relation in self.get_all('relation'):
            self._relation_by_overlay[relation.overlay] = relation

    @classmethod
    def _invert_aspect(cls, aspect: str):
        extra_intra_dict = {
            'Б': 'Ч',
            'Ч': 'Б'
        }
        return extra_intra_dict[aspect[0]] + aspect[1]

    @classmethod
    def _paired_aspect(cls, aspect: str):
        paired_aspect = {
            'Л': 'Э',
            'Э': 'Л',
            'С': 'И',
            'И': 'С',
        }
        return aspect[0] + paired_aspect[aspect[1]]

    @classmethod
    def model_by_aspects(cls, first: str, second: str) -> ModelA:
        model = ModelA()
        model[1] = first
        model[2] = second
        model[3] = cls._paired_aspect(first)
        model[4] = cls._paired_aspect(second)
        model[5] = cls._invert_aspect(model[3])
        model[6] = cls._invert_aspect(model[4])
        model[7] = cls._invert_aspect(first)
        model[8] = cls._invert_aspect(second)
        return model

    def get_all(self, model_name: str):
        return self.theory_items[model_name].get_all_items()

    def get_item(self, model_name: str, item_id: str):
        return self.theory_items[model_name].get_by_id(item_id)

    def get_relation_by_types(self, first: SocType, second: SocType) -> SocRelation:
        first_a = self.model_by_aspects(*first.model)
        second_a = self.model_by_aspects(*second.model)
        overlay = (
            second_a.where(first_a[1]),
            second_a.where(first_a[2])
        )
        return self._relation_by_overlay[overlay]

    def get_type(self, type_id):
        return self.get_item('type', type_id)

    def get_all_types(self):
        return self.get_all('type')


soc_engine = SocEngine()
