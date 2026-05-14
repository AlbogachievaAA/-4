import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = "8849596723:AAGDVxHsxikkBcKLdCSoF7PGFE0WSZYWeR0"
NVIDIA_API_KEY = "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"

messages = {}

def ask_ai(question, user_id):
    if user_id not in messages:
        messages[user_id] = []
    
    messages[user_id].append({"role": "user", "content": question})
    
    url = "https://integrate.api.nvidia.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {NVIDIA_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "meta/llama-3.3-70b-instruct",
        "messages": messages[user_id],
        "max_tokens": 500
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        answer = response.json()["choices"][0]["message"]["content"]
        messages[user_id].append({"role": "assistant", "content": answer})
        return answer
    except:
        return "Ошибка. Попробуй ещё раз."

async def start(update, context):
    await update.message.reply_text("Привет! Я бот-помощник. Задавай вопросы по учёбе. Напиши /help для списка команд.")

async def help(update, context):
    text = """📖 Доступные команды:

/start - начать общение
/help - показать список команд
/clear - очистить историю диалога
/history - показать историю сообщений

Просто напиши вопрос, и я отвечу!"""
    await update.message.reply_text(text)

async def clear(update, context):
    user_id = update.effective_user.id
    messages[user_id] = []
    await update.message.reply_text("История очищена.")

async def history(update, context):
    user_id = update.effective_user.id
    
    if user_id not in messages or len(messages[user_id]) == 0:
        await update.message.reply_text("История пуста. Напиши что-нибудь!")
        return
    
    history_text = "📜 История диалога:\n\n"
    count = 0
    
    for msg in messages[user_id]:
        if msg["role"] == "user":
            history_text += f"👤 Вы: {msg['content']}\n\n"
            count += 1
        elif msg["role"] == "assistant":
            history_text += f"🤖 Бот: {msg['content'][:100]}...\n\n"
    
    if count == 0:
        await update.message.reply_text("История пуста.")
    else:
        if len(history_text) > 4000:
            history_text = history_text[:4000] + "\n...(обрезано)"
        await update.message.reply_text(history_text)

async def reply(update, context):
    user_id = update.effective_user.id
    question = update.message.text
    await update.message.reply_text("Печатаю...")
    answer = ask_ai(question, user_id)
    await update.message.reply_text(answer)

def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(CommandHandler("history", history))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply))
    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()