# HW04 - HTTP-сервис качества датасетов

**Студент:** Фех Алексей Александрович
**Группа:** ИМБО-02-24
**GitHub:** @Lishangie

---

## Решение

### Структура проекта

Проект расположен в `homeworks/HW04/eda-cli/`:

```
eda-cli/
├── pyproject.toml
├── README.md
├── .gitignore
├── .python-version
├── src/eda_cli/
│   ├── __init__.py
│   ├── core.py
│   ├── cli.py
│   ├── viz.py
│   └── api.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   └── test_core.py
└── data/
    └── example.csv
```

### Реализованные эндпоинты

#### 1. GET /health

Проверка статуса сервиса.

```bash
curl http://localhost:8000/health
```

Ответ:
```json
{
  "status": "healthy",
  "message": "EDA Quality Service is running"
}
```

#### 2. POST /quality

Оценка качества данных по JSON параметрам.

```bash
curl -X POST "http://localhost:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{"n_rows": 50, "n_cols": 10, "max_missing_share": 0.6}'
```

#### 3. POST /quality-from-csv

Оценка качества из CSV-файла.

```bash
curl -X POST "http://localhost:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

#### 4. POST /quality-flags-from-csv (HW04)

Полный набор флагов качества с использованием доработок из HW03.

```bash
curl -X POST "http://localhost:8000/quality-flags-from-csv" \
  -F "file=@data/example.csv"
```

Ответ:
```json
{
  "flags": {
    "too_few_rows": false,
    "too_many_columns": false,
    "too_many_missing": false,
    "has_constant_columns": false,
    "has_many_zero_values": false,
    "constant_columns": [],
    "zero_heavy_columns": [],
    "max_missing_share": 0.04,
    "quality_score": 0.96
  },
  "latency_ms": 12.45
}
```

---

## Ключевые моменты

### Зависимости

Добавлены в pyproject.toml:
- fastapi>=0.100.0
- uvicorn[standard]>=0.23.0
- python-multipart>=0.0.6

### Собственный эндпоинт

POST /quality-flags-from-csv реализует Вариант A из задания:

- Принимает CSV-файл
- Вычисляет полный набор флагов:
  - too_few_rows, too_many_columns, too_many_missing
  - has_constant_columns (HW03)
  - has_many_zero_values (HW03)
  - quality_score
- Возвращает весь словарь флагов

### Использование HW03

Эндпоинт вызывает compute_quality_flags из core.py, которая содержит все эвристики из HW03.

---

## Запуск

### Установка

```bash
cd homeworks/HW04/eda-cli
uv sync
```

### CLI

```bash
uv run eda-cli overview data/example.csv
uv run eda-cli report data/example.csv --out-dir reports_example
```

### HTTP-сервис

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Откройте http://localhost:8000/docs для интерактивной документации.

### Тесты

```bash
uv run pytest -q
```

---

## Проверка требований

1. Структура HW04 соответствует требованиям (pyproject.toml, src/, api.py)
2. HTTP-сервис запускается и работает
3. Реализованы все требуемые эндпоинты
4. Собственный эндпоинт использует доработки из HW03
5. Полный набор флагов возвращается в JSON
6. Тесты проходят

Статус: Готово
