# Directive 01 — Setup do Projeto

## Objetivo
Configurar o ambiente de desenvolvimento completo para o IMOBILAY: Python, Node.js, Supabase e dependências.

## Inputs
- Acesso ao Supabase Dashboard (URL + chaves)
- Python 3.11+ instalado
- Node.js 18+ instalado
- Redis local ou Upstash configurado

## Passos

### 1. Ambiente Python
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou: venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

### 2. Variáveis de Ambiente
```bash
cp .env.example .env
# Preencher todas as variáveis no .env
```

Validar com:
```bash
python execution/setup_env.py
```

### 3. Supabase Dashboard
Checklist de setup (executar nesta ordem):
1. Project Settings → API → copiar URL, anon key, service_role key para `.env`
2. Database → Extensions → ativar `uuid-ossp` e `vector` (pgvector)
3. SQL Editor → executar `database/migrations/001_initial.sql`
4. Authentication → Providers → ativar Email
5. Database → Connection Pooling → confirmar Pool Mode = Transaction, porta 6543

Validar com:
```bash
python execution/test_connection.py
```

### 4. Ambiente Frontend
```bash
npx -y create-vite@latest frontend --template react-ts
cd frontend && npm install
npm install framer-motion lucide-react @fontsource/cormorant-garamond @fontsource/dm-sans
npm install -D tailwindcss @tailwindcss/vite
```

> **Aprendizado:** O frontend fica em `frontend/` (não `src/`). Tailwind v4 usa `@tailwindcss/vite` como plugin do Vite, não precisa de PostCSS.

### 5. Redis
```bash
# Local:
redis-server
# Ou usar REDIS_URL do Upstash no .env
```

## Scripts/Tools
- `execution/setup_env.py` — valida variáveis obrigatórias no `.env`
- `execution/test_connection.py` — testa conexão com Supabase
- `execution/run_migrations.py` — executa SQL de migrations

## Outputs
- Ambiente Python com venv e todas as dependências
- `.env` preenchido e validado
- Supabase configurado com tabelas criadas
- Frontend inicializado com Vite + React + TypeScript
- Redis rodando

## Edge Cases
- Se `pgvector` não estiver disponível: verificar se o plano do Supabase suporta extensões
- Se `sentence-transformers` falhar no install: verificar se PyTorch está instalado (`pip install torch`)
- Se porta 6543 não funcionar: testar com 5432 (conexão direta, sem pooling)
- Windows: usar `venv\Scripts\activate` ao invés de `source`
- **Aprendizado:** `sentence-transformers` pode levar tempo na 1ª execução para baixar o modelo (~90MB). O `setup_env.py` pode parecer travado durante esse download.
- **Aprendizado:** No bash do Windows, usar `python -m pip install` ao invés de paths diretos do venv.

## Dependências (requirements.txt)
```
google-genai>=1.0.0
sentence-transformers>=2.7.0
aiohttp>=3.9.0
pydantic>=2.7.0
redis>=5.0.0
supabase>=2.10.0
structlog>=24.0.0
python-dotenv>=1.0.0
pytest>=8.0.0
pytest-asyncio>=0.23.0
```
