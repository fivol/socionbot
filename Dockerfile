FROM python:3.9
WORKDIR /app
RUN pip install "poetry"
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
#COPY pyproject.toml pyproject.toml
#COPY poetry.lock poetry.lock
#
#RUN poetry config virtualenvs.create false && poetry install --no-dev --no-interaction --no-ansi


CMD python main.py