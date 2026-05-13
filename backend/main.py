import os
import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# React ile iletişim için CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Streaming için AsyncOpenAI client
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MCP_URL = os.getenv("MCP_SERVER_URL")

class ChatRequest(BaseModel):
    message: str

@app.get("/")
async def root():
    return {"message": "Backend aktif!"}

# Azure MCP serverından toolları al
async def get_mcp_tools():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{MCP_URL}/list_tools", timeout=10.0)
            if response.status_code == 200:
                return response.json().get("tools", [])
            return []
    except Exception as e:
        print(f"Could not fetch MCP tools: {e}")
        return []

# Azure MCP serverından toolları çağır
async def call_mcp_tool(name: str, arguments: dict):
    try:
        async with httpx.AsyncClient() as client:
            payload = {"name": name, "arguments": arguments}
            response = await client.post(f"{MCP_URL}/call_tool", json=payload, timeout=30.0)
            if response.status_code == 200:
                return response.json()
            return {"error": f"Server returned {response.status_code}"}
    except Exception as e:
        return {"error": str(e)}

@app.post("/chat")
async def chat(request: ChatRequest):
    async def event_generator():
        try:
            mcp_tools = await get_mcp_tools()
            # MCP toolları OpenAI JSON-Schema formatına çevir
            openai_tools = [
                {
                    "type": "function", 
                    "function": {
                        "name": t["name"], 
                        "description": t["description"], 
                        "parameters": t["input_schema"]
                    }
                } for t in mcp_tools
            ]

            messages = [
                {"role": "system", "content": "Sen bir mevzuat asistanısın. Mevzuat MCP sunucusundaki araçları kullanarak doğru bilgi ver. Eğer bir sorunun cevabını o araçların içinde bulamazsan, bu konuda yardımcı olamayacağını söyle. Mevzuat MCP sunucusundaki araçların yardım edemeyeceği, konuyla alakasız soruları cevaplayamayacağını söyleyerek kullanıcıyı nazikçe asıl konuya döndür. Mevzuat MCP sunucusundan kullanıcıya bahsetme."},
                {"role": "user", "content": request.message}
            ]

            # Cevap için toola ihtiyaç var mı?
            response = await client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=messages,
                tools=openai_tools if openai_tools else None
            )
            
            response_message = response.choices[0].message
            tool_calls = response_message.tool_calls

            # Eğer toola ihtiyaç varsa, çağır
            if tool_calls:
                messages.append(response_message)
                for tool_call in tool_calls:
                    import json
                    function_args = json.loads(tool_call.function.arguments)
                    tool_result = await call_mcp_tool(tool_call.function.name, function_args)
                    # Sonuçları mesaja appendle
                    messages.append({
                        "tool_call_id": tool_call.id, 
                        "role": "tool", 
                        "name": tool_call.function.name, 
                        "content": json.dumps(tool_result)
                    })

            # Elde edilen cevabı React'e streamle           
            final_stream = await client.chat.completions.create(
                model="gpt-5.4-mini",
                messages=messages,
                stream=True
            )

            async for chunk in final_stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield content

        except Exception as e:
            yield f"Error: {str(e)}"

    return StreamingResponse(event_generator(), media_type="text/plain")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)