Você é um engenheiro frontend sênior especializado em produtos B2C com inteligência embarcada.
Crie uma aplicação React + Vite completa para o IMOBILAY — um consultor de investimentos 
imobiliários com interface de chat, onde a resposta não é geração livre de texto, mas sim 
uma análise estruturada formatada como linguagem natural.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STACK OBRIGATÓRIA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
- React 18 + Vite + TypeScript
- Framer Motion (todas as animações)
- Tailwind CSS v3
- Lucide React (ícones, com parcimônia)
- Fontes: Cormorant Garamond (display) + DM Sans (corpo) via @fontsource

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IDENTIDADE VISUAL — IMOBILAY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Tom: Consultoria de alto padrão. Confiança técnica, sem frieza. 
Pensa em uma intersecção entre um relatório da JLL e um produto 
consumer moderno — dados sérios, experiência fluida.

CSS Custom Properties:
:root {
  --gold:          #B8960C;
  --gold-light:    #F5EFC0;
  --gold-muted:    #7A6209;
  --navy:          #0D1B2A;
  --navy-mid:      #1A2D42;
  --surface:       #F9F8F6;  /* nunca branco puro */
  --surface-alt:   #F2F0EB;
  --border:        rgba(0,0,0,0.07);
  --border-mid:    rgba(0,0,0,0.12);
  --text-primary:  #0D1B2A;
  --text-muted:    #5A6470;
  --text-ghost:    #9BA4AE;
  --green:         #1D9E75;
  --green-light:   #E1F5EE;
  --coral:         #D85A30;
  --coral-light:   #FAECE7;
  --blue:          #185FA5;
  --blue-light:    #E6F1FB;
}

Tipografia:
- Logo/títulos de página: Cormorant Garamond 500–600, letter-spacing 0.02em
- Valores numéricos grandes: Cormorant Garamond 300, rendering óptico máximo
- Corpo/UI: DM Sans 300–500
- Labels uppercase: 9–10px, letter-spacing 0.16em
- Nenhum uso de Inter, Roboto, ou system-ui

Paleta de aplicação:
- Accent principal: --gold (#B8960C) — usado com extrema parcimônia
- Texto ativo/selecionado: --gold em fundo #B8960C0D
- Mensagens do usuário: fundo --navy, texto --surface
- Cards de análise: --surface-alt com borda 0.5px
- Scores positivos: --green / negativos: --coral
- Sem gradients, sem box-shadow > 8px blur

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LAYOUT GERAL
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

┌──────────────┬──────────────────────────────────┐
│   Sidebar    │           Chat Principal          │
│   210px      │  TopBar | Messages | Input        │
└──────────────┴──────────────────────────────────┘

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPONENTES — ESPECIFICAÇÃO DETALHADA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

── 1. SIDEBAR ──────────────────────────────────

Largura fixa 220px, height 100vh, border-right 0.5px.
Estrutura de cima para baixo:

┌─────────────────────────────────────────────┐
│  Logo  "IMOBILAY"          [+ nova]          │
├─────────────────────────────────────────────┤
│  ◉  Nova análise   (ação, sempre visível)   │
│  🔔  Alertas        (ação, sempre visível)   │
├─────────────────────────────────────────────┤
│                                             │
│  HOJE                                       │
│  · 2 quartos Pinheiros até 800k    agora    │
│  · Kitnet Vila Madalena aluguel    3h       │
│                                             │
│  ONTEM                                      │
│  · Cobertura Moema investimento    19h      │
│  · Studio Itaim ROI comparativo    14h      │
│                                             │
│  ESTA SEMANA                                │
│  · Apartamentos Brooklin 3 quartos seg      │
│  · ...                                      │
│                                             │
│  (scroll independente, sem barra visível)   │
│                                             │
├─────────────────────────────────────────────┤
│  [RC]  Rafael Costa         ···             │
│        Pro · 14 análises                    │
└─────────────────────────────────────────────┘

LOGO + BOTÃO NOVA ANÁLISE:
  - "IMOBI" text-primary + "LAY" em --gold, Cormorant 20px
  - Botão [+] no canto direito: 28px, border 0.5px, border-radius 6px
    Framer Motion: whileHover scale(1.05), whileTap scale(0.95)
    Ao clicar: abre nova conversa e seleciona no histórico

AÇÕES FIXAS (abaixo do logo, acima do histórico):
  Dois itens sempre visíveis, não entram no scroll:
  
  1. "Nova análise" — ícone MessageSquare (Lucide)
     Sempre no topo, cria nova sessão de chat
  
  2. "Alertas" — ícone Bell (Lucide)
     Badge numérico dourado se houver alertas não lidos
     ex: "3" em círculo 14px, fundo --gold, texto branco
  
  Item ativo: background #B8960C0D, texto --gold, font-weight 500
  Item hover: background --surface-alt
  Separador 0.5px entre ações e histórico

HISTÓRICO DE CONVERSAS (estilo claude.ai):
  - Ocupa todo o espaço restante com overflow-y: auto
  - Scroll customizado: scrollbar-width 3px, thumb --border-mid
  - Agrupado por período com label uppercase 9px ghost:
      HOJE / ONTEM / ESTA SEMANA / MESES ANTERIORES (ex: MARÇO)
  
  Cada item de histórico:
    - Dot 4px (--text-tertiary normal, --gold se for conversa atual)
    - Texto truncado com text-overflow: ellipsis, font-size 12px
    - Timestamp à direita: 10px --text-ghost
      Formato: "agora" | "3h" | "19h" | "seg" | "12/03"
    - Hover: background --surface-alt
    - Conversa ativa: background #B8960C0D, texto --text-primary, 
      dot --gold, font-weight 500
    - Ao hover: mostrar ícone de lixeira (Trash2 Lucide) 14px 
      que aparece com opacity transition 0ms→200ms

  Framer Motion no item ativo:
    layoutId="active-conversation" para transição suave

USER FOOTER (canto inferior esquerdo):
  - Sempre fixo no bottom, border-top 0.5px
  - Avatar 30px com iniciais, border-radius 50%
  - Nome: 12px font-weight 500
  - Plano: 10px --gold (ex: "Pro · 14 análises")
  - Ícone ··· (MoreVertical Lucide) à direita
  - Cursor pointer, hover: background --surface-alt
  
  AO CLICAR: abre Popover flutuando ACIMA do footer
  (position absolute, bottom: footer-height + 8px, z-index 50)
  
  Popover (border 0.5px, border-radius 8px, padding 6px,
           background --surface, box-shadow sutil):
    ┌──────────────────────────────┐
    │  👤  Preferências            │
    │  💳  Plano & cobrança        │
    │  ─────────────────────────  │
    │  ↪  Sair          (coral)   │
    └──────────────────────────────┘
  
  Framer Motion no popover:
    initial={{ opacity: 0, y: 6, scale: 0.97 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    exit={{ opacity: 0, y: 4, scale: 0.97 }}
    transition={{ duration: 0.15, ease: [0.16, 1, 0.3, 1] }}
  
  Fechar ao clicar fora (useClickOutside hook)

TIPO TYPESCRIPT para histórico:
  interface ConversationItem {
    id: string
    title: string           // gerado automaticamente da 1ª mensagem
    lastMessage: Date
    messageCount: number
    isActive: boolean
  }
  
  type HistoryGroup = {
    label: 'Hoje' | 'Ontem' | 'Esta semana' | string  // mês para mais antigas
    conversations: ConversationItem[]
  }
  
  // Hook para agrupar por período
  function groupConversationsByDate(convs: ConversationItem[]): HistoryGroup[]

── 2. TOPBAR ───────────────────────────────────

  - Título da conversa: Cormorant Garamond 22px
    (default "Nova análise", editável ao renomear)
  - Status pill direita: dot verde animado (pulse suave) + 
    "Sistema online" | "Analisando..." | "Aguardando dados"
  - Border-bottom 0.5px

── 3. ÁREA DE MENSAGENS ────────────────────────

Mensagem do usuário (alinhada à direita):
  - Bubble com fundo --navy, texto --surface
  - Border-radius: 14px 14px 3px 14px
  - Font-size 13px, line-height 1.5
  - Framer Motion: slide-up + fade-in ao aparecer

Resposta do IMOBILAY (alinhada à esquerda):
  
  A. PIPELINE INDICATOR (sempre aparece primeiro):
     Chips horizontais mostrando as fases do pipeline:
     [Busca] › [Normalização] › [Precificação] › [ROI] › [Ranking]
     
     Estados de cada chip:
       done:    fundo --green-light, texto --green, borda verde sutil
       active:  fundo --gold-light, texto --gold-muted, borda dourada
       pending: fundo transparente, texto --text-ghost, borda 0.5px
     
     Animação: chips aparecem em stagger com Framer Motion.
     O chip "active" pulsa levemente (scale 1 → 1.02 → 1, loop).
     Ao concluir, todos ficam "done" e o card de análise surge.
  
  B. TEXTO INTRODUTÓRIO:
     Bubble simples: fundo --surface, borda 0.5px, 
     border-radius 3px 14px 14px 14px
     Texto gerado pelo LLM contextualizando a análise.
  
  C. ANÁLISE CARD (PropertyAnalysisCard):
     Aparece após o texto com Framer Motion:
       initial={{ opacity: 0, y: 12 }}
       animate={{ opacity: 1, y: 0 }}
       transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
     
     Estrutura do card:
     ┌──────────────────────────────────────────┐
     │ [Endereço — Cormorant 16px]   [Oport. tag]│
     │ 2 quartos · 68m² · 1 vaga · 4º andar     │
     ├──────────────────────────────────────────┤
     │  Preço pedido  │  Preço justo  │  ROI     │
     │  R$749k        │  R$791k ↑    │  6,2% a.a│
     │  R$11.014/m²   │  +5,6% margem│  estimado│
     ├──────────────────────────────────────────┤
     │ Localização    ████████░░  8,8            │
     │ Preço vs merc. █████████░  9,2            │
     │ Liquidez       ███████░░░  7,5            │
     ├──────────────────────────────────────────┤
     │ [Ver detalhes]    [Salvar]   [Comparar]   │
     └──────────────────────────────────────────┘
     
     Score bars: animam width de 0% ao valor (stagger 80ms, ease-out)
     Preço justo: se acima do pedido → --green, se abaixo → --coral
     Tag de oportunidade: pill verde quando preço pedido < preço justo
  
  D. CONFIDENCE GATE (estado especial):
     Quando o sistema não tem dados suficientes:
     Card com borda --gold, ícone de alerta dourado e mensagem
     clara: "Dados insuficientes para [região/tipo]" + sugestão 
     de como refinar a busca. Nunca mensagem genérica de erro.

── 4. INPUT DE CHAT ────────────────────────────

  - Input full-width, borda 0.5px, border-radius 8px
  - Placeholder: "Faça uma nova pergunta ou refine a busca…"
  - Botão send: fundo --navy, ícone seta, border-radius 8px
  - Enquanto pipeline roda: botão desabilitado, input mostra 
    "Analisando…" como placeholder
  - Framer Motion: o botão send faz scale(0.95) no click

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTADOS DE LOADING — FASES DO PIPELINE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

O loading NÃO é um spinner genérico. Reflete as fases reais:

type PipelinePhase = 
  'idle' | 'routing' | 'searching' | 'normalizing' | 
  'pricing' | 'roi' | 'ranking' | 'generating' | 'done' | 'limited'

Sequência visual:
  1. Usuário envia → input desabilita, topbar muda para "Analisando…"
  2. Chips do pipeline aparecem em stagger (100ms cada)
  3. Cada chip ativa em sequência com delay simulado realista
  4. Ao chegar em "generating": typing indicator (3 dots pulsando)
  5. Texto aparece → PropertyAnalysisCard surge com animação

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIPOS TYPESCRIPT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

interface PropertyAnalysis {
  id: string
  address: string
  neighborhood: string
  specs: { rooms: number; area: number; parking: number; floor: number }
  pricing: {
    listed: number        // preço pedido
    fair: number          // preço justo calculado
    pricePerSqm: number
    margin: number        // % diferença listed vs fair
    opportunity: boolean  // fair > listed
  }
  roi: {
    annual: number        // % a.a. estimado aluguel
    paybackYears: number
  }
  scores: {
    location: number      // 0–10
    priceVsMarket: number
    liquidity: number
  }
  totalScore: number      // média ponderada
  tag?: 'opportunity' | 'overpriced' | 'fair'
}

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  analysis?: PropertyAnalysis
  pipeline?: PipelinePhase
  limited?: boolean       // confidence gate ativado
  timestamp: Date
}

interface UserProfile {
  name: string
  initials: string
  plan: 'free' | 'pro' | 'elite'
  analysisCount: number
  preferences: {
    maxBudget?: number
    preferredAreas?: string[]
    minRooms?: number
    investmentGoal?: 'rental' | 'appreciation' | 'both'
  }
}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
MOCK DATA
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const mockAnalysis: PropertyAnalysis = {
  id: "prop-001",
  address: "Alameda Lorena, 1.240",
  neighborhood: "Pinheiros, SP",
  specs: { rooms: 2, area: 68, parking: 1, floor: 4 },
  pricing: {
    listed: 749000,
    fair: 791000,
    pricePerSqm: 11014,
    margin: 5.6,
    opportunity: true
  },
  roi: { annual: 6.2, paybackYears: 16.1 },
  scores: { location: 8.8, priceVsMarket: 9.2, liquidity: 7.5 },
  totalScore: 8.5,
  tag: 'opportunity'
}

const initialMessages: Message[] = [
  {
    id: "1",
    role: "user",
    content: "Quero um apartamento de 2 quartos em Pinheiros, SP. Orçamento até R$800k. O que vale a pena?",
    timestamp: new Date()
  },
  {
    id: "2",
    role: "assistant",
    content: "Encontrei 38 imóveis em Pinheiros dentro do seu orçamento. Após análise de preço justo e ROI, este se destacou como a melhor oportunidade do momento:",
    analysis: mockAnalysis,
    pipeline: 'done',
    timestamp: new Date()
  }
]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ANIMAÇÕES — ESPECIFICAÇÃO FRAMER MOTION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

const luxEase = [0.16, 1, 0.3, 1]
const springSnappy = { type: "spring", stiffness: 280, damping: 26 }

1. Mensagem nova: { initial: {opacity:0, y:14}, animate: {opacity:1,y:0}, 
   transition: {duration:0.4, ease: luxEase} }

2. Pipeline chips: stagger 0.08s por chip, slide-up + fade

3. Score bars: animate de 0 ao valor via motion.div width,
   delay staggered 80ms, transition {duration:0.7, ease:"easeOut"}

4. Chip "active": keyframes scale [1, 1.03, 1], repeat Infinity, duration 1.6s

5. Dot de status online: keyframes opacity [1, 0.4, 1], repeat Infinity, duration 2s

6. Send button: whileTap={{ scale: 0.93 }}, transition: springSnappy

7. PropertyAnalysisCard: layoutId para expandir ao clicar em "Ver detalhes"
   (AnimateSharedLayout ou LayoutGroup do Framer Motion)

8. Sidebar active dot: layoutId="active-dot", move suavemente entre items

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ESTRUTURA DE ARQUIVOS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

src/
  types/
    index.ts                ← todos os tipos TS
  components/
    layout/
      Sidebar.tsx
      TopBar.tsx
    chat/
      MessageList.tsx
      MessageBubble.tsx
      ChatInput.tsx
      PipelineIndicator.tsx  ← chips de fase
      TypingIndicator.tsx
    analysis/
      PropertyAnalysisCard.tsx
      ScoreBar.tsx
      MetricCell.tsx
      ConfidenceGate.tsx     ← estado de dados insuficientes
  hooks/
    useChat.ts               ← lógica de mensagens + pipeline mock
    usePipeline.ts           ← sequência de fases com delays
  data/
    mock.ts                  ← dados fake para dev
  styles/
    globals.css              ← CSS custom properties + reset
  App.tsx
  main.tsx

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
REGRAS ABSOLUTAS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. NUNCA spinner genérico — o loading SEMPRE reflete as fases do pipeline
2. NUNCA mensagem de erro genérica — o ConfidenceGate é específico e educativo
3. Toda animação com easing personalizado — zero linear ou ease padrão
4. Números formatados sempre: Intl.NumberFormat para moeda, toFixed(1) para %
5. O chat é scroll-anchored: nova mensagem sempre puxa o scroll para baixo
6. PropertyAnalysisCard é o componente mais importante — polimento máximo
7. Responsivo: sidebar vira overlay em mobile com hamburger
8. Fontes nunca Inter, Roboto, system-ui
9. Entregue código completo, funcional, sem placeholders nem TODOs

Entregue todos os arquivos com código real e funcional.