FROM python:3.9
WORKDIR /app
RUN pip install "poetry"

RUN pip install -r requirements.txt
#COPY pyproject.toml pyproject.toml
#COPY poetry.lock poetry.lock
#
#RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi

COPY . .

CMD python main.py