# HW04 - HTTP-сервис качества датасетов

Студент: Фех Алексей Александрович  
Группа: ИМБО-02-24

---

## Что лежит в HW04

Проект в `homeworks/HW04/eda-cli/`.

```
eda-cli/
  pyproject.toml
  README.md
  src/eda_cli/
    __init__.py
    core.py
    cli.py
    viz.py
    api.py
  tests/
    test_core.py
  data/
    example.csv
```

Это копия HW03 с добавленным HTTP-сервисом.

---

## Эндпоинты

Запуск сервиса:

```bash
cd homeworks/HW04/eda-cli
uv sync
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Дальше:
- /docs — swagger
- /health — просто проверка, что живой
- /quality — берёт n_rows, n_cols, max_missing_share из JSON
- /quality-from-csv — считает качество прямо из CSV
- /quality-flags-from-csv — то же, но отдаёт все флаги из HW03

Пример для /quality-flags-from-csv:

```bash
curl -X POST "http://localhost:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```

Ответ выглядит примерно так:

```json
{
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_many_zero_values": false,
    "max_missing_share": 0.04,
    "quality_score": 0.96
  },
  "latency_ms": 12.4
}
```

Внутри вызывается `summarize_dataset`, `missing_table` и `compute_quality_flags` из core.py, как в HW03.

---

## Что сделано по заданию

- HW04 лежит в отдельной папке, структура как в методичке
- fastapi, uvicorn и python-multipart добавлены в pyproject.toml
- api.py подключает функции из core.py
- базовые эндпоинты из семинара есть
- свой эндпоинт `/quality-flags-from-csv` завязан на эвристики HW03
- флаги типа `has_constant_columns` и `has_many_zero_values` попадают в ответ
- тесты на ядро те же, что и в HW03, проходят

По сути, HW03 обёрнут в небольшой HTTP-сервис.
