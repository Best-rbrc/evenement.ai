#!/usr/bin/env python3
"""
Local MCP server for Tally form creation.
Designed to run inside a sandboxed Docker container with network egress.
"""

import os
import sys
import json
import asyncio
import uuid
from typing import Any, Optional

# Simple HTTP client implementation without external dependencies
import urllib.request
import urllib.error


class TallyMCPServer:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.tally.so"
    
    def create_form(self, title: str, fields: list[dict[str, Any]]) -> dict[str, Any]:
        """Create a Tally form via API (two-step: create blank, then add blocks)."""
        
        # Step 1: Create a blank form with empty blocks
        print(f" Step 1: Creating blank form...", file=sys.stderr)
        create_url = f"{self.base_url}/forms"
        create_data = {
            "status": "BLANK",
            "blocks": []  # Required even for blank forms
        }
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        create_req = urllib.request.Request(
            create_url,
            data=json.dumps(create_data).encode('utf-8'),
            headers=headers,
            method='POST'
        )
        
        try:
            with urllib.request.urlopen(create_req) as response:
                form_result = json.loads(response.read().decode('utf-8'))
                form_id = form_result.get('id')
                print(f" Blank form created with ID: {form_id}", file=sys.stderr)
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f" Step 1 failed - HTTP Error {e.code}: {error_body}", file=sys.stderr)
            return {"error": f"Failed to create blank form: HTTP {e.code}: {error_body}", "status_code": e.code}
        except Exception as e:
            print(f" Step 1 failed - Exception: {e}", file=sys.stderr)
            return {"error": f"Failed to create blank form: {str(e)}"}
        
        # Step 2: Add blocks via PATCH
        print(f" Step 2: Adding blocks to form {form_id}...", file=sys.stderr)
        
        # Map field types to Tally's block types
        type_mapping = {
            "text": "INPUT_TEXT",
            "email": "INPUT_EMAIL",
            "number": "INPUT_NUMBER",
            "textarea": "TEXTAREA",
            "select": "DROPDOWN"
        }
        
        # Build blocks per documentation example
        blocks = []
        
        # Form title block (groupType: TEXT per docs)
        title_uuid = str(uuid.uuid4())
        title_group_uuid = str(uuid.uuid4())
        blocks.append({
            "uuid": title_uuid,
            "type": "FORM_TITLE",
            "groupUuid": title_group_uuid,
            "groupType": "TEXT",
            "payload": {
                "html": title,
                "title": title
            }
        })
        
        # Add question blocks per documentation pattern
        for field in fields:
            field_type = field.get("type", "text")
            tally_type = type_mapping.get(field_type, "INPUT_TEXT")
            label = field.get("label", "")
            required = field.get("required", False)
            
            # TITLE block for question
            title_block_uuid = str(uuid.uuid4())
            title_block_group_uuid = str(uuid.uuid4())
            blocks.append({
                "uuid": title_block_uuid,
                "type": "TITLE",
                "groupUuid": title_block_group_uuid,
                "groupType": "QUESTION",
                "payload": {
                    "html": label
                }
            })
            
            # Input block
            input_uuid = str(uuid.uuid4())
            input_group_uuid = str(uuid.uuid4())
            input_payload = {
                "isRequired": required,
                "placeholder": ""
            }
            
            if "options" in field and tally_type == "DROPDOWN":
                input_payload["options"] = [{"label": opt} for opt in field["options"]]
            
            blocks.append({
                "uuid": input_uuid,
                "type": tally_type,
                "groupUuid": input_group_uuid,
                "groupType": tally_type,
                "payload": input_payload
            })
        
        # PATCH request to add blocks
        patch_url = f"{self.base_url}/forms/{form_id}"
        patch_data = {
            "name": title,
            "status": "PUBLISHED",
            "blocks": blocks
        }
        
        print(f" Patching form with {len(blocks)} blocks", file=sys.stderr)
        
        patch_req = urllib.request.Request(
            patch_url,
            data=json.dumps(patch_data).encode('utf-8'),
            headers=headers,
            method='PATCH'
        )
        
        try:
            with urllib.request.urlopen(patch_req) as response:
                result = json.loads(response.read().decode('utf-8'))
                print(f" Step 2 complete! Form published with blocks", file=sys.stderr)
                return result
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8')
            print(f" Step 2 failed - HTTP Error {e.code}: {error_body}", file=sys.stderr)
            return {"error": f"Failed to add blocks: HTTP {e.code}: {error_body}", "status_code": e.code, "form_id": form_id}
        except Exception as e:
            print(f" Step 2 failed - Exception: {e}", file=sys.stderr)
            return {"error": f"Failed to add blocks: {str(e)}", "form_id": form_id}


