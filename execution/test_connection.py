"""
IMOBILAY — Testar Conexão com Supabase

Valida que o cliente async conecta corretamente e que as tabelas existem.

Uso:
    python execution/test_connection.py

Pré-requisitos:
    - .env configurado
    - Migrations executadas
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

# Tabelas esperadas após executar 001_initial.sql
EXPECTED_TABLES = [
    "user_profiles",
    "investor_profiles",
    "sessions",
    "messages",
    "execution_traces",
    "feedback_records",
    "saved_properties",
    "intent_embeddings",
]


async def test_connection():
    """Testa conexão com Supabase e verifica tabelas."""

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("✗ SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configurados no .env")
        sys.exit(1)

    print(f"  URL: {supabase_url}")
    print()

    try:
        from supabase._async.client import create_client as acreate_client

        client = await acreate_client(
            supabase_url=supabase_url,
            supabase_key=service_key,
        )
        print("✓ Conexão com Supabase estabelecida")

    except ImportError:
        print("✗ Pacote 'supabase' não instalado. Execute: pip install supabase")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Falha na conexão: {e}")
        sys.exit(1)

    # ── Verificar tabelas ──
    print()
    print("── Verificando tabelas ──")

    all_ok = True
    for table in EXPECTED_TABLES:
        try:
            result = await (
                client.table(table)
                .select("*", count="exact")
                .limit(0)
                .execute()
            )
            count = result.count if result.count is not None else 0
            print(f"  ✓ {table:<25} ({count} registros)")
        except Exception as e:
            print(f"  ✗ {table:<25} — erro: {e}")
            all_ok = False

    print()
    if all_ok:
        print("✓ Todas as tabelas existem e estão acessíveis!")
    else:
        print("✗ Algumas tabelas não foram encontradas.")
        print("  → Execute as migrations: python execution/run_migrations.py")


def main():
    print("=" * 50)
    print("IMOBILAY — Testar Conexão com Supabase")
    print("=" * 50)
    print()
    asyncio.run(test_connection())


if __name__ == "__main__":
    main()
