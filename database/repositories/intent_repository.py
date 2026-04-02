import structlog
from database.client import get_system_client

logger = structlog.get_logger(__name__)

class IntentRepository:
    """Repositório para gerenciar intents e embeddings no banco."""

    async def get_all_intents_and_embeddings(self) -> dict[str, list]:
        """
        Busca todos os exemplos de intents e seus embeddings no banco.
        Retorna um dicionário: { "intent_name": [ {"text": "...", "embedding": [...] } ] }
        """
        try:
            client = await get_system_client()
            response = await client.table("intent_embeddings").select("intent_name, example_text, embedding").execute()

            result = {}
            for row in response.data:
                intent = row.get("intent_name")
                if intent not in result:
                    result[intent] = []
                result[intent].append({
                    "text": row.get("example_text"),
                    "embedding": row.get("embedding")
                })

            return result
        except Exception as e:
            logger.error(f"Erro ao buscar intents no banco: {str(e)}")
            return {}
