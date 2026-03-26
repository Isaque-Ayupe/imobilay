# Migrações do Banco de Dados (Database Migrations)

Este diretório contém os scripts SQL para a estrutura inicial e evoluções do banco de dados Supabase.

## Arquivos e suas Funções

- **[001_initial.sql](file:///c:/imobilay/database/migrations/001_initial.sql)**: Script SQL inicial que cria as tabelas principais: `user_profiles`, `sessions`, `investor_profiles`, `messages`, `saved_properties`, `feedback`, `execution_traces`.

## Funcionamento no Projeto

As migrações são fundamentais para manter o ambiente de desenvolvimento e produção em sincronia. O Imobilay utiliza esses scripts para configurar o banco de dados Supabase com as tabelas, índices e restrições necessários para o funcionamento correto do sistema.
