import json
from typing import Dict, Union

from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardButton, CallbackQuery

from socionbot.bot import dp
from socionbot.common import send_desc
from socionbot.soc_engine import soc_engine
from socionbot.theory_models import *
from socionbot.utils import callback, answer, batcher, back_to, generate_callback_data, callback_keys, \
    extract_value_from_callback, read_file

TESTS_PATH = 'socionbot/testing'


class TestAnswer(BaseModel):
    btn: str
    id: str


class TestQuestion(BaseModel):
    text: str
    answers: List[TestAnswer]
    id: str


class TestModel(BaseModel):
    id: str
    name: str
    questions: List[TestQuestion]


class TestManger:
    def __init__(self):
        self._testing_data: List[TestModel] = self.parse_test_file()
        self._tests_by_id: Dict[str, TestModel] = {}
        self._fill_tests_dict()

    def _fill_tests_dict(self):
        for test in self._testing_data:
            self._tests_by_id[test.id] = test

    @classmethod
    def parse_test_file(cls):
        return [TestModel.parse_obj(test) for test in read_file(f'{TESTS_PATH}/testing.json')]

    def get_test_by_id(self, test_id: str) -> TestModel:
        return self._tests_by_id[test_id]

    def get_all_tests(self):
        return self._testing_data


class TesterModeRunner:
    def __init__(self, data: dict):
        self._data = data
        self._questions = read_file(f'{TESTS_PATH}/questions.json')

    def get_questions(self):
        return [item['text'] for item in self._questions]

    def get_current_question(self) -> (str, int, int):
        if self._data.get('question_idx') is None:
            self._data['question_idx'] = 0
        question_idx = self._data['question_idx']
        return self.get_questions()[question_idx], question_idx, len(self.get_questions())

    def next_question(self):
        self._data['question_idx'] = (self._data.get('question_idx', 0) + 1) % len(self.get_questions())

    def get_counters(self) -> List[Tuple[str, int]]:
        counters = [
            (key, value)
            for key, value in
            self._data.get('aspects', {}).items()
        ]
        counters += [
            (key, value)
            for key, value in
            self._data.get('dichotomies', {}).items()
        ]
        return sorted(counters, key=lambda x: -x[1])

    def add_vote(self, vote: Union[SocDichotomyValue, str]):
        if isinstance(vote, SocDichotomyValue):
            if not self._data.get('dichotomies'):
                self._data['dichotomies'] = {}
            self._data['dichotomies'][vote.value] = self._data['dichotomies'].get(vote.value, 0) + 1
        else:
            if not self._data.get('aspects'):
                self._data['aspects'] = {}
            self._data['aspects'][vote] = self._data['aspects'].get(vote, 0) + 1

    @classmethod
    def normalize_dict(cls, items: dict):
        values_sum = sum(items.values()) or 1
        return {
            key: value / values_sum
            for key, value in items.items()
        }

    @classmethod
    def _fit_type_score(cls, soc_type: SocType,
                        aspects: Dict[str, int],
                        dichotomies: Dict[SocDichotomyValue, int]) -> float:

        aspects = cls.normalize_dict(aspects)
        dichotomies = cls.normalize_dict(dichotomies)
        model_a = soc_engine.model_by_type(soc_type)
        model_ds = []

        aspect_weight = {
            model_a[1]: 8,
            model_a[2]: 6,
            model_a[3]: 1,
            model_a[4]: 0,
            model_a[5]: 3,
            model_a[6]: 3,
            model_a[7]: 1,
            model_a[8]: 2,
        }
        aspect_weight = cls.normalize_dict(aspect_weight)

        for d_name in SocDichotomyName:
            model_ds.append(soc_engine.get_dichotomy_value(model_a, d_name))

        aspect_score = 0
        for aspect, amount in aspects.items():
            aspect_score += aspect_weight[aspect] * amount

        d_score = 0
        for d in model_ds:
            d_score += dichotomies.get(d, 0)

        return d_score + aspect_score

    def have_results(self):
        return sum(self._data.get('dichotomies', {}).values()) + sum(self._data.get('aspects', {}).values()) > 3

    def calculate_types_percents(self) -> List[Tuple[SocType, float]]:
        aspects = self._data.get('aspects', {})
        dichotomies = self._data.get('dichotomies', {})
        dichotomies = {
            SocDichotomyValue(item): count
            for item, count in dichotomies.items()
        }
        types_score: Dict[SocType, float] = {}
        for soc_type in soc_engine.get_all_types():
            score = self._fit_type_score(soc_type, aspects, dichotomies)
            types_score[soc_type] = score

        types_score = {
            item: value / 2
            for item, value in types_score.items()
        }
        result = [
            (item, score * 100)
            for item, score in
            types_score.items() if score > 0
        ]
        return sorted(result, key=lambda x: -x[1])


tests_manager = TestManger()


class SimpleTestRunner:
    def __init__(self, test: TestModel, data: dict):
        self._test = test
        self._data = data

    def get_soc_type(self) -> SocType:
        answers = [
            self._data[q.id] for q in self._test.questions
        ]
        dichotomies = [SocDichotomyValue(ans) for ans in answers]
        return soc_engine.get_type_by_dichotomies(dichotomies)

    def add_answer(self, question_id: str, ans: str):
        self._data[question_id] = ans
        self._data['last'] = question_id

    def is_begin(self) -> bool:
        return self._data.get('test') is None

    def init_test(self):
        self._data['test'] = self._test.id

    def finish(self):
        self._data.clear()

    def next_question(self) -> Optional[TestQuestion]:
        for q in self._test.questions:
            if not self._data.get(q.id):
                return q

    def prev_question(self) -> TestQuestion:
        return self._get_question_by_id(self._data['last'])

    def _get_question_by_id(self, question_id: str):
        for question in self._test.questions:
            if question.id == question_id:
                return question
        return None


