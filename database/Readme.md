# Camada de Dados (Database)

Este diretório contém a lógica de acesso ao banco de dados Supabase e a definição dos repositórios.

## Arquivos e suas Funções

- **[client.py](file:///c:/imobilay/database/client.py)**: Gerencia a conexão com o Supabase. Possui dois clientes distintos: `system_client` (para operações de backend ignorando RLS) e `user_client` (para operações respeitando RLS).
- **[__init__.py](file:///c:/imobilay/database/__init__.py)**: Inicialização do pacote.

## Diretórios

- **[migrations/](file:///c:/imobilay/database/migrations)**: Scripts SQL para configuração do esquema do banco de dados.
- **[repositories/](file:///c:/imobilay/database/repositories)**: Implementação do padrão Repository para abstrair o acesso às tabelas.

## Funcionamento no Projeto

A camada de dados é a base para a persistência do Imobilay. Ela é utilizada por todas as outras camadas (Input, Orchestrator, Learning) para salvar e recuperar informações sobre usuários, sessões, imóveis e feedbacks. O uso de repositórios garante que a lógica de negócio não dependa diretamente da estrutura do banco de dados.
