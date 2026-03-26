# Camada 3: Aprendizado e Observabilidade (Learning Layer)

Este diretório contém a lógica de aprendizado do sistema, responsável por coletar feedback e gerenciar a memória de longo prazo.

## Arquivos e suas Funções

- **[__init__.py](file:///c:/imobilay/layer_3_learning/__init__.py)**: Inicialização do pacote.
- **[feedback_collector.py](file:///c:/imobilay/layer_3_learning/feedback_collector.py)**: Coleta feedback explícito e implícito do usuário sobre as respostas do sistema.
- **[memory_manager.py](file:///c:/imobilay/layer_3_learning/memory_manager.py)**: Gerencia a memória de sessão e de longo prazo do usuário (ex: perfil de investidor).
- **[observability_layer.py](file:///c:/imobilay/layer_3_learning/observability_layer.py)**: Registra logs de execução dos agentes para auditoria e melhoria contínua.
- **[router_feedback_loop.py](file:///c:/imobilay/layer_3_learning/router_feedback_loop.py)**: Realiza o ajuste fino dos roteadores de intenção com base no feedback coletado.

## Funcionamento no Projeto

A Camada 3 é responsável por tornar o Imobilay cada vez melhor a cada interação. Ela gerencia a memória do usuário, permitindo que o sistema aprenda suas preferências de investimento e ofereça sugestões cada vez mais personalizadas. Além disso, ela coleta feedback e monitora o desempenho de todos os agentes para identificar áreas de melhoria e realizar o ajuste fino dos roteadores de intenção. Isso garante que o Imobilay evolua continuamente para atender melhor às necessidades dos usuários.
