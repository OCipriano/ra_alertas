import os
import aiohttp
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime

# ------------------------- CARREGAR VARIÁVEIS DE AMBIENTE -----------------

load_dotenv()

SISMOS_API = os.getenv("SISMOS_API")

# ------------------------- CONFIGURAÇÕES DA MAGNITUDE ----------------------

def cor_magnitude(mag: float) -> str:
    if mag >= 6:
        return "🔴"  # Vermelho
    elif mag >= 5:
        return "🟠"  # Laranja
    elif mag >= 2:
        return "🟢"  # Verde
    else:
        return "⚪"  # Neutro (abaixo de 2)

# ------------------------- COMANDOS DO BOT --------------------------------

async def sismos(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    params = {
        "start": os.getenv("SEISMIC_START"),
        "format": os.getenv("SEISMIC_FORMAT", "json"),
        "minmag": os.getenv("SEISMIC_MINMAG", "2"),
        "limit": os.getenv("SEISMIC_LIMIT", "10")
    }

    seismic_end = os.getenv("SEISMIC_END")
    if seismic_end:
        params["end"] = seismic_end

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(SISMOS_API, params=params) as response:
                data = await response.json()

        eventos = data.get("features", [])
        if not eventos:
            await update.message.reply_text("❌ Não foram encontrados sismos com os critérios definidos.")
            return

        mensagem = "🌍 *Últimos Sismos:*\n\n"
        for evento in eventos:
            props = evento.get("properties", {})
            geo = evento.get("geometry", {})

            mag = props.get("mag", "?")
            magtype = props.get("magtype", "?")
            profundidade = props.get("depth", "?")
            lugar = props.get("flynn_region", "Região desconhecida")
            datahora = props.get("time", "").replace("T", " ").split(".")[0]

            latitude = geo.get("coordinates", [None, None])[1]
            longitude = geo.get("coordinates", [None, None])[0]

            if latitude and longitude:
                link_mapa = f"https://www.google.com/maps/search/?api=1&query={latitude},{longitude}"
                mapa_texto = f"🗺️ [Ver no mapa]({link_mapa})"
            else:
                mapa_texto = "🗺️ Localização desconhecida"

            # Cor de acordo com magnitude
            try:
                mag_valor = float(mag)
            except:
                mag_valor = 0
            cor = cor_magnitude(mag_valor)

            mensagem += (
                f"📍 *{lugar}*\n"
                f"🕒 {datahora}\n"
                f"💥️ Magnitude: {cor} {magtype} {mag}\n"
                f"📏 Profundidade: {profundidade} Km\n"
                f"{mapa_texto}\n\n"
            )

        if update.message:
            await update.message.reply_text(mensagem.strip(), parse_mode="Markdown")
        elif update.callback_query:
            await update.callback_query.message.reply_text(mensagem.strip(), parse_mode="Markdown")

    except Exception as e:
        erro_msg = f"⚠️ Erro ao obter dados sísmicos: {e}"
        if update.message:
            await update.message.reply_text(erro_msg)
        elif update.callback_query:
            await update.callback_query.message.reply_text(erro_msg)

async def magnitude_sismica(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Explica os diferentes tipos de magnitude sísmica."""
    mensagem = (
        "📊 *Tipos de Magnitude Sísmica:*\n\n"
        "🔸 *ML (Magnitude Local ou de Richter)*:\n"
        "Baseia-se na amplitude das ondas sísmicas registadas por sismógrafos próximos. É usada principalmente para sismos locais.\n\n"
        "🔸 *mb (Magnitude de Ondas de Corpo)*:\n"
        "Calculada a partir das ondas que atravessam o interior da Terra (ondas P e S). É usada em sismos maiores e mais distantes.\n\n"
        "🔸 *Mw (Magnitude de Momento)*:\n"
        "É a escala mais moderna e precisa. Baseia-se nas características físicas da falha (como área de ruptura e deslocamento). "
        "É especialmente fiável para grandes sismos, pois não perde precisão como as outras escalas."
    )
    if update.message:
        await update.message.reply_markdown(mensagem)
    elif update.callback_query:
        await update.callback_query.message.reply_markdown(mensagem)
