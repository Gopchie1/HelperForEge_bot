import random
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import datetime
import pytz
from collections import defaultdict

# Конфигурация бота
bot = Bot(token="8086670033:AAFfk_9e6slFO9R2_BIQm7PVM-VqRXdfKGQ")
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

async def set_bot_avatar():
    """Устанавливает аватарку для бота из интернета"""
    try:
        avatar_url = "https://yaart-web-alice-images.s3.yandex.net/b3f21f0b2e9c11f08591baf2a50bbe99:1"
        response = requests.get(avatar_url)
        avatar_bytes = BytesIO(response.content)

        # Устанавливаем аватарку
        await bot.set_chat_photo(photo=types.FSInputFile(avatar_bytes))
        print("Аватарка бота успешно установлена!")
    except Exception as e:
        print(f"Ошибка при установке аватарки: {e}")

# База данных слов
WORDS_DB = [
    # Задание 4 - Ударения (10 слов)
    {
        "word": "звонит",
        "correct": "звонИт",
        "task": 4,
        "options": ["звОнит", "звонИт", "звОнишь", "звОнят"],
        "example": "Не забудь, что он звонИт ровно в полдень"
    },
    {
        "word": "торты",
        "correct": "тОрты",
        "task": 4,
        "options": ["тортЫ", "тОрты", "тортАми", "тортОв"],
        "example": "На праздник мы купили пять тОртов"
    },
    {
        "word": "красивее",
        "correct": "красИвее",
        "task": 4,
        "options": ["красивЕе", "красИвее", "красИвый", "красИвей"],
        "example": "Это платье выглядит красИвее, чем предыдущее"
    },
    {
        "word": "щавель",
        "correct": "щавЕль",
        "task": 4,
        "options": ["щАвель", "щавЕль", "щАвеля", "щАвелю"],
        "example": "Бабушка сварила суп со щавЕлем"
    },
    {
        "word": "свекла",
        "correct": "свЁкла",
        "task": 4,
        "options": ["свеклА", "свЁкла", "свЁклы", "свеклОй"],
        "example": "СвЁкла очень полезна для здоровья"
    },
    {
        "word": "договор",
        "correct": "договОр",
        "task": 4,
        "options": ["дОговор", "договОр", "договорА", "договорУ"],
        "example": "Мы подписали новый договОр с клиентом"
    },
    {
        "word": "каталог",
        "correct": "катАлог",
        "task": 4,
        "options": ["каталОг", "катАлог", "каталогА", "каталОгом"],
        "example": "В этом катАлоге представлены все наши товары"
    },
    {
        "word": "квартал",
        "correct": "квартАл",
        "task": 4,
        "options": ["квАртал", "квартАл", "квартАла", "квАрталу"],
        "example": "В последнем квартАле прибыль компании выросла"
    },
    {
        "word": "баловать",
        "correct": "баловАть",
        "task": 4,
        "options": ["бАловать", "баловАть", "балУющий", "балУете"],
        "example": "Не стоит слишком баловАть детей подарками"
    },
    {
        "word": "средства",
        "correct": "срЕдства",
        "task": 4,
        "options": ["средствА", "срЕдства", "срЕдству", "средствАх"],
        "example": "Все срЕдства пойдут на благотворительность"
    },

    # Задание 15 - Н/НН (10 слов)
    {
        "word": "кованый",
        "correct": "кованый",
        "task": 15,
        "options": ["кованый", "кованный"],
        "rule": "В прилагательных с суффиксами -ан-, -ян-, -ин- пишется одна Н"
    },
    {
        "word": "стеклянный",
        "correct": "стеклянный",
        "task": 15,
        "options": ["стекляный", "стеклянный"],
        "rule": "Исключения: стеклянный, оловянный, деревянный"
    },
    {
        "word": "нежданный",
        "correct": "нежданный",
        "task": 15,
        "options": ["нежданый", "нежданный"],
        "rule": "В прилагательных, образованных от глаголов несовершенного вида, пишется Н"
    },
    {
        "word": "раненый",
        "correct": "раненый",
        "task": 15,
        "options": ["раненый", "раненный"],
        "rule": "В отглагольных прилагательных пишется Н"
    },
    {
        "word": "лиственный",
        "correct": "лиственный",
        "task": 15,
        "options": ["лиственный", "лиственнный"],
        "rule": "В прилагательных, образованных от существительных с основой на Н, пишется НН"
    },
    {
        "word": "путаный",
        "correct": "путаный",
        "task": 15,
        "options": ["путаный", "путанный"],
        "rule": "В отглагольных прилагательных пишется Н"
    },
    {
        "word": "нечаянный",
        "correct": "нечаянный",
        "task": 15,
        "options": ["нечаяный", "нечаянный"],
        "rule": "В прилагательных, образованных от глаголов совершенного вида, пишется НН"
    },
    {
        "word": "масляный",
        "correct": "масляный",
        "task": 15,
        "options": ["масляный", "маслянный"],
        "rule": "В прилагательных с суффиксами -ан-, -ян- пишется одна Н"
    },
    {
        "word": "ветреный",
        "correct": "ветреный",
        "task": 15,
        "options": ["ветреный", "ветренный"],
        "rule": "Исключение: ветреный (но безветренный)"
    },
    {
        "word": "жареный",
        "correct": "жареный",
        "task": 15,
        "options": ["жареный", "жаренный"],
        "rule": "В отглагольных прилагательных пишется Н"
    },

    # Задание 14 - Слитное/дефисное/раздельное написание (10 слов)
    {
        "word": "кое(?)какой",
        "correct": "кое-какой",
        "task": 14,
        "options": ["коекакой", "кое-какой", "кое какой"],
        "rule": "Приставка кое- и суффиксы -то, -либо, -нибудь пишутся через дефис"
    },
    {
        "word": "по(?)новому",
        "correct": "по-новому",
        "task": 14,
        "options": ["по новому", "по-новому", "поновому"],
        "rule": "Наречия, образованные от прилагательных с помощью приставки по- пишутся через дефис"
    },
    {
        "word": "в(?)пятых",
        "correct": "в-пятых",
        "task": 14,
        "options": ["впятых", "в-пятых", "в пятых"],
        "rule": "Порядковые числительные с приставкой в- (во-) пишутся через дефис"
    },
    {
        "word": "железно(?)дорожный",
        "correct": "железнодорожный",
        "task": 14,
        "options": ["железно-дорожный", "железнодорожный", "железно дорожный"],
        "rule": "Сложные прилагательные, образованные от словосочетаний, пишутся слитно"
    },
    {
        "word": "русско(?)английский",
        "correct": "русско-английский",
        "task": 14,
        "options": ["русско английский", "русско-английский", "русскоанглийский"],
        "rule": "Сложные прилагательные, обозначающие равноправные понятия, пишутся через дефис"
    },
    {
        "word": "по(?)моему",
        "correct": "по-моему",
        "task": 14,
        "options": ["по моему", "по-моему", "помоему"],
        "rule": "Наречия с приставкой по- и суффиксами -ому, -ему, -и пишутся через дефис"
    },
    {
        "word": "в(?)общем",
        "correct": "в общем",
        "task": 14,
        "options": ["вобщем", "в-общем", "в общем"],
        "rule": "Предлог 'в' с существительным 'общем' пишется раздельно"
    },
    {
        "word": "кое(?)с(?)кем",
        "correct": "кое с кем",
        "task": 14,
        "options": ["кое-с-кем", "кое с кем", "коескем"],
        "rule": "Приставка кое- с предлогом пишется раздельно"
    },
    {
        "word": "ярко(?)красный",
        "correct": "ярко-красный",
        "task": 14,
        "options": ["ярко красный", "ярко-красный", "яркокрасный"],
        "rule": "Прилагательные, обозначающие оттенки цветов, пишутся через дефис"
    },
    {
        "word": "северо(?)западный",
        "correct": "северо-западный",
        "task": 14,
        "options": ["северозападный", "северо-западный", "северо западный"],
        "rule": "Сложные прилагательные, обозначающие стороны света, пишутся через дефис"
    }
]

