"""
Vault MCP server (stdio).

Exposes the second-brain vault to MCP clients (Claude Code/Desktop) as three
read-only tools: search_notes, fetch_note, related_notes. Backed by the same
services the web API uses (see tools.py). Read-only by design — no tool mutates
the vault or the database.

Run:
    python -m mcp_server.server

Register in an MCP client (e.g. Claude Desktop config):
    {
      "mcpServers": {
        "second-brain": {
          "command": "python",
          "args": ["-m", "mcp_server.server"],
          "cwd": "/path/to/second-brain/backend"
        }
      }
    }
"""
import json

from mcp.server import Server
from mcp.server.stdio import stdio_server
import mcp.types as types

from app.database import SessionLocal
from mcp_server import tools

server = Server("second-brain")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="search_notes",
            description="Search the personal knowledge vault (hybrid keyword + semantic). Returns matching notes with id, path, title, score.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results (default 10)"},
                },
                "required": ["query"],
            },
        ),
        types.Tool(
            name="fetch_note",
            description="Fetch a single note's full body and metadata by id or path.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {"type": "integer", "description": "Note id"},
                    "path": {"type": "string", "description": "Note path (alternative to note_id)"},
                },
            },
        ),
        types.Tool(
            name="related_notes",
            description="Find notes semantically related to a given note (kNN over embeddings). Empty if embeddings are unavailable.",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_id": {"type": "integer", "description": "Note id"},
                    "limit": {"type": "integer", "description": "Max results (default 5)"},
                },
                "required": ["note_id"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Dispatch a tool call to the pure tool logic over a short-lived session."""
    db = SessionLocal()
    try:
        if name == "search_notes":
            result = tools.search_notes(db, arguments["query"], arguments.get("limit", 10))
        elif name == "fetch_note":
            result = tools.fetch_note(db, arguments.get("note_id"), arguments.get("path"))
        elif name == "related_notes":
            result = tools.related_notes(db, arguments["note_id"], arguments.get("limit", 5))
        else:
            result = {"error": f"unknown tool: {name}"}
    finally:
        db.close()

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def _main() -> None:
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    import asyncio
    asyncio.run(_main())


if __name__ == "__main__":
    main()
