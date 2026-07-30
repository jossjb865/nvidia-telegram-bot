import os
import sys
import logging
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configuración de logs visibles en GitHub Actions
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not NVIDIA_API_KEY or not TELEGRAM_BOT_TOKEN:
    print("ERROR: Faltan las variables de entorno.")
    sys.exit(1)

# Cliente conectado a la infraestructura estable de NVIDIA NIM
client = OpenAI(
    base_url="https://nvidia.com",
    api_key=NVIDIA_API_KEY
)

# Migración al modelo Flash: Máxima estabilidad, velocidad inmediata y libre de saturación
MODEL_NAME = "deepseek-ai/deepseek-v4-flash"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ [MOTOR ESTADÍSTICO DEPORTIVO ACTIVO]\n\n"
        "Hola. Soy tu Ingeniero Analítico de Fútbol. "
        "Envíame un equipo o partido y procesaré de inmediato córners, tarjetas, remates y xG."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    # Inyectamos el rol analítico e instrucciones directamente en la petición del usuario (evita fallos de API)
    prompt_estructurado = (
        "Actúa estrictamente como un Ingeniero Estadístico Analítico deportivo. "
        "Investiga y calcula en tiempo real las principales estadísticas del siguiente partido o equipo. "
        "Estructura tu análisis usando títulos claros y guiones en este orden exacto:\n"
        "1. CÓRNERS (Tendencias y promedios)\n"
        "2. TARJETAS (Métricas disciplinarias)\n"
        "3. REMATES Y REMATES AL ARCO (Eficiencia de ataque y xG)\n"
        "4. GOLES (Producción y promedio)\n"
        f"Consulta: {user_text}\n\n"
        "Responde usando texto plano limpio, saltos de línea ordenados y un tono matemático probabilístico."
    )
    
    try:
        # Petición limpia sin System Prompt complejo
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "user", "content": prompt_estructurado}
            ],
            temperature=0.2, # Rigidez y exactitud en los datos numéricos
            max_tokens=1200
        )
        reply_text = response.choices.message.content
    except Exception as e:
        # Captura el error exacto de NVIDIA en tus logs para diagnosticar
        logger.error(f"Fallo crítico en la API de NVIDIA: {str(e)}")
        reply_text = f"❌ [ERROR DE CONEXIÓN NVIDIA]: El servidor de NVIDIA rechazó la solicitud. Detalles técnicos: {str(e)}"

    await update.message.reply_text(text=reply_text)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Excepción de Telegram interceptada:", exc_info=context.error)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    app.add_error_handler(error_handler)
    
    print("Bot analítico estable iniciado en producción...")
    app.run_polling()
