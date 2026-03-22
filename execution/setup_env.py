"""
IMOBILAY — Validação de Ambiente

Verifica se o .env existe e contém todas as variáveis obrigatórias.
Verifica se as dependências Python estão instaladas.

Uso:
    python execution/setup_env.py

Saída:
    ✓ ou ✗ para cada verificação, com mensagem descritiva.
"""

import os
import sys
from pathlib import Path


# Variáveis obrigatórias no .env
REQUIRED_VARS = [
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "GEMINI_API_KEY",
    "REDIS_URL",
]

# Dependências Python obrigatórias
REQUIRED_PACKAGES = [
    "google.genai",
    "sentence_transformers",
    "aiohttp",
    "pydantic",
    "redis",
    "supabase",
    "structlog",
    "dotenv",
    "pytest",
]


def check_env_file() -> bool:
    """Verifica se o .env existe e contém as variáveis obrigatórias."""
    env_path = Path(__file__).parent.parent / ".env"

    if not env_path.exists():
        print("✗ Arquivo .env não encontrado")
        print(f"  → Copie .env.example para .env: cp .env.example .env")
        return False

    print("✓ Arquivo .env encontrado")

    # Carregar variáveis do .env
    env_vars = {}
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                env_vars[key.strip()] = value.strip()

    all_present = True
    for var in REQUIRED_VARS:
        if var in env_vars and env_vars[var] and not env_vars[var].startswith("seu-"):
            print(f"  ✓ {var} configurado")
        else:
            print(f"  ✗ {var} não configurado ou com valor placeholder")
            all_present = False

    return all_present


def check_dependencies() -> bool:
    """Verifica se as dependências Python estão instaladas."""
    all_installed = True

    for package in REQUIRED_PACKAGES:
        try:
            __import__(package)
            print(f"  ✓ {package} instalado")
        except ImportError:
            print(f"  ✗ {package} NÃO instalado")
            all_installed = False

    return all_installed


def check_python_version() -> bool:
    """Verifica se Python 3.11+ está sendo usado."""
    major, minor = sys.version_info[:2]
    if major >= 3 and minor >= 11:
        print(f"✓ Python {major}.{minor} (requerido: 3.11+)")
        return True
    else:
        print(f"✗ Python {major}.{minor} — requerido 3.11+")
        return False


def main():
    print("=" * 50)
    print("IMOBILAY — Validação de Ambiente")
    print("=" * 50)
    print()

    results = []

    print("── Python ──────────────────────────")
    results.append(check_python_version())
    print()

    print("── Variáveis de Ambiente ───────────")
    results.append(check_env_file())
    print()

    print("── Dependências Python ────────────")
    results.append(check_dependencies())
    print()

    print("=" * 50)
    if all(results):
        print("✓ Ambiente configurado corretamente!")
    else:
        print("✗ Há problemas no ambiente. Corrija os itens acima.")
        sys.exit(1)


if __name__ == "__main__":
    main()
