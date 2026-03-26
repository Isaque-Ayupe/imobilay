# Execução e Scripts Utilitários (Execution)

Este diretório contém os scripts Python determinísticos utilizados para setup, migrações e execução do pipeline do Imobilay.

## Arquivos e suas Funções

- **[run_migrations.py](file:///c:/imobilay/execution/run_migrations.py)**: Script para executar as migrações SQL no banco de dados Supabase.
- **[run_pipeline.py](file:///c:/imobilay/execution/run_pipeline.py)**: Script para executar o pipeline completo do Imobilay (Input → Orchestrator → Learning).
- **[seed_intents.py](file:///c:/imobilay/execution/seed_intents.py)**: Script para popular a base de intents do SemanticRouter.
- **[setup_env.py](file:///c:/imobilay/execution/setup_env.py)**: Script para configuração inicial das variáveis de ambiente.
- **[test_connection.py](file:///c:/imobilay/execution/test_connection.py)**: Script para testar a conexão com o banco de dados Supabase.

## Funcionamento no Projeto

Os scripts de execução são as ferramentas que automatizam as tarefas recorrentes do Imobilay. Eles são fundamentais para manter o sistema em funcionamento e garantir que as configurações do ambiente estejam corretas. O uso de scripts determinísticos ajuda a evitar erros manuais e facilita a reprodução do ambiente em diferentes máquinas.
