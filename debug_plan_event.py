import asyncio
import json

from custom_mcp_servers.fastmcp_server import _run_workflow_headless

async def main():
    event_details = {
        "event_name": "Testkonferenz",
        "event_type": "Conference",
        # zusätzliche Felder je nach Workflow
    }

    # sync → in Thread ausführen
    result = await asyncio.to_thread(_run_workflow_headless, event_details)

    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())