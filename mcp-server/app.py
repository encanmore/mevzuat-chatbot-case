"""
ASGI application for Mevzuat MCP Server

This is the production ASGI application that can be run with:
    uvicorn app:app --host 0.0.0.0 --port 8000

The MCP server will be available at:
    http://localhost:8000/mcp/
"""

from starlette.responses import JSONResponse
from mevzuat_mcp_server import app as mcp

# Add health check endpoint to the MCP server
@mcp.custom_route("/health", methods=["GET"])
async def health_check(request):
    """Health check endpoint for Fly.io and other monitoring services"""
    return JSONResponse({
        "status": "healthy",
        "service": "Mevzuat MCP Server",
        "version": "0.1.0"
    })

# REST bridges:
@mcp.custom_route("/list_tools", methods=["GET"])
async def list_tools_rest(request):
    try:
        tools_list = []
        available_tools = await mcp.list_tools() 
        
        for t in available_tools:
            tools_list.append({
                "name": getattr(t, "name", "unknown"),
                "description": getattr(t, "description", ""),
                "input_schema": getattr(t, "parameters", getattr(t, "input_schema", {}))
            })
        return JSONResponse({"tools": tools_list})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

@mcp.custom_route("/call_tool", methods=["POST"])
async def call_tool_rest(request):
    try:
        data = await request.json()
        name = data.get("name")
        args = data.get("arguments", {})
        result = await mcp.call_tool(name, args)
        return JSONResponse(result.content if hasattr(result, 'content') else result)
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)

# Create ASGI app directly from FastMCP server
# This avoids routing issues with nested mounts
app = mcp.http_app()

# Endpoints:
# - /mcp/ - MCP server (Streamable HTTP transport, default FastMCP path)
# - /health - Health check for monitoring
# Run with: uvicorn app:app --host 0.0.0.0 --port 8000
