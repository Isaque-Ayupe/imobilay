import type { ContextData, SessionInfo } from '../types';

export const MOCK_CONTEXT_DATA: ContextData = {
  properties: [
    {
      id: "prop-001",
      address: "Rua dos Pinheiros, 1240",
      neighborhood: "Pinheiros",
      city: "São Paulo",
      rooms: 2,
      area: 68,
      parking: 1,
      floor: 5,
      price: 749000,
      price_per_sqm: 11014.7,
      property_type: 'apartamento',
      source: 'zap',
      url: "https://example.com/imovel1",
      location_insights: {
        bairro_score: 8.5,
        seguranca_index: 7.0,
        liquidez_estimada: "alta",
        infraestrutura_proxima: ["metrô", "parque", "hospital", "shopping"]
      }
    },
    {
      id: "prop-002",
      address: "Rua Fradique Coutinho, 500",
      neighborhood: "Pinheiros",
      city: "São Paulo",
      rooms: 2,
      area: 72,
      parking: 2,
      floor: 12,
      price: 880000,
      price_per_sqm: 12222.2,
      property_type: 'apartamento',
      source: 'vivareal',
      url: "https://example.com/imovel2",
      location_insights: {
        bairro_score: 8.5,
        seguranca_index: 7.0,
        liquidez_estimada: "alta",
        infraestrutura_proxima: ["metrô", "restaurantes"]
      }
    }
  ],
  analysis: {
    valuation: [
      {
        property_id: "prop-001",
        preco_justo: 850000,
        preco_justo_por_sqm: 12500,
        desvio_percentual: -11.9,
        classificacao: "barato",
        comparaveis_usados: 12
      },
      {
        property_id: "prop-002",
        preco_justo: 900000,
        preco_justo_por_sqm: 12500,
        desvio_percentual: -2.2,
        classificacao: "justo",
        comparaveis_usados: 12
      }
    ],
    investment: [
      {
        property_id: "prop-001",
        aluguel_estimado: 2996,
        roi_mensal: 0.4,
        roi_anual: 4.8,
        payback_anos: 20.8,
        potencial_valorizacao: 'alto'
      },
      {
        property_id: "prop-002",
        aluguel_estimado: 3520,
        roi_mensal: 0.4,
        roi_anual: 4.8,
        payback_anos: 20.8,
        potencial_valorizacao: 'alto'
      }
    ],
    opportunities: [
      {
        property_id: "prop-001",
        score_composto: 8.2,
        desvio_percentual: -11.9,
        liquidez: "alta",
        location_score: 8.5,
        motivo: "Preço 11% abaixo do justo, liquidez alta e score de bairro 8.5/10."
      }
    ],
    ranking: {
      melhor_opcao: "prop-001",
      total_avaliados: 2,
      ranking: [
        {
          property_id: "prop-001",
          score_total: 8.4,
          score_preco: 8.0,
          score_localizacao: 8.5,
          score_investimento: 7.5,
          score_oportunidade: 8.2,
          resumo: "Excelente oportunidade por desvio negativo de preço com alta liquidez."
        },
        {
          property_id: "prop-002",
          score_total: 7.6,
          score_preco: 5.5,
          score_localizacao: 8.5,
          score_investimento: 7.5,
          score_oportunidade: 0,
          resumo: "Imóvel dentro do preço justo de mercado, boa liquidez e localização."
        }
      ]
    }
  }
};

export const MOCK_HISTORY: SessionInfo[] = [
  { id: "sess-01", title: "2 quartos Pinheiros até 800k", timestamp: new Date(Date.now() - 1000 * 60 * 5), isToday: true },
  { id: "sess-02", title: "Kitnet Vila Madalena aluguel", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 3), isToday: true },
  { id: "sess-03", title: "Cobertura Moema investimento", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 19), isYesterday: true },
  { id: "sess-04", title: "Studio Itaim ROI comparativo", timestamp: new Date(Date.now() - 1000 * 60 * 60 * 24 * 3) }
];
