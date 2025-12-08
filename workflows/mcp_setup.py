"""MCP server setup functions for event planning workflow."""
import os
from pathlib import Path


async def setup_sandboxed_local_tally_mcp(custom_mcp_dir: Path = None):
    """Setup sandboxed LOCAL Tally MCP server (custom Python implementation).
    
    This uses our custom tally_mcp_server.py that wraps the Tally REST API.
    Runs in Docker sandbox with network egress to api.tally.so.
    
    Args:
        custom_mcp_dir: Path to custom_mcp_servers directory (defaults to parent/custom_mcp_servers)
    
    Returns:
        Sandboxed custom Tally MCP server
    """
    from mcp_sandbox_openai_sdk import (
        DevMCPManifest,
        DomainPort,
        Permission,
        SandboxedMCPStdio,
    )
    
    # Custom local Tally MCP server (same setup as test_form_mcp.py)
    if custom_mcp_dir is None:
        # Default: assume this file is in workflows/, so go up one level
        custom_mcp_dir = Path(__file__).parent.parent / "custom_mcp_servers"
    tally_api_key = os.getenv('TALLY_API_KEY', '')
    
    tally_manifest = DevMCPManifest(
        name="Tally Form Server",
        description="Custom sandboxed Tally MCP server with network access to api.tally.so",
        registry="pypi",
        package_name="tally-mcp-server",  # Not used for DevMCPManifest
        permissions=[Permission.MCP_AC_NETWORK_CLIENT],
        code_mount=str(custom_mcp_dir),
        exec_command="python3 /sandbox/tally_mcp_server.py",
    )
    
    tally_server = SandboxedMCPStdio(
        manifest=tally_manifest,
        runtime_args=[],
        runtime_permissions=[DomainPort("api.tally.so", 443)],
        static_environment_vars={"TALLY_API_KEY": tally_api_key},
    )
    
    await tally_server.__aenter__()
    return tally_server


async def setup_unsandboxed_tally_mcp():
    """Setup UNSANDBOXED Tally mcp-remote server (official Tally MCP).
    
    This uses Tally's official mcp-remote package without sandboxing.
    Connects directly to api.tally.so with OAuth2 authentication.
    
    Returns:
        Unsandboxed Tally MCP client
    """
    from mcp import ClientSession, StdioServerParameters
    from mcp.client.stdio import stdio_client
    
    tally_api_key = os.getenv('TALLY_API_KEY', '')
    
    server_params = StdioServerParameters(
        command="npx",
        args=[
            "mcp-remote",
            "https://api.tally.so/mcp",
            "--header",
            f"Authorization: Bearer {tally_api_key}",
        ],
    )
    
    stdio_transport = await stdio_client(server_params).__aenter__()
    session = ClientSession(stdio_transport[0], stdio_transport[1])
    await session.__aenter__()
    
    return session


async def setup_sandboxed_filesystem_mcp(sandbox_dir: Path, project_output_dir: Path):
    """Setup sandboxed MCP server for calendar file operations.
    
    Creates filesystem server for ICS calendar file writes in sandbox.
    
    Args:
        sandbox_dir: Path to sandbox directory
        project_output_dir: Path to project output directory
    
    Returns:
        Sandboxed filesystem MCP server
    """
    from mcp_sandbox_openai_sdk import (
        FSAccess,
        MCPManifest,
        Permission,
        SandboxedMCPStdio,
    )
    
    sandbox_dir.mkdir(parents=True, exist_ok=True)
    project_output_dir.mkdir(parents=True, exist_ok=True)
    
    # Filesystem server manifest
    fs_manifest = MCPManifest(
        name="Filesystem Server",
        description="Sandbox-restricted file server for event outputs (ICS calendar files)",
        registry="npm",
        package_name="@modelcontextprotocol/server-filesystem",
        permissions=[
            Permission.MCP_AC_FILESYSTEM_READ,
            Permission.MCP_AC_FILESYSTEM_WRITE,
            Permission.MCP_AC_FILESYSTEM_DELETE,
        ],
    )
    
    # Create sandboxed filesystem server
    fs_server = SandboxedMCPStdio(
        manifest=fs_manifest,
        runtime_args=[str(sandbox_dir)],
        runtime_permissions=[
            FSAccess(str(sandbox_dir), read=True, write=True),
        ],
    )
    
    # Enter the async context but DON'T exit it
    # The context must stay alive for the duration of the workflow
    await fs_server.__aenter__()
    
    return fs_server

