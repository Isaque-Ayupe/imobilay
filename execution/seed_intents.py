"""
IMOBILAY — Seed de Intent Embeddings

Gera embeddings para os exemplos de cada intent usando sentence-transformers
e insere na tabela intent_embeddings do Supabase (pgvector).

Uso:
    python execution/seed_intents.py

Pré-requisitos:
    - .env configurado
    - Tabela intent_embeddings criada (migration 001)
    - sentence-transformers instalado
"""

import os
import sys
import asyncio
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv

load_dotenv()

# ── Exemplos por intent ──────────────────────────────────────
# Cada intent tem múltiplos exemplos para gerar embeddings variados.
# Quanto mais exemplos, melhor a cobertura do SemanticRouter.

INTENT_EXAMPLES = {
    "buscar_imoveis": [
        "quero um apartamento de 2 quartos em Pinheiros",
        "procuro imóvel até 800 mil reais",
        "tem algo em Vila Madalena com 3 quartos?",
        "quero apartamento no Brooklin com vaga",
        "busco kitnet para alugar no centro",
        "preciso de um apartamento em Goiânia",
        "quero comprar um imóvel em São Paulo",
        "tem cobertura disponível em Moema?",
        "apartamento com 2 quartos e varanda",
        "studios disponíveis no Itaim Bibi",
    ],
    "analisar_imovel": [
        "analisa esse imóvel pra mim",
        "o preço desse apartamento está bom?",
        "vale a pena esse imóvel na Alameda Lorena?",
        "esse preço por metro quadrado é justo?",
        "como está o mercado nesse bairro?",
        "esse imóvel está caro ou barato?",
        "qual seria o preço justo desse apartamento?",
        "esse imóvel tem boa liquidez?",
    ],
    "investimento": [
        "qual o melhor imóvel para investir?",
        "quero ROI alto, o que tem?",
        "qual apartamento dá mais retorno no aluguel?",
        "investir em studio vale a pena?",
        "quanto tempo para pagar o investimento?",
        "quero investir em imóvel para alugar",
        "qual o payback desse imóvel?",
        "onde tem melhor rentabilidade?",
        "análise de investimento imobiliário",
        "comparar retorno de investimento",
    ],
    "refinar_busca": [
        "agora quero com 3 quartos",
        "tira os acima de 1 milhão",
        "mostra só os de Pinheiros",
        "filtra por preço menor",
        "quero ver só apartamentos maiores",
        "remove os sem vaga de garagem",
        "ordena por preço mais baixo",
        "agora com área mínima de 80m²",
    ],
}


async def seed_intents():
    """Gera embeddings e insere no Supabase."""

    print("── Carregando modelo sentence-transformers ──")
    try:
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("all-MiniLM-L6-v2")
        print("✓ Modelo all-MiniLM-L6-v2 carregado")
    except ImportError:
        print("✗ sentence-transformers não instalado")
        print("  → pip install sentence-transformers")
        sys.exit(1)

    print()
    print("── Gerando embeddings ──")

    all_records = []
    for intent_name, examples in INTENT_EXAMPLES.items():
        embeddings = model.encode(examples)
        print(f"  ✓ {intent_name}: {len(examples)} exemplos → dimensão {embeddings.shape[1]}")

        for text, embedding in zip(examples, embeddings):
            all_records.append({
                "intent_name": intent_name,
                "example_text": text,
                "embedding": embedding.tolist(),
            })

    print(f"\n  Total: {len(all_records)} embeddings gerados")

    # ── Inserir no Supabase ──
    print()
    print("── Inserindo no Supabase ──")

    supabase_url = os.getenv("SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not supabase_url or not service_key:
        print("✗ SUPABASE_URL ou SUPABASE_SERVICE_ROLE_KEY não configurados")
        print("  → Salvando embeddings localmente em .tmp/intent_embeddings.json")

        import json
        tmp_dir = Path(__file__).parent.parent / ".tmp"
        tmp_dir.mkdir(exist_ok=True)
        output_path = tmp_dir / "intent_embeddings.json"

        # Converter para serialização (numpy arrays → lists)
        serializable = []
        for r in all_records:
            serializable.append({
                "intent_name": r["intent_name"],
                "example_text": r["example_text"],
                "embedding_dim": len(r["embedding"]),
                # Não salvar embedding completo no JSON (muito grande)
            })

        output_path.write_text(json.dumps(serializable, indent=2, ensure_ascii=False))
        print(f"✓ Metadata salva em {output_path}")
        return

    try:
        from supabase._async.client import create_client as acreate_client

        client = await acreate_client(
            supabase_url=supabase_url,
            supabase_key=service_key,
        )

        # Limpar registros existentes antes de re-seed
        await client.table("intent_embeddings").delete().neq("id", "00000000-0000-0000-0000-000000000000").execute()
        print("✓ Tabela intent_embeddings limpa")

        # Inserir em lotes de 10
        batch_size = 10
        for i in range(0, len(all_records), batch_size):
            batch = all_records[i : i + batch_size]
            await client.table("intent_embeddings").insert(batch).execute()
            print(f"  ✓ Inseridos {min(i + batch_size, len(all_records))}/{len(all_records)}")

        print(f"\n✓ {len(all_records)} embeddings inseridos com sucesso!")

    except Exception as e:
        print(f"✗ Erro ao inserir: {e}")
        sys.exit(1)


def main():
    print("=" * 50)
    print("IMOBILAY — Seed de Intent Embeddings")
    print("=" * 50)
    print()
    asyncio.run(seed_intents())


if __name__ == "__main__":
    main()