@dp.callback_query_handler(callback('testing'))
async def testing_handler(cb: CallbackQuery, state: FSMContext):
    await state.finish()
    text = 'Выберите один из тестов на определения ТИМ-а, или запустите режим "Я Тестировщик"'
    buttons = []
    for test in tests_manager.get_all_tests():
        buttons.append(
            InlineKeyboardButton(test.name, callback_data=generate_callback_data(test=test.id))
        )
    keyword = [
        *batcher(buttons, 1),
        [InlineKeyboardButton('Режим "Тестировщик"', callback_data=generate_callback_data(vote='', q=''))],
        [back_to('menu')]
    ]
    await answer(
        cb, text, keyboard=keyword
    )


@dp.callback_query_handler(callback_keys('test', question=None, answer=None))
async def test_handler(cb: CallbackQuery, state: FSMContext):
    test = tests_manager.get_test_by_id(extract_value_from_callback(cb.data, 'test'))
    question_id = extract_value_from_callback(cb.data, 'question')
    curr_answer = extract_value_from_callback(cb.data, 'answer')

    async with state.proxy() as data:
        test_runner = SimpleTestRunner(test, data)
        is_begin = test_runner.is_begin()
        if is_begin:
            test_runner.init_test()
        else:
            test_runner.add_answer(question_id, curr_answer)

        question = test_runner.next_question()

        if not question:
            soc_type = test_runner.get_soc_type()
            test_runner.finish()
            cb.data = generate_callback_data(type=soc_type.id, desc=0)
            await send_desc(cb, back_route='testing')
            return

        buttons = []
        for ans in question.answers:
            buttons.append(
                InlineKeyboardButton(
                    ans.btn,
                    callback_data=generate_callback_data(
                        test=test.id,
                        question=question.id,
                        answer=ans.id
                    )
                )
            )

        keyword = [buttons]
        # if not is_begin and test_runner.prev_question().id != question_id:
        #     keyword.append(
        #         [InlineKeyboardButton(
        #             '⬅ Предыдущий вопрос',
        #             callback_data=generate_callback_data(test=test.id, question=test_runner.prev_question().id))]
        #     )
        keyword.append(
            [InlineKeyboardButton('↙️ Выйти из теста', callback_data='testing')]
        )
        await answer(cb, question.text, keyword)


@dp.callback_query_handler(callback_keys(vote=None, q=None, all_q=None, res=None))
async def tester_handler(cb: CallbackQuery, state: FSMContext):
    vote = extract_value_from_callback(cb.data, 'vote')
    q = extract_value_from_callback(cb.data, 'q')
    all_q = extract_value_from_callback(cb.data, 'all_q')
    res = extract_value_from_callback(cb.data, 'res')
    async with state.proxy() as data:
        runner = TesterModeRunner(data)
        if vote:
            try:
                runner.add_vote(SocDichotomyValue[vote])
            except:
                runner.add_vote(vote)
        text = soc_engine.get_desc('tester') + '\n\n'

        if q:
            runner.next_question()

        if all_q:
            questions = runner.get_questions()
            for q_ in questions:
                text += f'{q_}\n'
        else:
            question, curr, count = runner.get_current_question()
            text += f'({curr + 1}/{count}) {question}\n\n'

            if not res:
                counters = runner.get_counters()
                if counters:
                    for key, value in counters:
                        text += f'{key}: {value}\n'

        if res:
            types_percents = runner.calculate_types_percents()[:5]
            if types_percents:
                for i, (soc_type, percent) in enumerate(types_percents):
                    text += f'{i + 1}. {soc_type.name}: {round(percent, 1)}%\n'

        buttons = []
        for aspect in soc_engine.get_all_aspects():
            buttons.append(
                InlineKeyboardButton(
                    f'{aspect.emoji} {aspect.abbr}',
                    callback_data=generate_callback_data(vote=aspect.id)
                )
            )

        for dichotomy_value in SocDichotomyValue:
            buttons.append(
                InlineKeyboardButton(
                    dichotomy_value.value,
                    callback_data=generate_callback_data(vote=dichotomy_value.name)
                )
            )

        control_buttons = [
            InlineKeyboardButton('Следующий вопрос', callback_data=generate_callback_data(vote='', q='yes'))
        ]
        if not all_q:
            control_buttons.append(
                InlineKeyboardButton('Все вопросы', callback_data=generate_callback_data(vote='', all_q='yes'))
            )
        else:
            control_buttons.append(
                InlineKeyboardButton('Скрыть вопросы', callback_data=generate_callback_data(vote='', all_q=''))
            )

        if runner.have_results():
            if not res:
                control_buttons.append(
                    InlineKeyboardButton('Результаты', callback_data=generate_callback_data(res='yes', vote=''))
                )
            else:
                control_buttons.append(
                    InlineKeyboardButton('Скрыть результаты', callback_data=generate_callback_data(res='', vote=''))
                )

        keyword = [
            *batcher(buttons, 4),
            control_buttons,
            [back_to('testing')]
        ]
        await answer(cb, text, keyboard=keyword)
