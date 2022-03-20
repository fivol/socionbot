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

    def in_two_first(self, aspect: str):
        return self[0] == aspect or self[1] == aspect

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


def read_file(file_name: str):
    with open(f'{THEORY_PATH}/{file_name}.json', 'r') as f:
        return json.loads(f.read())


class SocTheoryFileAdapter:
    def __init__(self, file_name: str, model: type(SocModel)):
        self.file_name = file_name
        self.model: type(SocModel) = model
        self.items: Dict[str, model] = self.parse_file()

    def parse_file(self):
        items = {}
        file_items = read_file(self.file_name)
        for item in file_items:
            items[item['id']] = self.model.parse_obj(item)
        assert len(file_items) == len(items), 'Have repeat "id" in the same file'
        return items

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
        self.quadras = SocTheoryFileAdapter('quadras', SocDichotomy)
        self.desc_file = read_file('desc')
        self._desc_settings = self._read_desc_settings()
        self.theory_items = {
            'type': self.types,
            'aspect': self.aspects,
            'relation': self.relations,
            'func': self.functions,
            'dichotomy': self.dichotomies,
            'quad': self.quadras
        }
        self._relation_by_overlay: Dict[Tuple[int, int], SocRelation] = {}
        self._calculate_relation_by_overlay_map()

    @classmethod
    def _read_desc_settings(cls) -> Dict[str, dict]:
        return {
            item['id']: item for item in read_file('desc_settings')
        }

    def get_soc_model_desc(self, model: SocModel, desc_idx: int) -> SocItemDesc:
        desc_item = model.desc[desc_idx]
        template = self._desc_settings.get(desc_item.id)
        if template:
            if 'label' in template and not desc_item.label:
                desc_item.label = template['label']

        return desc_item

    def get_soc_model_desc_list(self, model: SocModel) -> List[SocItemDesc]:
        items = []
        for i, desc_item in enumerate(model.desc):
            items.append(self.get_soc_model_desc(model, i))
        return items

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

    @classmethod
    def model_by_type(cls, soc_type: SocType):
        return cls.model_by_aspects(*soc_type.model)

    def get_all(self, model_name: str):
        return self.theory_items[model_name].get_all_items()

    def get_all_dichotomies(self) -> List[SocDichotomy]:
        return self.get_all('dichotomy')

    def get_item(self, model_name: str, item_id: str) -> SocModel:
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

    def get_all_types(self) -> List[SocType]:
        return self.get_all('type')

    def get_desc(self, name: str) -> str:
        return self.desc_file[name]

    @classmethod
    def get_dichotomy_value(cls, model: ModelA, dichotomy: SocDichotomyName):
        if dichotomy == SocDichotomyName.IS:
            if model.in_two_first('БС') or model.in_two_first('ЧС'):
                return SocDichotomyValue.sensor
            return SocDichotomyValue.intuit
        if dichotomy == SocDichotomyName.IE:
            if model[1][0] == 'Ч':
                return SocDichotomyValue.exter
            return SocDichotomyValue.inter
        if dichotomy == SocDichotomyName.RI:
            if model[1][1] in 'ИС':
                return SocDichotomyValue.irrac
            return SocDichotomyValue.rac
        if dichotomy == SocDichotomyName.LE:
            if model.in_two_first('БЛ') or model.in_two_first('ЧЛ'):
                return SocDichotomyValue.logic
            return SocDichotomyValue.etic
        raise ValueError

    def get_type_by_dichotomies(self, d_list: List[SocDichotomyValue]) -> SocType:
        for soc_type in self.get_all_types():
            model_a = self.model_by_type(soc_type)
            skip = False
            for dichotomy in SocDichotomyName:
                value = self.get_dichotomy_value(model_a, dichotomy)
                if value not in d_list:
                    skip = True
                    break
            if skip:
                continue
            return soc_type


soc_engine = SocEngine()
