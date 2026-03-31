# Camada 1: Entrada e Processamento (Input Layer)

Este diretório contém a lógica de entrada do sistema, responsável por classificar e rotear a intenção do usuário.

## Arquivos e suas Funções

- **[__init__.py](file:///c:/imobilay/layer_1_input/__init__.py)**: Inicialização do pacote.
- **[context_store.py](file:///c:/imobilay/layer_1_input/context_store.py)**: Gerencia o armazenamento do contexto da conversa, mantendo o estado da interação.
- **[dag_resolver.py](file:///c:/imobilay/layer_1_input/dag_resolver.py)**: Resolve o DAG (Grafo Acíclico Dirigido) de execução com base na intenção do usuário, definindo quais agentes serão chamados.
- **[input_processor.py](file:///c:/imobilay/layer_1_input/input_processor.py)**: Processa a entrada do usuário, realizando normalizações e limpezas iniciais.
- **[semantic_router.py](file:///c:/imobilay/layer_1_input/semantic_router.py)**: Classifica a intenção do usuário utilizando embeddings e similaridade de cosseno, sem o uso direto de LLMs para esta tarefa.

## Funcionamento no Projeto

A Camada 1 é a porta de entrada para todas as requisições do usuário no Imobilay. Ela recebe a mensagem bruta, identifica o que o usuário deseja fazer (ex: buscar imóveis, analisar investimento) e gera um plano de execução (DAG) que será processado pela Camada 2 (Orchestrator). Isso garante que o sistema seja eficiente e determinístico na escolha do fluxo de resposta.
