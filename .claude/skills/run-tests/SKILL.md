---
name: run-tests
description: Rodar a suite de testes pytest do IMOBILAY com cobertura e filtros.
disable-model-invocation: true
allowed-tools: Bash
---

# Testes do IMOBILAY

## Rodar todos os testes

```bash
cd /c/imobilay
python -m pytest tests/ -v
```

## Rodar um arquivo específico

```bash
python -m pytest tests/test_orchestrator.py -v
```

## Rodar com cobertura

```bash
python -m pytest tests/ -v --cov=. --cov-report=term-missing
```

## Rodar testes assíncronos

O projeto usa `pytest-asyncio`. Não é necessário flag extra — o decorator `@pytest.mark.asyncio` nos testes já ativa o loop.

## Rodar testes de um módulo específico

```bash
python -m pytest tests/test_semantic_router.py -v -k "test_route"
```

## Rodar testes com output detalhado

```bash
python -m pytest tests/ -v -s --tb=long
```

## Arquivos de teste existentes

- `tests/test_api.py` — endpoints da API
- `tests/test_calculator.py` — cálculos financeiros
- `tests/test_confidence_gate.py` — validação de confiança
- `tests/test_dag_resolver.py` — resolução de grafos DAG
- `tests/test_memory_manager.py` — gerenciamento de memória
- `tests/test_orchestrator.py` — orquestração de agentes
- `tests/test_resilience_manager.py` — circuit breakers e fallbacks
- `tests/test_semantic_router.py` — roteamento semântico
- `tests/test_user_service.py` — serviço de usuário

## Dependências

```bash
pip install -r requirements.txt
```

Requisitos de teste: `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`
