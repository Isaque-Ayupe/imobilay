# Agentes Especialistas (Agents)

Este diretório contém a implementação dos diversos agentes especialistas do Imobilay.

## Arquivos e suas Funções

- **[__init__.py](file:///c:/imobilay/layer_2_orchestrator/agents/__init__.py)**: Exporta os agentes para o pacote.
- **[base_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/base_agent.py)**: Definição da classe base `BaseAgent` que todos os outros agentes devem herdar.
- **[compare_properties_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/compare_properties_agent.py)**: Agente para comparar múltiplos imóveis.
- **[investment_analysis_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/investment_analysis_agent.py)**: Agente para análise de ROI, payback e rentabilidade.
- **[location_insights_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/location_insights_agent.py)**: Agente para análise de localização e infraestrutura.
- **[normalize_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/normalize_agent.py)**: Agente para normalização de dados de imóveis.
- **[opportunity_detection_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/opportunity_detection_agent.py)**: Agente para detecção de oportunidades de investimento.
- **[valuation_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/valuation_agent.py)**: Agente para avaliação de preço de mercado.
- **[web_scraper_agent.py](file:///c:/imobilay/layer_2_orchestrator/agents/web_scraper_agent.py)**: Agente para extração de dados de imóveis de fontes externas.

## Funcionamento no Projeto

Os agentes especialistas são as unidades de execução do Imobilay. Cada um é especializado em uma tarefa específica (ex: análise de preço, localização, investimento). Eles são orquestrados pela Camada 2 para realizar o trabalho necessário para responder ao usuário. O uso de agentes especializados permite que cada um seja otimizado e testado individualmente, garantindo a qualidade e confiabilidade do sistema.
