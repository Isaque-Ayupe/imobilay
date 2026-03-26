# Repositórios (Database Repositories)

Este diretório contém a implementação do padrão Repository para abstrair o acesso às tabelas do Supabase.

## Arquivos e suas Funções

- **[__init__.py](file:///c:/imobilay/database/repositories/__init__.py)**: Exporta os repositórios para o pacote.
- **[feedback_repository.py](file:///c:/imobilay/database/repositories/feedback_repository.py)**: CRUD para a tabela `feedback`.
- **[investor_profile_repository.py](file:///c:/imobilay/database/repositories/investor_profile_repository.py)**: CRUD para a tabela `investor_profiles`.
- **[message_repository.py](file:///c:/imobilay/database/repositories/message_repository.py)**: CRUD para a tabela `messages`.
- **[saved_property_repository.py](file:///c:/imobilay/database/repositories/saved_property_repository.py)**: CRUD para a tabela `saved_properties`.
- **[session_repository.py](file:///c:/imobilay/database/repositories/session_repository.py)**: CRUD para a tabela `sessions`.
- **[trace_repository.py](file:///c:/imobilay/database/repositories/trace_repository.py)**: CRUD para a tabela `execution_traces`.
- **[user_repository.py](file:///c:/imobilay/database/repositories/user_repository.py)**: CRUD para a tabela `user_profiles`.

## Funcionamento no Projeto

Os repositórios são utilizados por todas as camadas do sistema (Input, Orchestrator, Learning) para realizar operações no banco de dados. Eles garantem que a lógica de negócio não dependa diretamente da estrutura do banco de dados, facilitando a manutenção e testes unitários.