def handle_initialize(request_id: Optional[Any]):
    """Handle MCP initialize request."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "tally-mcp-server",
                "version": "1.0.0"
            }
        }
    }


def handle_tools_list(request_id: Optional[Any]):
    """List available tools."""
    return {
        "jsonrpc": "2.0",
        "id": request_id,
        "result": {
            "tools": [
                {
                    "name": "create_form",
                    "description": "Create a registration form on Tally",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the form"
                            },
                            "fields": {
                                "type": "array",
                                "description": "Array of form fields",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "type": {
                                            "type": "string",
                                            "enum": ["text", "email", "number", "textarea", "select"]
                                        },
                                        "label": {
                                            "type": "string"
                                        },
                                        "required": {
                                            "type": "boolean"
                                        }
                                    },
                                    "required": ["type", "label"]
                                }
                            }
                        },
                        "required": ["title", "fields"]
                    }
                }
            ]
        }
    }


def handle_tools_call(request_id: Optional[Any], tool_name: str, arguments: dict[str, Any]):
    """Execute a tool."""
    print(f" Tool called: {tool_name} with args: {arguments}", file=sys.stderr)
    
    api_key = os.environ.get("TALLY_API_KEY")
    if not api_key:
        print(" TALLY_API_KEY not set!", file=sys.stderr)
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": "TALLY_API_KEY environment variable not set"
                        })
                    }
                ]
            }
        }
    
    print(f" API key found: {api_key[:10]}...", file=sys.stderr)
    
    if tool_name == "create_form":
        print(" Creating form via Tally API...", file=sys.stderr)
        server = TallyMCPServer(api_key)
        result = server.create_form(
            title=arguments["title"],
            fields=arguments["fields"]
        )
        
        print(f" Form creation result: {result}", file=sys.stderr)
        
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result)
                    }
                ]
            }
        }
    else:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps({
                            "error": f"Unknown tool: {tool_name}"
                        })
                    }
                ]
            }
        }


def main():
    """Main MCP server loop using stdio transport."""
    print("Tally MCP Server starting...", file=sys.stderr)
    
    while True:
        try:
            # Read JSON-RPC message from stdin
            line = sys.stdin.readline()
            if not line:
                break
            
            line = line.strip()
            if not line:
                continue
                
            request = json.loads(line)
            request_id = request.get("id")
            method = request.get("method")
            params = request.get("params", {})
            
            # Handle notifications (no response expected)
            if method == "notifications/initialized":
                # Just acknowledge, no response needed for notifications
                continue
            
            # Route to appropriate handler
            if method == "initialize":
                response = handle_initialize(request_id)
            elif method == "tools/list":
                response = handle_tools_list(request_id)
            elif method == "tools/call":
                response = handle_tools_call(
                    request_id,
                    params.get("name"),
                    params.get("arguments", {})
                )
            else:
                # Unknown method
                response = {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
            
            # Send response
            print(json.dumps(response), flush=True)
            
        except json.JSONDecodeError as e:
            print(f"JSON decode error: {e}", file=sys.stderr)
            continue
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id") if 'request' in locals() else None,
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
            print(json.dumps(error_response), flush=True)


if __name__ == "__main__":
    main()
