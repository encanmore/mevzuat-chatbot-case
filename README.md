# Mevzuat MCP Chatbot

Azure üzerinde deploy edilmiş bir MCP (Model Context Protocol) serverı kullanarak mevzuat hakkında bilgi sağlayan basit bir chatbot sistemi.

## Deployment Detayları
- **MCP Server URL:** mevzuat-mcp-elif.bxdcceascchqhufh.westeurope.azurecontainer.io
- **Resource Group:** case-study-elif-candan

## Setup ve Çalıştırma

### 1. MCP Server (Cloud)
Server Dockerize edilmiş ve Azure Container Instances'a deploy edilmiştir. 
- Dockerfile lokasyonu: `mcp-server/Dockerfile`

### 2. Backend (Python)
- `backend/` klasörüne gidin
- Dependencyleri indirin: `pip install -r requirements.txt`
- Serverı başlatın: `python main.py`
- Backend `http://localhost:5000` adresinde çalışacaktır.

### 3. Frontend (React)
- `frontend/` klasörüne gidin
- Dependencyleri indirin: `npm install`
- Uygulamayı başlatın: `npm start`
- Frontend `http://localhost:3000` adresinde çalışacaktır.

## Özellikler
- **Streaming Cevaplar:** AI cevapları, streaming ile real-time olarak kullanıcıya iletilir.
- **MCP Entegrasyonu:** Mevzuat verilerini almak için cloud tabanlı MCP serverından araçlar kullanır.
- **Azure Entegrasyonu:** MCP serverı, konteynerleştirilmiş bir cloud ortamında deploy edilmiştir.