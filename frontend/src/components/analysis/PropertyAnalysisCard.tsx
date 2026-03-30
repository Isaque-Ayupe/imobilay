import { useState, memo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MapPin, Maximize2, ExternalLink, BookmarkPlus, ArrowRightLeft } from 'lucide-react';
import type { Property, ValuationResult, InvestmentResult, Opportunity, RankingJustificativa } from '../../types';
import { MetricCell } from './MetricCell';
import { ScoreBar } from './ScoreBar';

interface PropertyAnalysisCardProps {
  property: Property;
  valuation?: ValuationResult;
  investment?: InvestmentResult;
  opportunity?: Opportunity;
  ranking?: RankingJustificativa;
}

// ⚡ Bolt Optimization:
// React.memo prevents the PropertyAnalysisCard from unnecessarily re-rendering
// when parent components update without changing the property props.
export const PropertyAnalysisCard = memo(function PropertyAnalysisCard({
  property, 
  valuation, 
  investment,
  opportunity,
  ranking 
}: PropertyAnalysisCardProps) {
  const [expanded, setExpanded] = useState(false);

  const formatCurrency = (value: number) => 
    new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL', maximumFractionDigits: 0 }).format(value);

  return (
    <motion.div 
      layoutId={`card-${property.id}`}
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
      className="w-full bg-surface-alt border-[0.5px] border-border-mid rounded-xl overflow-hidden shadow-sm my-4"
    >
      {/* HEADER */}
      <div className="p-4 border-b-[0.5px] border-border bg-gradient-to-br from-surface to-surface-alt">
        <div className="flex justify-between items-start mb-2">
          <div className="flex flex-col gap-1">
            <h3 className="font-display text-xl text-text-primary font-semibold tracking-[0.02em]">
              {property.address}
            </h3>
            <div className="flex items-center gap-1.5 text-text-muted text-xs">
              <MapPin className="w-3.5 h-3.5" />
              <span>{property.neighborhood}, {property.city}</span>
            </div>
          </div>
          
          {opportunity && (
            <div className="px-2.5 py-1 rounded-full bg-green-light border border-green/20">
              <span className="text-[10px] uppercase tracking-wider font-semibold text-green">
                Oportunidade
              </span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2 mt-3 text-sm text-text-muted">
          <span>{property.rooms} quartos</span>
          <span className="text-border-mid">•</span>
          <span>{property.area}m²</span>
          <span className="text-border-mid">•</span>
          <span>{property.parking} vagas</span>
          {property.floor && (
            <>
              <span className="text-border-mid">•</span>
              <span>{property.floor}º andar</span>
            </>
          )}
        </div>
      </div>

      {/* MÉTRICAS PRINCIPAIS */}
      <div className="p-4 grid grid-cols-1 md:grid-cols-3 gap-3 border-b-[0.5px] border-border bg-surface/50">
        <MetricCell 
          label="Preço Pedido" 
          value={formatCurrency(property.price)} 
          subValue={`${formatCurrency(property.price_per_sqm)}/m²`}
        />
        
        {valuation ? (
          <MetricCell 
            label="Preço Justo" 
            value={formatCurrency(valuation.preco_justo)} 
            subValue={`${Math.abs(valuation.desvio_percentual).toFixed(1)}% ${valuation.desvio_percentual < 0 ? 'abaixo do mercado' : 'acima do mercado'}`}
            highlight={valuation.desvio_percentual < -5 ? 'green' : (valuation.desvio_percentual > 5 ? 'coral' : 'neutral')}
          />
        ) : (
          <MetricCell label="Preço Justo" value="N/A" subValue="Sem dados suficientes" />
        )}

        {investment ? (
          <MetricCell 
            label="ROI Anual" 
            value={`${investment.roi_anual.toFixed(1)}%`} 
            subValue={`Est. ${formatCurrency(investment.aluguel_estimado)}/mês`}
            highlight={investment.roi_anual > 5 ? 'green' : 'neutral'}
          />
        ) : (
          <MetricCell label="Investimento" value="N/A" subValue="Sem projeção" />
        )}
      </div>

      {/* SCORES BARS */}
      {property.location_insights && (
        <div className="p-4 px-5 border-b-[0.5px] border-border bg-surface">
          <ScoreBar 
            label="Localização e Infra" 
            score={property.location_insights.bairro_score} 
            delay={0.1} 
          />
          {valuation && (
            <ScoreBar 
              label="Preço vs Mercado" 
              score={Math.max(0, 10 - (valuation.desvio_percentual / 5))} 
              delay={0.2} 
            />
          )}
          <ScoreBar 
            label="Liquidez Estimada" 
            score={property.location_insights.liquidez_estimada === 'alta' ? 9 : (property.location_insights.liquidez_estimada === 'media' ? 6 : 3)} 
            delay={0.3} 
          />
        </div>
      )}

      {/* DETALHES EXPANSÍVEIS */}
      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="overflow-hidden bg-surface-alt/50 border-b-[0.5px] border-border"
          >
            <div className="p-4 px-5 text-sm text-text-muted space-y-3">
              {opportunity?.motivo && (
                <div>
                  <h4 className="text-xs uppercase tracking-widest text-text-ghost font-medium mb-1">Motivo da Recomendação</h4>
                  <p>{opportunity.motivo}</p>
                </div>
              )}
              {ranking?.resumo && !opportunity?.motivo && (
                <div>
                  <h4 className="text-xs uppercase tracking-widest text-text-ghost font-medium mb-1">Resumo do Ranking</h4>
                  <p>{ranking.resumo}</p>
                </div>
              )}
              <div className="pt-2">
                {/* 🛡️ Sentinel: Sanitize URL to prevent javascript: XSS */}
                <a 
                  href={property.url?.startsWith('http') ? property.url : '#'}
                  target="_blank" 
                  rel="noreferrer"
                  className="flex items-center gap-1.5 text-blue hover:text-blue-light transition-colors text-xs font-medium w-fit"
                >
                  <ExternalLink className="w-3.5 h-3.5" />
                  Ver anúncio original
                </a>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* FOOTER ACTIONS */}
      <div className="flex p-2 bg-surface">
        <button 
          onClick={() => setExpanded(!expanded)}
          className="flex-1 flex items-center gap-1.5 justify-center py-2 px-3 text-xs font-medium text-text-muted hover:text-text-primary hover:bg-surface-alt rounded-md transition-all"
        >
          <Maximize2 className="w-3.5 h-3.5" />
          {expanded ? 'Mostrar menos' : 'Ver detalhes'}
        </button>
        <button className="flex-1 flex items-center gap-1.5 justify-center py-2 px-3 text-xs font-medium text-text-muted hover:text-[var(--gold)] hover:bg-[var(--gold)]/5 rounded-md transition-all">
          <BookmarkPlus className="w-3.5 h-3.5" />
          Salvar
        </button>
        <button className="flex-1 flex items-center gap-1.5 justify-center py-2 px-3 text-xs font-medium text-text-muted hover:text-blue hover:bg-blue/5 rounded-md transition-all">
          <ArrowRightLeft className="w-3.5 h-3.5" />
          Comparar
        </button>
      </div>
    </motion.div>
  );
});
