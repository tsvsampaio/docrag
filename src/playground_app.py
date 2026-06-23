import logging

from agno.agent import Agent
from agno.os import AgentOS

from src.expert import criar_agente_expert
from src.reviewer import criar_agente_revisor
from src.translator import AGENTE_TRADUTOR

logger = logging.getLogger("playground")

logger.info("Criando agentes...")
agents: list[Agent] = [
    criar_agente_expert(),
    criar_agente_revisor(),
    AGENTE_TRADUTOR,
]

logger.info("Inicializando AgentOS...")
agent_os = AgentOS(
    agents=agents,
    telemetry=False,
)
logger.info("Gerando app FastAPI...")
app = agent_os.get_app()
logger.info("Pronto! %d rotas registradas.", len(app.routes))
