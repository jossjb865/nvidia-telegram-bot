import os
import sys
import logging
from openai import OpenAI
from telegram import Update
from telegram.constants import ChatAction
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Configurar logging para ver errores detallados en los logs de GitHub Actions
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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

# System Prompt robusto enfocado en la estabilidad del texto enviado a Telegram
SYSTEM_INSTRUCTIONS = (
    "Eres un Ingeniero Estadístico Analítico especializado en fútbol predictivo y modelado de datos deportivos. "
    "Tu objetivo es investigar y desglosar métricas avanzadas por equipo con rigor matemático. "
    "Estructura tu respuesta analizando: 1) Córners, 2) Tarjetas, 3) Remates/al arco y xG, 4) Producción de goles. "
    "Usa un tono técnico, objetivo y probabilístico. "
    "IMPORTANTE: No uses etiquetas HTML complejas ni Markdown decorativo. Estructura el texto usando saltos de línea claros, "
    "mayúsculas para títulos y guiones para las listas. Así garantizamos que el sistema de mensajería no falle."
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "[SISTEMA ANALÍTICO ACTIVADO]\n\n"
        "Saludos. Soy tu asistente de ingeniería estadística deportiva. "
        "Envíame el nombre de un equipo o un enfrentamiento para calcular tendencias de córners, tarjetas, remates y goles."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = update.message.text
    
    # Envía estado de "Escribiendo..." continuo en Telegram
    await context.bot.send_chat_action(chat_id=update.effective_chat.id, action=ChatAction.TYPING)
    
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTIONS},
                {"role": "user", "content": user_text}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        reply_text = response.choices.message.content
    except Exception as e:
        reply_text = f"[ERROR DE API NVIDIA]: No se pudo obtener respuesta del catálogo. Detalle: {str(e)}"

    # Envío de texto plano seguro libre de errores de parseo
    await update.message.reply_text(text=reply_text)

# Manejador de errores global para evitar que el bot muera o deje de responder ante excepciones inesperadas
async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error(msg="Excepción capturada mientras se procesaba una actualización:", exc_info=context.error)
    if isinstance(update, Update) and update.message:
        await update.message.reply_text(
            "[ALERTA DE SISTEMA]: Ocurrió un error interno al procesar esta solicitud. "
            "El motor analítico sigue activo. Por favor, reformula tu consulta."
        )

if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar comandos y mensajes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    # Registrar el manejador de errores global obligatorio
    app.add_error_handler(error_handler)
    
    print("Bot estadístico protegido activo y escuchando flujos de datos...")
    app.run_polling()
