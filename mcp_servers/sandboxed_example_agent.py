import os
import asyncio
import shutil
from pathlib import Path

from dotenv import load_dotenv
from agents import Agent, Runner
from mcp_sandbox_openai_sdk import (
    FSAccess,
    MCPManifest,
    MCPServers,
    Permission,
    SandboxedMCPStdio,
)

# -------------------------------------------------
# 1) .env laden (OPENAI_API_KEY usw.)
# -------------------------------------------------

# Wir nehmen an: .env liegt im Projektroot,
# eine Ebene über dem Ordner mcp_servers
ENV_PATH = Path(__file__).parent.parent / ".env"
load_dotenv(ENV_PATH)

# Optionaler Check (kannst du auch auskommentieren)
if not os.getenv("OPENAI_API_KEY"):
    raise RuntimeError(
        f"OPENAI_API_KEY ist nicht gesetzt. "
        f"Stelle sicher, dass er in {ENV_PATH} steht "
        f"oder im Environment exportiert wurde."
    )

# -------------------------------------------------
# 2) Sandbox-Ordner definieren (ohne Leerzeichen)
# -------------------------------------------------

# Use /tmp for sandbox (no spaces in path - Docker requirement)
SANDBOX_DIR = Path("/tmp/mcp_event_outputs")
SANDBOX_DIR_STR = str(SANDBOX_DIR)
os.makedirs(SANDBOX_DIR, exist_ok=True)

# Project output directory (where files will be copied to)
PROJECT_OUTPUT_DIR = Path(__file__).parent.parent / "event_outputs"
os.makedirs(PROJECT_OUTPUT_DIR, exist_ok=True)

# -------------------------------------------------
# 3) MCP-Manifest für offiziellen Filesystem-Server
# -------------------------------------------------

manifest = MCPManifest(
    name="Filesystem Server",
    description="A server that accesses the local filesystem inside a sandbox.",
    registry="npm",  # WICHTIG: String, nicht Registry.NPM
    package_name="@modelcontextprotocol/server-filesystem",
    permissions=[
        Permission.MCP_AC_FILESYSTEM_READ,
        Permission.MCP_AC_FILESYSTEM_WRITE,
        Permission.MCP_AC_FILESYSTEM_DELETE,
    ],
)

# -------------------------------------------------
# 4) Hauptfunktion: Sandbox + Agent
# -------------------------------------------------


async def main():
    # Startet den MCP-Server im Docker-Sandbox-Container
    async with MCPServers(
        SandboxedMCPStdio(
            manifest=manifest,
            # Root-Verzeichnis für den Filesystem-Server
            runtime_args=[SANDBOX_DIR_STR],
            # Zugriffsrechte innerhalb der Sandbox
            runtime_permissions=[
                FSAccess(SANDBOX_DIR_STR, read=True, write=True),
            ],
        )
    ) as servers:
        # Agent, der NUR über diesen sandboxed MCP-Server aufs FS zugreifen darf
        agent = Agent(
            name="Sandbox Filesystem Tester",
            model="gpt-4.1-mini",  # oder "gpt-4o-mini", je nach Setup
            instructions=f"""
Du hast Zugriff auf einen sandboxed Filesystem-MCP-Server.

- Du darfst NUR das Verzeichnis {SANDBOX_DIR_STR} benutzen.
- Nutze die verfügbaren MCP-Tools (vom Filesystem-Server), um:
    1. Eine Datei 'hello.txt' mit etwas Inhalt anzulegen.
    2. Den Inhalt der Datei wieder auszulesen.
    3. Alle Dateien im Verzeichnis aufzulisten.

Erkläre in deiner Antwort:
- welche Tools du verwendet hast
- welche Ergebnisse du von den Tools bekommen hast.
""",
            mcp_servers=servers,
        )

        user_prompt = "Führe die drei beschriebenen Schritte aus."
        result = await Runner.run(agent, input=user_prompt)

        print("\n" + "=" * 60)
        print("AGENT-AUSGABE")
        print("=" * 60)
        print(result.final_output)
    
    # Copy files from sandbox temp directory to project directory
    print("\n" + "=" * 60)
    print("Kopiere Dateien in Projektordner...")
    print("=" * 60)
    
    if SANDBOX_DIR.exists():
        for file in SANDBOX_DIR.glob("*"):
            if file.is_file():
                dest = PROJECT_OUTPUT_DIR / file.name
                shutil.copy2(file, dest)
                print(f"✓ Kopiert: {file.name} → {dest}")
    
    print(f"\nDateien gespeichert in: {PROJECT_OUTPUT_DIR}")


# -------------------------------------------------
# 5) Entry Point
# -------------------------------------------------

if __name__ == "__main__":
    print("Starte Sandbox-MCP-Demo …")
    asyncio.run(main())