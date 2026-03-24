# IMOBILAY

**Consultor Inteligente de Investimentos Imobiliários**

O IMOBILAY é uma plataforma completa de consultoria imobiliária baseada em inteligência artificial. A proposta é entregar análises estruturadas e fundamentadas em dados — não texto livre gerado por IA — através de uma interface de chat premium, similar a um relatório da JLL com a fluidez de um produto moderno.

---

## 📋 Escopo Atual do Projeto

O projeto foi inteiramente arquitetado sob um princípio de **Sistema Multi-Agente Determinístico**. Diferente de chatbots tradicionais que dependem exclusivamente de LLMs para todas as decisões, o IMOBILAY restringe o LLM apenas à **verbalização final**, enquanto toda a lógica analítica roda em scripts Python independentes.

O escopo está estruturado em 3 grandes camadas no Backend e uma interface Frontend premium:

### 1. Camada 1: Entrada e Roteamento
- **Roteamento Semântico:** Identifica intenções do usuário (ex: *busca, valuation, análise de ROI*) usando Embeddings locais (`sentence-transformers`), não LLM.
- **DAG Resolver:** Monta um Grafo Direcionado Acíclico (DAG) com base nas intenções capturadas, desenhando as etapas que os agentes deverão seguir em paralelo ou em sequência.

### 2. Camada 2: Orquestrador e Agentes Especializados
- **Orquestrador:** Executa o DAG paralelizando o que for possível. Se a busca precisa de precificação e ROI, os agentes rodam simultaneamente usando `asyncio`.
- **7 Agentes de Negócios:** WebScraper (Busca), Normalize (Limpeza), Location (Geolocalização e Insights do IBGE/OSM), Valuation (Preço Justo), Investment (ROI, Payback), Opportunity (Achar a "pechincha") e Compare (Ranking Final).
- **Confidence Gate:** Uma trava de segurança. O LLM só emite uma resposta se o contexto coletado tiver dados sólidos. Se não tiver, o gate aciona um pedido de detalhes sem envolver tokens caros.

### 3. Camada 3: Aprendizado e Observabilidade
- **Memória & Cache:** Histórico de conversas por sessão (Memória de Curto Prazo) e perfil do investidor (Memória de Longo Prazo), armazenados com Supabase e Redis.
- **Circuit Breaker:** Garante que o sistema nunca trave. Se alguma API de terceiros falhar continuamente, a resiliência adapta o caminho sem quebrar a jornada do usuário.

### 4. Frontend: Interface Premium
- **React + Vite + TypeScript** rodando uma UI sofisticada focada em tipografia (Cormorant Garamond/DM Sans) e paletas escuras elegantes (Navy, Surface, Gold).
- **Framer Motion** dá vida ao chat com indicadores de pipeline realistas (`[Busca] › [Precificação] › [ROI]`) em estilo cascata, finalizando com a expansão de "Property Cards" matemáticos.

---

## 🚀 Como Rodar o Projeto Localmente

O IMOBILAY é desacoplado (API Backend + SPA Frontend). Siga os passos abaixo para testá-lo ou contribuir.

### Passo 1: Configurar Variáveis de Ambiente

Crie ou edite o arquivo `.env` na pasta raiz (`c:\imobilay\.env`) adicionando suas apikeys reais. Há um `.env.example` disponível como molde.
```env
# Essencial para o Response Verbalizer (LLM Final)
GEMINI_API_KEY=sua-chave-aqui 
# Repositório de Memória / Busca
SUPABASE_URL=url_aqui
SUPABASE_SERVICE_KEY=key_aqui
```

### Passo 2: Rodar o Backend Institucional (FastAPI)

Abra o seu terminal na pasta do projeto e inicie o ambiente virtual e a API.

```bash
# Navegue até a pasta do projeto
cd c:\imobilay

# Instale os requisitos
pip install -r requirements.txt fastapi uvicorn

# Suba a API na porta 8000
uvicorn api:app --reload --port 8000
```
> **Nota de Teste:** O servidor estará disponível em `http://localhost:8000`. Você pode conferir a documentação gerada instantaneamente do Swagger em `http://localhost:8000/docs`.

### Passo 3: Rodar o Frontend Inteligente (React/Vite)

Abra um **segundo terminal** para servir a interface visual:

```bash
# Vá para a pasta web
cd c:\imobilay\frontend

# Instalar Node Modules
npm install

# Subir servidor Vite
npm run dev
```
> O painel do Vite abrirá e fornecerá o endereço do site, usualmente `http://localhost:5173`. Você já poderá conversar com a interface que se conectará naturalmente à sua instância FastAPI local!

### Adicional: CLI de Testes E2E (Rodando sem Browser)

Se quiser testar a arquitetura inteira (`Orquestrador -> DAG -> Agentes -> Gate -> LLM`) puramente no servidor sem interagir com o Front:

```bash
cd c:\imobilay
python main.py "quero um flat perto do Ibirapuera para eu investir até uns 850 mil"
```
A Engine vai printar todo o processo de decisão no terminal e entregar a reposta mastigada de modo cru e rápido.

---

*Copyright © 2026 - IMOBILAY*
