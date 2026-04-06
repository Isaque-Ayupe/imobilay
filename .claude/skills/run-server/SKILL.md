---
name: run-server
description: Iniciar a API (FastAPI) e o frontend (Vite) do IMOBILAY em modo de desenvolvimento.
disable-model-invocation: true
allowed-tools: Bash
---

# Rodar Servidores — IMOBILAY

## Back-end (FastAPI)

A API expõe endpoints REST em `/api/chat`, `/api/sessions` e `/api/health`.

### Via arquivo principal

```bash
cd /c/imobilay
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### CLI rápida (pipeline direto)

```bash
cd /c/imobilay
python main.py "texto-da-query"
```

## Front-end (Vite)

### Instalação

```bash
cd /c/imobilay/frontend
npm install
```

### Desenvolvimento

```bash
npm run dev
```

## Pré-requisitos

- **Python 3.14+** com dependências: `pip install -r requirements.txt`
- **Node.js 18+** para o frontend
- **Variáveis de ambiente** em `.env` (ver `.env.example` se existir):
  - `GOOGLE_API_KEY` — acesso ao Google Gemini
  - Credenciais do Supabase (se não for modo mock)
  - Credenciais do Redis (se habilitado)

## Estrutura dos servidores

| Serviço | URL padrão | Comando |
|---------|-----------|---------|
| API (FastAPI) | `http://localhost:8000` | `uvicorn api:app --reload` |
| Frontend (Vite) | `http://localhost:5173` | `npm run dev` (em `frontend/`) |
| Docs Swagger | `http://localhost:8000/docs` | automático com FastAPI |

## Modo debug

```bash
cd /c/imobilay
uvicorn api:app --reload --log-level debug
```
