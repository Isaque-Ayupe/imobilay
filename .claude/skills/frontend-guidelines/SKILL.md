---
name: frontend-guidelines
description: Diretrizes de desenvolvimento frontend do IMOBILAY — React 19 + TypeScript + TailwindCSS 4 + Framer Motion.
user-invocable: false
paths: "frontend/**/*.{ts,tsx,css,js,jsx}"
---

# Frontend Guidelines — IMOBILAY

## Stack

| Tecnologia | Versão | Uso |
|-----------|--------|-----|
| React | 19 | UI library |
| Vite | latest | Build tool |
| TypeScript | latest | Type safety |
| TailwindCSS | 4 | Styling |
| Framer Motion | latest | Animações |
| Lucide React | latest | Ícones |

## Convenções de Código

### Componentes

```typescript
// Nome: PascalCase, arquivo: PascalCase.tsx
interface PropertyCardProps {
  property: Property;
  onSelect: (id: string) => void;
}

export function PropertyCard({ property, onSelect }: PropertyCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-surface p-4 rounded-lg"
    >
      <h3 className="font-serif text-gold">{property.title}</h3>
      <p>{property.formattedPrice}</p>
      <button onClick={() => onSelect(property.id)}>
        Ver detalhes
      </button>
    </motion.div>
  );
}
```

### Tipografia

- **Cormorant Garamond** — títulos, nomes de propriedades (font-serif)
- **DM Sans** — texto corrido, labels, botões

### Tema (Cores)

| Token | Valor | Uso |
|-------|-------|-----|
| Navy | fundo principal | background |
| Surface | fundo de cards | cards, modais |
| Gold | destaque, CTAs | links, botões primários, scores |

## Estrutura do Frontend

```
frontend/
├── package.json
├── vite.config.ts
├── tailwind.config.ts (ou css)
├── index.html
├── src/
│   ├── App.tsx
│   ├── main.tsx
│   ├── components/    # Componentes reutilizáveis
│   ├── pages/         # Páginas/rotas
│   ├── hooks/         # Custom hooks
│   ├── types/         # TypeScript types/interfaces
│   ├── services/      # API calls (fetch para backend)
│   └── utils/         # Funções auxiliares
```

## Comandos

```bash
cd /c/imobilay/frontend
npm install        # Instalar dependências
npm run dev        # Dev server (localhost:5173)
npm run build      # Build de produção
npm run lint       # ESLint
npm run preview    # Preview do build
```

## Padrões

1. **Animações**: usar Framer Motion para transições suaves. Elementos devem aparecer com `initial={{ opacity: 0, y: 20 }}` e `animate={{ opacity: 1, y: 0 }}`.
2. **API calls**: usar `fetch` ou `httpx` (via serviço) para `/api/chat`, `/api/sessions`, `/api/health`.
3. **Estado**: priorizar React State local. Context API apenas para estado global compartilhado.
4. **Ícones**: sempre usar Lucide React — não usar emojis ou SVGs customizados sem necessidade.
5. **Responsividade**: Mobile-first com Tailwind breakpoints.
6. **Acessibilidade**: usar `aria-*` attributes, `role` quando necessário, semântica HTML correta.
