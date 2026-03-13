# 🏗️ Fort Lauderdale Construction Expert Bot — Setup Guide

## КРОК 1: Отримай Telegram Bot Token

1. Відкрий Telegram і знайди **@BotFather**
2. Надішли `/newbot`
3. Придумай ім'я боту: наприклад `FL Construction Expert`
4. Придумай username: наприклад `fl_build_expert_bot`
5. BotFather дасть тобі **TOKEN** — збережи його!

---

## КРОК 2: Отримай Anthropic API Key

1. Зайди на **https://console.anthropic.com**
2. Зареєструйся або увійди
3. Йди в **API Keys** → **Create Key**
4. Збережи ключ — він показується тільки один раз!

---

## КРОК 3: Запусти бота

### Варіант A — Локально на комп'ютері (тільки поки комп включений)

```bash
# Встанови залежності
pip install -r requirements.txt

# Встанови змінні середовища
export TELEGRAM_TOKEN="твій_token_від_botfather"
export ANTHROPIC_API_KEY="твій_anthropic_key"

# Запусти
python bot.py
```

### Варіант B — На сервері 24/7 (РЕКОМЕНДОВАНО)

**Використай Railway.app (безкоштовно до $5/міс)**

1. Зайди на **https://railway.app**
2. Підключи GitHub або завантаж файли
3. Додай environment variables:
   - `TELEGRAM_TOKEN` = твій токен
   - `ANTHROPIC_API_KEY` = твій ключ
4. Railway запустить бота автоматично 24/7!

**Або використай Render.com:**

1. Зайди на **https://render.com**
2. New → Web Service → завантаж файли
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python bot.py`
5. Додай Environment Variables

**Або VPS (найнадійніше):**

```bash
# На VPS (Ubuntu):
sudo apt update && sudo apt install python3-pip screen -y
pip3 install -r requirements.txt

# Запусти в фоні
export TELEGRAM_TOKEN="..."
export ANTHROPIC_API_KEY="..."
screen -S flbot
python3 bot.py
# Ctrl+A, D — щоб відійти від screen
```

---

## КРОК 4: Налаштуй бота в Telegram

В BotFather:
- `/setdescription` — опис бота
- `/setabouttext` — "Fort Lauderdale Construction Expert | Technical & Legal Advice"
- `/setuserpic` — завантаж аватар

---

## Що вміє бот:

✅ Відповідає на технічні питання (FBC, hurricane standards)
✅ Юридичні консультації (permits, zoning, liens)
✅ **Аналізує фотографії** будівництва
✅ Шукає актуальну інформацію на сайтах міста
✅ Пам'ятає контекст розмови (до 20 повідомлень)
✅ Підтримує українську та англійську мову
✅ Команда /clear для нової розмови
✅ Розбиває довгі відповіді на частини

---

## Файли:

```
fl_bot/
├── bot.py           ← Основний файл бота
├── requirements.txt ← Залежності
└── README.md        ← Ця інструкція
```

---

## Підтримка:

Якщо бот не відповідає — перевір:
1. Чи правильний TELEGRAM_TOKEN
2. Чи є баланс на Anthropic API
3. Логи в терміналі — там буде причина помилки
