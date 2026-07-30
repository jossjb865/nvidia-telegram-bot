import os
import sys
import html
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction, ParseMode
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuración de entornos y variables de seguridad
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not NVIDIA_API_KEY or not TELEGRAM_BOT_TOKEN:
    print("ERROR: Faltan las variables de entorno NVIDIA_API_KEY o TELEGRAM_BOT_TOKEN.")
    sys.exit(1)

# Conexión directa a la API de NVIDIA basada en la arquitectura OpenAI
client = OpenAI(
    base_url="https://nvidia.com",
    api_key=NVIDIA_API_KEY
)

# Modelo oficial de investigación y razonamiento avanzado del catálogo de NVIDIA
MODEL_NAME = "deepseek-ai/deepseek-v4-pro"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "¡Hola! Soy tu asistente de investigación avanzada potenciado por DeepSeek V4 Pro en la infraestructura de NVIDIA."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Envía estado de "Escribiendo..." continuo mientras el modelo investiga y razona
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system", 
                    "content": "Eres un asistente experto en investigación profunda y razonamiento técnico. Responde directamente en formato HTML limpio para Telegram (usa <b>, <i>, <code>, <pre>)."
                },
                {"role": "user", "content": user_text}
            ],
            temperature=0.6,
            max_tokens=1500
        )
        reply_text = response.choices.message.content
        parse_mode = ParseMode.HTML
    except Exception as e:
        reply_text = f"Ocurrió un error con la API de NVIDIA: {html.escape(str(e))}"
        parse_mode = None

    await update.message.reply_text(text=reply_text, parse_mode=parse_mode)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Bot activo y escuchando mensajes en tiempo real...")
    app.run_polling()
