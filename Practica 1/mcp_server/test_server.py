import asyncio
import sys
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


SERVER = Path(__file__).resolve().parent / "server.py"


async def main():

    parametros = StdioServerParameters(
        command=sys.executable,
        args=[str(SERVER)],
    )

    async with stdio_client(parametros) as (read, write):

        async with ClientSession(
            read,
            write,
        ) as session:

            await session.initialize()

            herramientas = await session.list_tools()

            print("Herramientas MCP disponibles:")

            for herramienta in herramientas.tools:
                print(f"- {herramienta.name}")

            print()
            print("Probando resumen_general...")

            resultado = await session.call_tool(
                "resumen_general",
                arguments={},
            )

            print()
            print("Resultado:")

            for contenido in resultado.content:

                if hasattr(contenido, "text"):
                    print(contenido.text)
                else:
                    print(contenido)


if __name__ == "__main__":
    asyncio.run(main())
