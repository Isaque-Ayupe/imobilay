"""
IMOBILAY — InvestorProfileRepository

Persistência de investor_profiles (memória de longo prazo — Camada 3).
TTL lógico de 90 dias: enforçado na aplicação via last_active_at.
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
from uuid import UUID
from supabase._async.client import AsyncClient


TTL_DAYS = 90


@dataclass
class InvestorProfileRecord:
    user_id: UUID
    risk_tolerance: str | None          # "low", "medium", "high"
    horizon_years: int | None
    estimated_capital: float | None
    preferred_areas: list[str]
    price_min: float | None
    price_max: float | None
    preferred_types: list[str]
    investment_goal: str | None         # "rental", "appreciation", "both"
    last_active_at: datetime
    updated_at: datetime

    @property
    def is_expired(self) -> bool:
        """Verifica se o perfil expirou (TTL lógico de 90 dias)."""
        return datetime.utcnow() - self.last_active_at.replace(tzinfo=None) > timedelta(days=TTL_DAYS)


class InvestorProfileRepository:
    def __init__(self, client: AsyncClient):
        self._db = client

    async def upsert(
        self,
        user_id: str,
        risk_tolerance: str | None = None,
        horizon_years: int | None = None,
        estimated_capital: float | None = None,
        preferred_areas: list[str] | None = None,
        price_min: float | None = None,
        price_max: float | None = None,
        preferred_types: list[str] | None = None,
        investment_goal: str | None = None,
    ) -> InvestorProfileRecord:
        """
        Cria ou atualiza o perfil de investidor.
        Atualiza last_active_at automaticamente.
        """
        data = {
            "user_id": user_id,
            "last_active_at": datetime.utcnow().isoformat(),
        }
        # Só incluir campos não-None para permitir updates parciais
        if risk_tolerance is not None:
            data["risk_tolerance"] = risk_tolerance
        if horizon_years is not None:
            data["horizon_years"] = horizon_years
        if estimated_capital is not None:
            data["estimated_capital"] = estimated_capital
        if preferred_areas is not None:
            data["preferred_areas"] = preferred_areas
        if price_min is not None:
            data["price_min"] = price_min
        if price_max is not None:
            data["price_max"] = price_max
        if preferred_types is not None:
            data["preferred_types"] = preferred_types
        if investment_goal is not None:
            data["investment_goal"] = investment_goal

        result = await (
            self._db.table("investor_profiles")
            .upsert(data, on_conflict="user_id")
            .execute()
        )
        return self._map(result.data[0])

    async def get_by_user_id(self, user_id: str) -> InvestorProfileRecord | None:
        result = await (
            self._db.table("investor_profiles")
            .select("*")
            .eq("user_id", user_id)
            .maybe_single()
            .execute()
        )
        if not result.data:
            return None

        record = self._map(result.data)

        # Aplicar TTL lógico: se expirado, retornar None (perfil descartado)
        if record.is_expired:
            return None

        return record

    async def touch(self, user_id: str) -> None:
        """Atualiza last_active_at para renovar o TTL."""
        await (
            self._db.table("investor_profiles")
            .update({"last_active_at": datetime.utcnow().isoformat()})
            .eq("user_id", user_id)
            .execute()
        )

    async def delete(self, user_id: str) -> None:
        await (
            self._db.table("investor_profiles")
            .delete()
            .eq("user_id", user_id)
            .execute()
        )

    def _map(self, row: dict) -> InvestorProfileRecord:
        return InvestorProfileRecord(
            user_id=UUID(row["user_id"]),
            risk_tolerance=row.get("risk_tolerance"),
            horizon_years=row.get("horizon_years"),
            estimated_capital=float(row["estimated_capital"]) if row.get("estimated_capital") else None,
            preferred_areas=row.get("preferred_areas") or [],
            price_min=float(row["price_min"]) if row.get("price_min") else None,
            price_max=float(row["price_max"]) if row.get("price_max") else None,
            preferred_types=row.get("preferred_types") or [],
            investment_goal=row.get("investment_goal"),
            last_active_at=datetime.fromisoformat(row["last_active_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )
