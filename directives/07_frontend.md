# Directive 07 — Frontend (React + Vite)

## Objetivo
Implementar a interface de chat premium do IMOBILAY: layout com Sidebar + Chat, componentes de análise e animações Framer Motion.

## Inputs
- Especificação completa em `context/imobilay_front.md`
- Backend funcionando com API (Directive 08)

## Scripts/Tools
- Nenhum — implementação direta no frontend

## Stack
- React 18 + Vite + TypeScript
- Framer Motion (todas as animações)
- Tailwind CSS v3
- Lucide React (ícones, com parcimônia)
- Fontes: Cormorant Garamond (display) + DM Sans (corpo) via @fontsource
- **NUNCA** Inter, Roboto ou system-ui

## Estrutura de Arquivos

```
src/
├── types/index.ts                    ← PropertyAnalysis, Message, UserProfile
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx               ← Logo, ações fixas, histórico, user footer
│   │   └── TopBar.tsx                ← Título, status pill
│   ├── chat/
│   │   ├── MessageList.tsx           ← Lista de mensagens com scroll anchoring
│   │   ├── MessageBubble.tsx         ← Bubble user (navy) e assistant (surface)
│   │   ├── ChatInput.tsx             ← Input + botão send
│   │   ├── PipelineIndicator.tsx     ← Chips de fases do pipeline
│   │   └── TypingIndicator.tsx       ← 3 dots pulsando
│   └── analysis/
│       ├── PropertyAnalysisCard.tsx   ← Card principal de análise
│       ├── ScoreBar.tsx              ← Barra animada de score
│       ├── MetricCell.tsx            ← Célula de métrica (preço, ROI)
│       └── ConfidenceGate.tsx        ← Estado de dados insuficientes
├── hooks/
│   ├── useChat.ts                    ← Lógica de mensagens + pipeline mock
│   └── usePipeline.ts               ← Sequência de fases com delays
├── data/mock.ts                      ← Dados fake para dev
├── styles/globals.css                ← CSS custom properties + reset
├── App.tsx
└── main.tsx
```

## Identidade Visual (CSS Custom Properties)

```css
:root {
  --gold: #B8960C;          --gold-light: #F5EFC0;     --gold-muted: #7A6209;
  --navy: #0D1B2A;          --navy-mid: #1A2D42;
  --surface: #F9F8F6;       --surface-alt: #F2F0EB;
  --border: rgba(0,0,0,0.07);  --border-mid: rgba(0,0,0,0.12);
  --text-primary: #0D1B2A;  --text-muted: #5A6470;     --text-ghost: #9BA4AE;
  --green: #1D9E75;         --green-light: #E1F5EE;
  --coral: #D85A30;         --coral-light: #FAECE7;
  --blue: #185FA5;          --blue-light: #E6F1FB;
}
```

## Componentes Críticos

### PropertyAnalysisCard
O componente **mais importante** — polimento máximo.
- Endereço (Cormorant 16px), tag de oportunidade
- Specs: quartos, m², vagas, andar
- Métricas: preço pedido, preço justo (verde se acima, coral se abaixo), ROI
- Score bars animadas: Localização, Preço vs Mercado, Liquidez
- Botões: Ver detalhes, Salvar, Comparar
- Framer Motion: `layoutId` para expandir ao clicar "Ver detalhes"

### PipelineIndicator
Chips: `[Busca] › [Normalização] › [Precificação] › [ROI] › [Ranking]`
Estados: done (verde), active (dourado, pulsando), pending (ghost)
Stagger de 0.08s por chip.

### Sidebar
Layout vertical fixo (220px) com scroll independente no histórico.
Estilo Claude.ai: agrupado por Hoje/Ontem/Esta Semana/Meses.

## Animações (Framer Motion)

```typescript
const luxEase = [0.16, 1, 0.3, 1]
const springSnappy = { type: "spring", stiffness: 280, damping: 26 }
```

| Componente | Animação |
|---|---|
| Mensagem nova | slide-up + fade-in (0.4s, luxEase) |
| Pipeline chips | stagger 0.08s, slide-up + fade |
| Score bars | width 0→valor, stagger 80ms, 0.7s ease-out |
| Chip ativo | scale [1, 1.03, 1], loop, 1.6s |
| Status dot | opacity [1, 0.4, 1], loop, 2s |
| Send button | whileTap scale(0.93), springSnappy |
| Analysis card | layoutId para animação de expansão |

## Regras Absolutas
1. NUNCA spinner genérico — loading reflete fases reais do pipeline
2. NUNCA mensagem de erro genérica — ConfidenceGate é específico e educativo
3. Toda animação com easing personalizado — zero linear
4. Números formatados: `Intl.NumberFormat` para moeda, `toFixed(1)` para %
5. Scroll-anchored: nova mensagem puxa scroll para baixo
6. Responsivo: sidebar vira overlay em mobile com hamburger
7. Código completo, funcional, sem placeholders nem TODOs

## Outputs
- Frontend completo e funcional
- Todos os componentes com animações Framer Motion
- Mock data para desenvolvimento independente do backend
- Responsivo (desktop + mobile)

## Edge Cases
- Mobile (<768px): sidebar vira overlay com botão hamburger
- Mensagem muito longa: truncar no histórico da sidebar com ellipsis
- PropertyAnalysisCard com dados parciais (fallback): mostrar campos disponíveis, omitir o rest
- Pipeline com fase falhada: chip fica vermelho (coral) em vez de verde
