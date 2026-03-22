"""
IMOBILAY — Executar Migrations no Supabase

Lê o arquivo SQL de migrations e executa via Supabase API (RPC ou SQL Editor).
Para uso inicial do projeto — criar todas as tabelas, extensões e índices.

Uso:
    python execution/run_migrations.py

Pré-requisitos:
    - .env configurado com SUPABASE_URL e SUPABASE_SERVICE_ROLE_KEY
    - Extensões uuid-ossp e vector ativadas no Supabase Dashboard
"""

import os
import sys
import asyncio
from pathlib import Path

# Adicionar raiz do projeto ao path
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()


async def run_migrations():
    """Executa o arquivo de migration SQL no Supabase."""

    migration_path = Path(__file__).parent.parent / "database" / "migrations" / "001_initial.sql"

    if not migration_path.exists():
        print(f"✗ Arquivo de migration não encontrado: {migration_path}")
        print("  → Crie o arquivo database/migrations/001_initial.sql primeiro")
        print("  → Referência: context/baserelacional.md, seção 3")
        sys.exit(1)

    sql_content = migration_path.read_text(encoding="utf-8")
    print(f"✓ Migration carregada: {migration_path.name} ({len(sql_content)} bytes)")

    # Verificar variáveis de ambiente
    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("✗ SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configurados no .env")
        sys.exit(1)

    try:
        from supabase._async.client import create_client as acreate_client

        client = await acreate_client(
            supabase_url=supabase_url,
            supabase_key=service_key,
        )
        print("✓ Conectado ao Supabase")

        # Executar migration via RPC (requer função SQL no Supabase)
        # Alternativa: executar diretamente no SQL Editor do Dashboard
        print()
        print("⚠ Para executar a migration:")
        print("  1. Abra o SQL Editor no Supabase Dashboard")
        print(f"  2. Cole o conteúdo de: {migration_path}")
        print("  3. Execute o SQL")
        print()
        print("  Ou crie uma função RPC 'execute_sql' no Supabase para automatizar.")
        print()
        print(f"── Conteúdo da migration ({migration_path.name}) ──")
        print(sql_content[:500] + "..." if len(sql_content) > 500 else sql_content)

    except ImportError:
        print("✗ Pacote 'supabase' não instalado. Execute: pip install supabase")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Erro ao conectar: {e}")
        sys.exit(1)


def main():
    print("=" * 50)
    print("IMOBILAY — Executar Migrations")
    print("=" * 50)
    print()
    asyncio.run(run_migrations())


if __name__ == "__main__":
    main()
