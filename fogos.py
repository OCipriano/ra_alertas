# fogos.py

import os
import aiohttp
import logging
from dotenv import load_dotenv

# ------------------------- CONFIGURAÇÃO DE LOGS ---------------------------

logger = logging.getLogger(__name__)

# ------------------------- CARREGAR VARIÁVEIS DE AMBIENTE -----------------

load_dotenv()

FOGOS_API = os.getenv("FOGOS_API")

# ------------------------- OBTER FOGOS DO API -----------------------------

async def obter_fogos_ativos():
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(FOGOS_API) as response:
                if response.status != 200:
                    logger.warning("Erro ao obter dados dos fogos: HTTP %d", response.status)
                    return []

                dados = await response.json()
                return dados.get("data", [])
    except Exception as e:
        logger.exception("Erro ao obter dados dos fogos")
        return []
