# Modelos de Dados (Models)

Este diretório contém a definição das estruturas de dados (Pydantic models, Dataclasses) utilizadas por todo o sistema.

## Arquivos e suas Funções

- **[__init__.py](file:///c:/imobilay/models/__init__.py)**: Inicialização do pacote.
- **[context.py](file:///c:/imobilay/models/context.py)**: Definição do `ContextStore` e do `SessionRecord`.
- **[feedback.py](file:///c:/imobilay/models/feedback.py)**: Definição do `FeedbackRecord` e do `OrchestratorResult`.
- **[property.py](file:///c:/imobilay/models/property.py)**: Definição do `PropertyRecord` e do `PropertyAnalysis`.
- **[routing.py](file:///c:/imobilay/models/routing.py)**: Definição do `RoutingResult`, `ExecutionDAG` e do `ExecutionGroup`.

## Funcionamento no Projeto

Os modelos de dados são o contrato de comunicação entre todas as camadas do sistema (Input, Orchestrator, Learning). Eles garantem que a informação seja transmitida de forma consistente e estruturada, facilitando o desenvolvimento e a manutenção. O uso de Pydantic models e Dataclasses permite validar os dados em tempo de execução e garantir que as interfaces entre os componentes sejam claras e previsíveis.
