# HW06: Decision Trees and Ensembles

**Студент**: Фех Алексей Александрович  
**Датасет**: S06-hw-dataset-02.csv  
**Задача**: Бинарная классификация с дисбалансом классов  

## Описание

Домашнее задание по теме деревья решений и ансамбли (Random Forest, Gradient Boosting).

## Структура

```
HW06/
├── HW06.ipynb              # Основной ноутбук с экспериментами
├── report.md               # Итоговый отчёт
├── S06-hw-dataset-02.csv   # Используемый датасет
├── README.md               # Этот файл
└── artifacts/
    ├── best_model.joblib               # Лучшая модель (GradientBoosting)
    ├── metrics_test.json               # Финальные метрики на test
    ├── search_summaries.json           # Результаты GridSearchCV
    ├── best_model_meta.json            # Метаданные лучшей модели
    └── figures/
        ├── roc_curves.png              # ROC кривые для всех моделей
        ├── confusion_matrix.png        # Матрица ошибок для лучшей модели
        └── feature_importance.png      # Permutation importance (Top-15)
```

## Эксперименты

### Базовые модели (baseline)
- **DummyClassifier**: стратегия `most_frequent`
- **LogisticRegression**: с StandardScaler нормализацией

### Модели недели 6 (с подбором параметров через GridSearchCV)

1. **DecisionTree** ✓
   - GridSearchCV: `max_depth` ∈ [5, 10, 15, 20], `min_samples_leaf` ∈ [5, 10, 20, 30]
   - CV scoring: ROC-AUC (5 фолдов)
   - Контроль сложности: предотвращение переобучения

2. **RandomForest** ✓
   - GridSearchCV: `n_estimators` ∈ [50, 100, 200], `max_depth` ∈ [10, 15, 20]
   - GridSearchCV: `min_samples_leaf` ∈ [5, 10, 20], `max_features` ∈ ['sqrt', 'log2']
   - CV scoring: ROC-AUC (5 фолдов)
   - Bagging + случайность по признакам

3. **GradientBoosting** ✓
   - Параметры: `n_estimators=100`, `max_depth=5`, `learning_rate=0.1`
   - Последовательное улучшение модели
   - **Лучшая модель** (ROC-AUC ≈ 0.8712)

## Метрики качества

Для оценки используются:
- **Accuracy**: общая точность классификации
- **F1-score**: гармоническое среднее precision и recall
- **ROC-AUC**: площадь под ROC-кривой (инвариантна к порогу)

### Результаты на test (25% выборки, test_size=0.25)

| Модель | Accuracy | F1 | ROC-AUC |
|--------|----------|-------|----------|
| DummyClassifier | 0.7373 | 0.0000 | - |
| LogisticRegression | 0.8162 | 0.5717 | 0.8009 |
| DecisionTree (best) | 0.8367 | 0.6286 | 0.8129 |
| RandomForest (best) | 0.8513 | 0.6789 | 0.8645 |
| **GradientBoosting** | **0.8578** | **0.6921** | **0.8712** |

## Как запустить

1. Убедитесь, что установлены зависимости:
   ```bash
   pip install pandas numpy scikit-learn matplotlib seaborn joblib
   ```

2. Откройте `HW06.ipynb` в Jupyter Notebook:
   ```bash
   jupyter notebook HW06.ipynb
   ```

3. Выполните все ячейки по порядку. Код автоматически:
   - Загружает данные
   - Разделяет на train/test с фиксированным `random_state=42`
   - Выполняет GridSearchCV для DecisionTree и RandomForest (только на train)
   - Обучает все модели
   - Генерирует метрики и графики
   - Сохраняет артефакты в `artifacts/`

## Ключевые выводы

✅ **GridSearchCV** - Подбор гиперпараметров выполняется только на train через кросс-валидацию (5 фолдов)

✅ **Честный протокол** - train/test разбиение фиксировано (`random_state=42`), test используется только один раз

✅ **Сравнение моделей** - GradientBoosting показал лучший результат (ROC-AUC = 0.8712)

✅ **Интерпретация** - Top-15 признаков по permutation importance выявили ключевые факторы

✅ **Визуализация** - ROC-кривые, confusion matrix и feature importance сохранены в `artifacts/figures/`

## Автор

Фех Алексей Александрович  
МАНИ РТУ МИРЭА (Московский институт радиоэлектроники, электроники и автоматики)
