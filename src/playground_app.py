from agno.agent import Agent
from agno.os import AgentOS

from src.expert import criar_agente_expert
from src.reviewer import criar_agente_revisor
from src.translator import AGENTE_TRADUTOR

agents: list[Agent] = [
    criar_agente_expert(),
    criar_agente_revisor(),
    AGENTE_TRADUTOR,
]

agent_os = AgentOS(agents=agents)
app = agent_os.get_app()
