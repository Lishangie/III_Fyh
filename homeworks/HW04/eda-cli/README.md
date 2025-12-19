# eda-cli — HTTP-сервис для EDA

Расширение мини-приложения для анализа CSV-датасетов (HW04).

## Установка и запуск

```bash
cd homeworks/HW04/eda-cli
uv sync
```

## CLI команды

### overview
Быстрый обзор датасета (размеры, типы, пропуски, статистика).

```bash
uv run eda-cli overview data/example.csv
```

### report
Генерация полного отчёта в Markdown + графики.

```bash
uv run eda-cli report data/example.csv --out-dir reports_example
```

#### Параметры:
- `--title "Заголовок"` — кастомный заголовок отчёта (по умолчанию "EDA Report")
- `--min-missing-share 0.2` — порог доли пропусков для "проблемных" колонок (по умолчанию 0.1)

## HTTP-сервис (HW04)

Запуск сервера на локальном хосте (порт 8000):

```bash
uv run uvicorn eda_cli.api:app --reload --port 8000
```

Затем откройте интерактивную документацию:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/redoc (ReDoc)

### Эндпоинты

#### GET /health
Проверка статуса сервиса.

```bash
curl http://localhost:8000/health
```

#### POST /quality
Оценка качества данных по JSON-объекту.

```bash
curl -X POST "http://localhost:8000/quality" \
  -H "Content-Type: application/json" \
  -d '{
    "n_rows": 50,
    "n_cols": 10,
    "max_missing_share": 0.6
  }'
```

#### POST /quality-from-csv
Оценка качества данных из загруженного CSV-файла.

```bash
curl -X POST "http://localhost:8000/quality-from-csv" \
  -F "file=@data/example.csv"
```

#### POST /quality-flags-from-csv (HW04)
Полный набор флагов качества из CSV-файла с использованием эвристик HW03.

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
    "has_constant_columns": false,
    "has_many_zero_values": false,
    "quality_score": 0.95
  }
}
```

## Тесты

```bash
uv run pytest -q
```

## Эвристики качества данных
1. **too_few_rows** — датасет содержит менее 100 строк
2. **too_many_columns** — датасет содержит более 100 столбцов
3. **too_many_missing** — максимальная доля пропусков в колонке > 50%
4. **has_constant_columns** — присутствуют колонки с одинаковыми значениями
5. **has_many_zero_values** — числовые колонки с более чем 60% нулевых значений
6. **quality_score** — агрегированный балл качества (0.0–1.0)
