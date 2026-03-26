# Camada 2: Orquestrador (Orchestrator Layer)

Este diretório contém a lógica de orquestração do sistema, responsável por coordenar a execução de diversos agentes.

## Arquivos e suas Funções

- **[__init__.py](file:///c:/imobilay/layer_2_orchestrator/__init__.py)**: Inicialização do pacote.
- **[confidence_gate.py](file:///c:/imobilay/layer_2_orchestrator/confidence_gate.py)**: Verifica o nível de confiança das respostas dos agentes, garantindo que a resposta final seja confiável.
- **[orchestrator.py](file:///c:/imobilay/layer_2_orchestrator/orchestrator.py)**: Supervisor Agent que executa o DAG (Grafo Acíclico Dirigido) de agentes, coordenando paralelismo e sequencialismo.
- **[resilience_manager.py](file:///c:/imobilay/layer_2_orchestrator/resilience_manager.py)**: Gerencia a resiliência do sistema, aplicando retentativas e fallbacks em caso de falha de agentes.
- **[response_verbalizer.py](file:///c:/imobilay/layer_2_orchestrator/response_verbalizer.py)**: Formata a resposta final para o usuário, integrando os resultados dos diversos agentes de forma coerente.

## Diretórios

- **[agents/](file:///c:/imobilay/layer_2_orchestrator/agents)**: Implementação dos diversos agentes especialistas do Imobilay.

## Funcionamento no Projeto

A Camada 2 é o cérebro do Imobilay. Ela recebe o plano de execução (DAG) da Camada 1 e coordena os diversos agentes especializados para realizar as tarefas solicitadas pelo usuário. O Orquestrador garante que os agentes sejam chamados na ordem correta, gerencia falhas de forma resiliente e combina os resultados para produzir uma resposta final clara e útil.
