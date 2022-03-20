import json
from typing import Dict

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
    def __init__(self):
        self._questions = read_file(f'{TESTS_PATH}/questions.json')

    def get_questions(self):
        return [item['text'] for item in self._questions]


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
        [InlineKeyboardButton('Режим "Тестировщик"', callback_data='tester')],
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


@dp.callback_query_handler(callback('tester'))
async def tester_handler(cb: CallbackQuery):
    keyword = [
        [InlineKeyboardButton('Список вопросов')],
        [back_to('testing')]
    ]
    await answer(cb, 'текст', keyboard=keyword)


@dp.callback_query_handler(callback('questions'))
async def tester_handler(cb: CallbackQuery):
    pass