TASKS = {
    4: "Задание 4 (Ударения)",
    14: "Задание 14 (дефис/слитно/раздельно)",
    15: "Задание 15 (Н/НН)"
}


# Хранилище данных
class UserStats:
    def __init__(self):
        self.total_answers = 0
        self.correct_answers = 0
        self.mistakes = defaultdict(int)
        self.daily_streak = 0
        self.last_activity = None


USER_STATS = defaultdict(UserStats)
DAILY_USERS = {}


# Состояния FSM
class QuizStates(StatesGroup):
    select_task = State()
    select_mode = State()
    in_quiz = State()
    set_daily = State()


# ===== ОСНОВНЫЕ КОМАНДЫ =====
@dp.message(Command("start"))
async def start_cmd(message: types.Message, state: FSMContext):
    """Главное меню"""
    builder = InlineKeyboardBuilder()
    builder.button(text="🏋️ Тренировка", callback_data="open_training")
    builder.button(text="📅 Ежедневная тренировка", callback_data="daily_settings")
    builder.button(text="📊 Моя статистика", callback_data="my_stats")
    builder.adjust(1)

    await message.answer(
        "Привет! Я помогу тебе подготовиться к ЕГЭ по русскому языку.\n"
        "Выбери действие:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "open_training")
async def open_training(callback: types.CallbackQuery, state: FSMContext):
    """Меню выбора задания"""
    builder = InlineKeyboardBuilder()
    for task_num, task_name in TASKS.items():
        builder.button(text=task_name, callback_data=f"task_{task_num}")
    builder.button(text="🔙 В меню", callback_data="back_to_menu")
    builder.adjust(2, 1)

    await callback.message.edit_text(
        "Выберите задание ЕГЭ:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(QuizStates.select_task)


@dp.callback_query(F.data.startswith("task_"), QuizStates.select_task)
async def select_task(callback: types.CallbackQuery, state: FSMContext):
    """Выбор режима тренировки"""
    task_num = int(callback.data.split("_")[1])
    await state.update_data(current_task=task_num)

    builder = InlineKeyboardBuilder()
    builder.button(text="⏱ На время", callback_data="mode_timed")
    builder.button(text="🔢 На количество", callback_data="mode_limited")
    builder.button(text="🔙 В меню", callback_data="back_to_menu")
    builder.adjust(2, 1)

    await callback.message.edit_text(
        f"Выбрано: {TASKS[task_num]}\nВыберите режим:",
        reply_markup=builder.as_markup()
    )
    await state.set_state(QuizStates.select_mode)


@dp.callback_query(F.data.startswith("mode_"), QuizStates.select_mode)
async def select_mode(callback: types.CallbackQuery, state: FSMContext):
    """Начало тренировки"""
    mode = callback.data.split("_")[1]
    data = await state.get_data()
    question = random.choice([w for w in WORDS_DB if w["task"] == data["current_task"]])

    builder = InlineKeyboardBuilder()
    for option in question["options"]:
        builder.button(text=option, callback_data=f"answer_{option}")
    builder.button(text="🔙 В меню", callback_data="back_to_menu")

    # Разное расположение кнопок для разных заданий
    if data["current_task"] in [15, 14]:  # Для Н/НН и написания - одна колонка
        builder.adjust(1, 1)
    else:  # Для ударений - две колонки
        builder.adjust(2, 1)

    # Формируем текст вопроса
    if data["current_task"] == 4:
        question_text = f"Где ударение в слове {question['word']}?"
        options_text = "\n".join([f"{option}" for option in question["options"]])
    elif data["current_task"] == 15:
        question_text = f"Как правильно писать слово:\n{question['word']}"
        options_text = " / ".join(question["options"])
    elif data["current_task"] == 14:
        question_text = f"Выберите правильный вариант написания:\n{question['word'].replace('(?)', '_')}"
        options_text = "\n".join(question["options"])

    # Таймер только для задания 4
    timer_text = "\n\n⏱ У вас 20 секунд на ответ!" if mode == "timed" and data["current_task"] == 4 else ""

    await callback.message.edit_text(
        f"{question_text}\n\n{options_text}{timer_text}",
        reply_markup=builder.as_markup()
    )

    if mode == "timed" and data["current_task"] == 4:
        await asyncio.create_task(timed_quiz(callback.message, state))

    await state.update_data(
        current_mode=mode,
        current_question=question,
        correct=0,
        total=0,
        mistakes=[],
        timer_active=True
    )
    await state.set_state(QuizStates.in_quiz)


async def timed_quiz(message: types.Message, state: FSMContext):
    """Таймер для режима 'На время'"""
    await asyncio.sleep(20)
    data = await state.get_data()
    if data.get("timer_active", False):
        await state.update_data(timer_active=False)
        await finish_quiz(message, state, timed_out=True)


async def finish_quiz(message: types.Message, state: FSMContext, timed_out=False):
    """Завершение тренировки"""
    data = await state.get_data()

    stats = "⏱ Время вышло!\n" if timed_out else ""
    stats += f"🏁 Тренировка завершена!\nПравильных ответов: {data['correct']}/{data['total']}\n"

    if data["mistakes"]:
        stats += "\nОшибки:\n" + "\n".join(f"• {m}" for m in data["mistakes"])

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 В меню", callback_data="back_to_menu")

    await message.answer(stats, reply_markup=builder.as_markup())
    await state.clear()


@dp.callback_query(F.data.startswith("answer_"), QuizStates.in_quiz)
async def check_answer(callback: types.CallbackQuery, state: FSMContext):
    """Проверка ответа"""
    data = await state.get_data()
    if not data.get("timer_active", True):
        await callback.answer("Время вышло! Тренировка завершена.")
        return

    user_answer = callback.data.split("_")[1]
    question = data["current_question"]
    is_correct = user_answer == question["correct"]
    user_id = callback.from_user.id

    USER_STATS[user_id].total_answers += 1
    if is_correct:
        USER_STATS[user_id].correct_answers += 1
        await callback.answer("✅ Правильно!")
    else:
        USER_STATS[user_id].mistakes[question['word']] += 1
        await callback.answer("❌ Неправильно!")

    new_data = {
        "correct": data["correct"] + (1 if is_correct else 0),
        "total": data["total"] + 1
    }
    if not is_correct:
        mistake_text = f"{question['word'].replace('(?)', '_')}: {user_answer} (верно: {question['correct']})"
        if "rule" in question:
            mistake_text += f"\nПравило: {question['rule']}"
        new_data["mistakes"] = data["mistakes"] + [mistake_text]

    await state.update_data(**new_data)

    if data["current_mode"] == "limited" and new_data["total"] >= 10:
        await state.update_data(timer_active=False)
        await finish_quiz(callback.message, state)
        return

    current_word = question['word']
    available_questions = [w for w in WORDS_DB if w["task"] == data["current_task"] and w['word'] != current_word]

    if not available_questions:
        await state.update_data(timer_active=False)
        await finish_quiz(callback.message, state)
        return

    next_question = random.choice(available_questions)

    builder = InlineKeyboardBuilder()
    for option in next_question["options"]:
        builder.button(text=option, callback_data=f"answer_{option}")
    builder.button(text="🔙 В меню", callback_data="back_to_menu")

    if data["current_task"] in [15, 14]:
        builder.adjust(1, 1)
    else:
        builder.adjust(2, 1)

    # Формируем текст вопроса
    if data["current_task"] == 4:
        question_text = f"Где ударение в слове {next_question['word']}?"
        options_text = "\n".join([f"{option}" for option in next_question["options"]])
    elif data["current_task"] == 15:
        question_text = f"Как правильно писать слово:\n{next_question['word']}"
        options_text = " / ".join(next_question["options"])
    elif data["current_task"] == 14:
        question_text = f"Выберите правильный вариант написания:\n{next_question['word'].replace('(?)', '_')}"
        options_text = "\n".join(next_question["options"])

    new_text = f"{question_text}\n\n{options_text}"

    if data["current_mode"] == "timed" and data["current_task"] == 4:
        new_text += "\n\n⏱ У вас 20 секунд на ответ!"

    try:
        await callback.message.edit_text(
            text=new_text,
            reply_markup=builder.as_markup()
        )
    except:
        await callback.message.answer(
            text=new_text,
            reply_markup=builder.as_markup()
        )

    await state.update_data(current_question=next_question)


# ===== ЕЖЕДНЕВНАЯ ТРЕНИРОВКА =====
@dp.callback_query(F.data == "daily_settings")
async def daily_settings(callback: types.CallbackQuery, state: FSMContext):
    """Настройки ежедневной тренировки"""
    user_id = callback.from_user.id
    current_settings = DAILY_USERS.get(user_id, {})

    builder = InlineKeyboardBuilder()
    if current_settings.get('active'):
        builder.button(text="🔴 Отключить", callback_data="daily_toggle_off")
        status = f"⏰ Включена ({current_settings.get('time', 'не указано')})"
    else:
        builder.button(text="🟢 Включить", callback_data="daily_toggle_on")
        status = "🔴 Отключена"

    builder.button(text="🕘 Изменить время", callback_data="daily_set_time")
    builder.button(text="📚 Изменить задание", callback_data="daily_set_task")
    builder.button(text="🔙 В меню", callback_data="back_to_menu")
    builder.adjust(1, 2, 1)

    await callback.message.edit_text(
        f"Ежедневная тренировка:\nСтатус: {status}\n"
        f"Текущее задание: {TASKS.get(current_settings.get('task', 4))}",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data == "daily_toggle_on")
async def daily_toggle_on(callback: types.CallbackQuery):
    """Активация ежедневной тренировки"""
    user_id = callback.from_user.id
    DAILY_USERS[user_id] = DAILY_USERS.get(user_id, {})
    DAILY_USERS[user_id]['active'] = True
    DAILY_USERS[user_id].setdefault('time', '09:00')
    DAILY_USERS[user_id].setdefault('task', 4)

    await callback.answer("Ежедневная тренировка активирована!")
    await daily_settings(callback)


@dp.callback_query(F.data == "daily_toggle_off")
async def daily_toggle_off(callback: types.CallbackQuery):
    """Деактивация ежедневной тренировки"""
    user_id = callback.from_user.id
    if user_id in DAILY_USERS:
        DAILY_USERS[user_id]['active'] = False
    await callback.answer("Ежедневная тренировка отключена!")
    await daily_settings(callback)


@dp.callback_query(F.data == "daily_set_time")
async def daily_set_time(callback: types.CallbackQuery, state: FSMContext):
    """Установка времени для ежедневной тренировки"""
    await callback.message.edit_text(
        "Введите время в формате ЧЧ:ММ (например, 09:30):"
    )
    await state.set_state(QuizStates.set_daily)


@dp.message(QuizStates.set_daily)
async def process_set_time(message: types.Message, state: FSMContext):
    """Обработка введенного времени"""
    try:
        input_time = datetime.strptime(message.text, "%H:%M").time()
        user_id = message.from_user.id

        if user_id not in DAILY_USERS:
            DAILY_USERS[user_id] = {'active': True, 'task': 4}

        DAILY_USERS[user_id]['time'] = message.text
        await message.answer(f"Время установлено на {message.text}")
        await state.clear()

    except ValueError:
        await message.answer("Неправильный формат времени. Попробуйте еще раз (например, 09:30)")


@dp.callback_query(F.data == "daily_set_task")
async def daily_set_task(callback: types.CallbackQuery, state: FSMContext):
    """Установка задания для ежедневной тренировки"""
    builder = InlineKeyboardBuilder()
    for task_num, task_name in TASKS.items():
        builder.button(text=task_name, callback_data=f"daily_task_{task_num}")
    builder.button(text="🔙 В меню", callback_data="back_to_menu")
    builder.adjust(2, 1)

    await callback.message.edit_text(
        "Выберите задание для ежедневной тренировки:",
        reply_markup=builder.as_markup()
    )


@dp.callback_query(F.data.startswith("daily_task_"))
async def process_daily_task(callback: types.CallbackQuery):
    """Обработка выбора задания для ежедневной тренировки"""
    task_num = int(callback.data.split("_")[2])
    user_id = callback.from_user.id

    if user_id not in DAILY_USERS:
        DAILY_USERS[user_id] = {'active': True, 'time': '09:00'}

    DAILY_USERS[user_id]['task'] = task_num
    await callback.answer(f"Задание для тренировки установлено: {TASKS[task_num]}")
    await daily_settings(callback)


# ===== СТАТИСТИКА =====
@dp.callback_query(F.data == "my_stats")
async def show_stats(callback: types.CallbackQuery):
    """Показ статистики"""
    user_id = callback.from_user.id
    stats = USER_STATS[user_id]

    correct_percent = (stats.correct_answers / stats.total_answers * 100) if stats.total_answers else 0
    top_mistakes = sorted(stats.mistakes.items(), key=lambda x: x[1], reverse=True)[:5]
    mistakes_text = "\n".join(
        [f"• {word} - {count} раз" for word, count in top_mistakes]) if top_mistakes else "Пока нет ошибок"

    stats_message = (
        f"📊 <b>Ваша статистика</b>\n\n"
        f"✅ Правильных ответов: <b>{stats.correct_answers}</b>\n"
        f"❌ Неправильных: <b>{stats.total_answers - stats.correct_answers}</b>\n"
        f"📈 Точность: <b>{correct_percent:.1f}%</b>\n"
        f"🔥 Серия дней: <b>{stats.daily_streak}</b>\n\n"
        f"<b>Частые ошибки:</b>\n{mistakes_text}"
    )

    builder = InlineKeyboardBuilder()
    builder.button(text="🔙 В меню", callback_data="back_to_menu")

    try:
        await callback.message.edit_text(
            stats_message,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )
    except:
        await callback.message.answer(
            stats_message,
            reply_markup=builder.as_markup(),
            parse_mode="HTML"
        )


@dp.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: types.CallbackQuery, state: FSMContext):
    """Возврат в главное меню"""
    await start_cmd(callback.message, state)


# ===== ЗАПУСК БОТА =====
async def on_startup():
    """Запуск фоновых задач"""
    await asyncio.create_task(send_daily_word())
    print("Бот успешно запущен!")


async def send_daily_word():
    """Фоновая рассылка ежедневных слов"""
    while True:
        now = datetime.now(pytz.timezone('Europe/Moscow')).strftime("%H:%M")
        for user_id, settings in DAILY_USERS.items():
            if settings.get('active', False) and settings.get('time') == now:
                task = settings.get('task', 4)
                available_words = [w for w in WORDS_DB if w["task"] == task]
                if available_words:
                    word_data = random.choice(available_words)

                    builder = InlineKeyboardBuilder()
                    for option in word_data["options"]:
                        builder.button(text=option, callback_data=f"answer_{option}")
                    builder.button(text="🔙 В меню", callback_data="back_to_menu")

                    if task in [15, 14]:
                        builder.adjust(1, 1)
                    else:
                        builder.adjust(2, 1)

                    try:
                        if task == 4:
                            text = f"📅 Слово дня ({TASKS[task]}):\n\nГде ударение в слове '{word_data['word']}'?"
                        elif task == 15:
                            text = f"📅 Слово дня ({TASKS[task]}):\n\nКак правильно писать слово:\n{word_data['word']}"
                        elif task == 14:
                            text = f"📅 Слово дня ({TASKS[task]}):\n\nВыберите правильный вариант написания:\n{word_data['word'].replace('(?)', '_')}"

                        await bot.send_message(
                            user_id,
                            text,
                            reply_markup=builder.as_markup()
                        )
                    except Exception as e:
                        print(f"Ошибка отправки сообщения пользователю {user_id}: {e}")

        await asyncio.sleep(60)


async def main():
    await dp.start_polling(bot, skip_updates=True, on_startup=on_startup)


if __name__ == "__main__":
    asyncio.run(main())