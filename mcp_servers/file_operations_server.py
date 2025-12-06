"""
Simple MCP server for file operations using FastMCP.
Allows agents to save files through MCP tools.

This implements the proper MCP pattern from modelcontextprotocol.io
"""
import json
import logging
from pathlib import Path
from mcp.server.fastmcp import FastMCP

# Setup logging to stderr (not stdout, as that breaks MCP protocol)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastMCP server
mcp = FastMCP("file-operations")

# Output directory for saved files (in project root)
OUTPUT_DIR = Path(__file__).parent.parent / "event_outputs"
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)


@mcp.tool()
async def save_text_file(filename: str, content: str) -> str:
    """Save text content to a file.
    
    Args:
        filename: Name of the file to save
        content: Text content to write
    """
    try:
        filepath = OUTPUT_DIR / filename
        filepath.write_text(content, encoding='utf-8')
        logger.info(f"Saved text file: {filepath}")
        return f"✓ File saved: {filepath}"
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        return f"✗ Error: {e}"


@mcp.tool()
async def save_json_file(filename: str, data: dict) -> str:
    """Save JSON data to a file.
    
    Args:
        filename: Name of the JSON file
        data: Dictionary to save as JSON
    """
    try:
        filepath = OUTPUT_DIR / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"Saved JSON file: {filepath}")
        return f"✓ File saved: {filepath}"
    except Exception as e:
        logger.error(f"Error saving JSON file: {e}")
        return f"✗ Error: {e}"


@mcp.tool()
async def save_ics_file(filename: str, ics_content: str) -> str:
    """Save ICS calendar content to a file.
    
    Args:
        filename: Name of the ICS file
        ics_content: ICS calendar content
    """
    try:
        filepath = OUTPUT_DIR / filename
        filepath.write_text(ics_content, encoding='utf-8')
        logger.info(f"Saved ICS file: {filepath}")
        return f"✓ Calendar file saved: {filepath}"
    except Exception as e:
        logger.error(f"Error saving ICS file: {e}")
        return f"✗ Error: {e}"


@mcp.tool()
async def list_files() -> str:
    """List all files in the output directory."""
    try:
        if OUTPUT_DIR.exists():
            files = [f.name for f in OUTPUT_DIR.iterdir() if f.is_file()]
            file_list = "\n".join(files) if files else "No files found"
            return f"Files in {OUTPUT_DIR}:\n{file_list}"
        else:
            return f"Directory {OUTPUT_DIR} does not exist"
    except Exception as e:
        logger.error(f"Error listing files: {e}")
        return f"✗ Error: {e}"


@mcp.tool()
async def read_file(filename: str) -> str:
    """Read a file from the output directory.
    
    Args:
        filename: Name of the file to read
    """
    try:
        filepath = OUTPUT_DIR / filename
        if not filepath.exists():
            return f"✗ File not found: {filename}"
        
        content = filepath.read_text(encoding='utf-8')
        size = filepath.stat().st_size
        return f"Content of {filename} ({size} bytes):\n\n{content}"
    except Exception as e:
        logger.error(f"Error reading file: {e}")
        return f"✗ Error: {e}"


def main():
    """Initialize and run the MCP server."""
    logger.info("Starting file operations MCP server...")
    mcp.run(transport='stdio')


if __name__ == "__main__":
    main()
