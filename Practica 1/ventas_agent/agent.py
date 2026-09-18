import sys
from pathlib import Path

from google.adk.agents import Agent
from google.adk.tools.mcp_tool.mcp_toolset import McpToolset
from google.adk.tools.mcp_tool import StdioConnectionParams
from mcp import StdioServerParameters


BASE_DIR = Path(__file__).resolve().parent.parent
MCP_SERVER = BASE_DIR / "mcp_server" / "server.py"


mcp_tools = McpToolset(
    connection_params=StdioConnectionParams(
        server_params=StdioServerParameters(
            command=sys.executable,
            args=[str(MCP_SERVER)],
        ),
        timeout=30,
    )
)


root_agent = Agent(
    name="analista_ventas_sog2",
    model="gemini-2.5-flash",
    description=(
        "Agente conversacional para análisis de ventas online 2025."
    ),
    instruction="""
Eres un analista de datos Junior para la práctica de
Sistemas Organizacionales y Gerenciales 2.

Tu información debe provenir de las herramientas MCP disponibles.
No inventes cifras.

Utiliza las herramientas adecuadas para responder preguntas sobre:

- estadísticas básicas;
- ventas por mes;
- métodos de pago;
- navegador o canal;
- segmentación por edad;
- comparación por género;
- correlación entre edad y venta total;
- boletines y vales;
- resumen general de ventas.

Cuando el usuario solicite un dato disponible en las herramientas,
consulta primero la herramienta correspondiente.

Responde en español de forma clara y breve.
Si los datos disponibles no permiten responder algo, indícalo.
""",
    tools=[
        mcp_tools
    ],
)
