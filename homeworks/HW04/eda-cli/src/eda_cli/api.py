"""HTTP-сервис для оценки качества данных на FastAPI.

Основные эндпоинты:
- GET /health — проверка статуса
- POST /quality — оценка качества по JSON
- POST /quality-from-csv — оценка качества из CSV
- POST /quality-flags-from-csv — ПОЛНЫЙ набор флагов (HW04)
"""

import io
import time
from typing import Any, Dict

from fastapi import FastAPI, File, UploadFile
from fastapi.responses import RedirectResponse
from pydantic import BaseModel
import pandas as pd

from .core import (
    compute_quality_flags,
    missing_table,
    summarize_dataset,
)

app = FastAPI(
    title="EDA Quality Service",
    description="HTTP сервис для оценки качества данных",
    version="0.1.0",
)


# ============================================================================
# Pydantic модели для реквестов и ответов
# ============================================================================

class HealthResponse(BaseModel):
    status: str
    message: str


class QualityRequest(BaseModel):
    n_rows: int
    n_cols: int
    max_missing_share: float


class QualityResponse(BaseModel):
    too_few_rows: bool
    too_many_columns: bool
    too_many_missing: bool
    quality_score: float
    latency_ms: float


class QualityFlagsResponse(BaseModel):
    """HW04: Полный набор флагов качества."""
    flags: Dict[str, Any]
    latency_ms: float


# ============================================================================
# Функции-помощники
# ============================================================================

def _read_csv_from_upload(file: UploadFile) -> pd.DataFrame:
    """Отчитывает CSV из загруженного файла."""
    contents = file.file.read()
    df = pd.read_csv(io.BytesIO(contents))
    return df


# ============================================================================
# Эндпоинты
# ============================================================================

@app.get("/")
def root():
    """Редирект на интерактивную документацию."""
    return RedirectResponse(url="/docs")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Проверка статуса сервиса."""
    return HealthResponse(
        status="healthy",
        message="EDA Quality Service is running",
    )


@app.post("/quality", response_model=QualityResponse)
def quality(request: QualityRequest) -> QualityResponse:
    """
    Оценка качества данных по основным параметрам.
    
    Параметры:
    - n_rows: количество строк
    - n_cols: количество столбцов
    - max_missing_share: макс. доля пропусков
    """
    start_time = time.time()
    
    too_few = request.n_rows < 100
    too_many_cols = request.n_cols > 100
    too_many_miss = request.max_missing_share > 0.5
    
    score = 1.0
    score -= request.max_missing_share
    if too_few:
        score -= 0.2
    if too_many_cols:
        score -= 0.1
    score = max(0.0, min(1.0, score))
    
    latency = (time.time() - start_time) * 1000
    
    return QualityResponse(
        too_few_rows=too_few,
        too_many_columns=too_many_cols,
        too_many_missing=too_many_miss,
        quality_score=score,
        latency_ms=latency,
    )


@app.post("/quality-from-csv", response_model=QualityResponse)
async def quality_from_csv(file: UploadFile = File(...)) -> QualityResponse:
    """
    Оценка качества данных из CSV-файла.
    Вычисляет основные проверки качества.
    """
    start_time = time.time()
    
    df = _read_csv_from_upload(file)
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    
    # Вычисляем некоторые базовые флаги
    flags = compute_quality_flags(summary, missing_df, df)
    
    latency = (time.time() - start_time) * 1000
    
    return QualityResponse(
        too_few_rows=flags.get("too_few_rows", False),
        too_many_columns=flags.get("too_many_columns", False),
        too_many_missing=flags.get("too_many_missing", False),
        quality_score=flags.get("quality_score", 0.0),
        latency_ms=latency,
    )


@app.post("/quality-flags-from-csv", response_model=QualityFlagsResponse)
async def quality_flags_from_csv(file: UploadFile = File(...)) -> QualityFlagsResponse:
    """
    HW04: Эндпоинт для получения ПОЛНОГО набора флагов качества.
    
    Ответ:
    {
      "flags": {
        "too_few_rows": bool,
        "too_many_columns": bool,
        "too_many_missing": bool,
        "has_constant_columns": bool,
        "has_many_zero_values": bool,
        "constant_columns": [str],
        "zero_heavy_columns": [str],
        "quality_score": float,
        "max_missing_share": float
      },
      "latency_ms": float
    }
    """
    start_time = time.time()
    
    df = _read_csv_from_upload(file)
    summary = summarize_dataset(df)
    missing_df = missing_table(df)
    
    # Основной вызов - от HW03!
    flags = compute_quality_flags(summary, missing_df, df)
    
    latency = (time.time() - start_time) * 1000
    
    return QualityFlagsResponse(
        flags=flags,
        latency_ms=latency,
    )
