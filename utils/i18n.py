from config import DEFAULT_LANGUAGE

translations = {
    "en": {
        "bot_ready": "✅ {bot} is running.",
        "failed_stream": "⚠️ Failed to fetch stream: {error}",
        "not_in_voice": "⚠️ You are not in a voice channel!",
        "added_queue": "➕ Added to queue: **{title}**",
        "now_playing": "🎶 Now playing: **{title}**",
        "nothing_playing": "⚠️ Nothing is playing right now.",
        "bot_not_connected": "⚠️ Bot is not connected.",
        "queue_empty": "🎧 Queue is empty.",
        "queue_shuffled": "🔀 Queue shuffled:\n{text}",
        "queue_list": "📜 Queue:\n{text}",
        "invalid_repeat": "⚠️ Invalid repeat mode! Choose: none, one, all",
        "repeat_set": "🔁 Repeat mode set to **{mode}**",
        "not_paused": "⚠️ Track is not paused.",
        "admin_only": "❌ Only administrators can use this command.",
        "searching_track": "🔎 Searching track...",
        "join_desc": "Connect the bot to a voice channel",
        "leave_desc": "Disconnect the bot from the voice channel",
        "play_desc": "Play a track by link or name",
        "skip_desc": "Skip the current track",
        "stop_desc": "Stop playing and disconnect the bot",
        "pause_desc": "Pause the current track",
        "resume_desc": "Resume playback",
        "shuffle_desc": "Shuffle the queue",
        "now_desc": "Show the currently playing track",
        "queue_desc": "Show the track queue",
        "repeat_desc": "Set repeat mode: none, one, all",
        "clear_desc": "Delete recent messages",
        "amount_desc": "Number of messages to delete",
        "buy": "See you soon!",
    },
    "ru": {
        "bot_ready": "✅ {bot} запущен.",
        "failed_stream": "⚠️ Не удалось получить поток: {error}",
        "not_in_voice": "⚠️ Ты не в голосовом канале!",
        "added_queue": "➕ Добавлено в очередь: **{title}**",
        "now_playing": "🎶 Сейчас играет: **{title}**",
        "nothing_playing": "⚠️ Сейчас ничего не играет.",
        "bot_not_connected": "⚠️ Бот не подключён.",
        "queue_empty": "🎧 Очередь пуста.",
        "queue_shuffled": "🔀 Очередь перемешана:\n{text}",
        "queue_list": "📜 Очередь:\n{text}",
        "invalid_repeat": "⚠️ Недопустимый режим! Выберите: none, one, all",
        "repeat_set": "🔁 Режим повтора установлен на **{mode}**",
        "not_paused": "⚠️ Трек не на паузе.",
        "admin_only": "❌ Только администратор может использовать эту команду.",
        "searching_track": "🔎 Ищу трек...",
        "join_desc": "Подключить бота к голосовому каналу",
        "leave_desc": "Отключить бота из голосового канала",
        "play_desc": "Играть трек по ссылке или названию",
        "skip_desc": "Пропустить текущий трек",
        "stop_desc": "Остановить воспроизведение и отключить бота",
        "pause_desc": "Поставить трек на паузу",
        "resume_desc": "Продолжить воспроизведение",
        "shuffle_desc": "Перемешать очередь",
        "now_desc": "Показать текущий трек",
        "queue_desc": "Показать очередь треков",
        "repeat_desc": "Выбрать режим повтора: none, one, all",
        "clear_desc": "Удалить последние сообщения",
        "amount_desc": "Количество сообщений для удаления",
        "buy": "До скорой встречи!",
    },
}


def t(key: str, lang: str = None, **kwargs) -> str:
    """Translate `key` into selected language and format with kwargs.

    If lang is None, uses DEFAULT_LANGUAGE from config. Falls back to English if
    key or language missing.
    """
    use_lang = lang or DEFAULT_LANGUAGE or "en"
    data = translations.get(use_lang) or translations.get("en")
    template = data.get(key)
    if template is None:
        template = translations.get("en", {}).get(key, key)
    try:
        return template.format(**kwargs)
    except Exception:
        return template
