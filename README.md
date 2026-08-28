# socionbot

A Telegram bot that turns socionics into something you can actually navigate: a
reference for all 16 types, a typing test, and the full 16×16 relations matrix —
without leaving the chat.

The bot speaks Russian; the code and docs are in English.

## What is inside

| Section | What it does |
|---|---|
| 📚 Reference | 16 types, 8 information aspects, 8 model-A functions, 4 quadras, 4 dichotomies — each with a description, rendered from a JSON knowledge base |
| 🎓 Typing test | 16 questions, dichotomy scoring, a type at the end |
| 🤝 Relations | Any pair of the 16 types → the relation between them (dual, conflict, mirror, …) and what it feels like in practice |

Everything the bot knows lives in `socionbot/theory/*.json` and
`socionbot/testing/*.json`, so editing the content never means touching the
handlers.

## Layout

```
main.py                    # menu, entry point
socionbot/
  bot.py                   # aiogram Dispatcher
  soc_engine.py            # the socionics engine: types, relations, scoring
  theory.py  theory_models.py  guide.py   # reference section
  testing.py               # the typing test
  relations.py             # relation lookup between two types
  templates.py static.py   # message rendering
  theory/*.json            # knowledge base: types, aspects, functions, quadras…
  testing/*.json           # test questions and scoring
```

## Run it

You need a bot token from [@BotFather](https://t.me/BotFather).

```bash
cp .env.example .env        # then put your BOT_TOKEN in it
pip install -r requirements.txt
python main.py
```

With Docker:

```bash
cp .env.example .env
docker compose up -d --build
```

## Configuration

| Variable | Required | What it is |
|---|---|---|
| `BOT_TOKEN` | yes | Telegram bot token from @BotFather |

## Sources

The type and relation descriptions were compiled from open socionics
references, mainly [socionika.info](https://socionika.info/tip/kwazi.html) and
[modernsocionics.ru](http://www.modernsocionics.ru/types/ile).

## License

MIT — see [LICENSE](LICENSE).
