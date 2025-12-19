#!/usr/bin/env python3
"""Генерирует структурированные данные для работы"""

import pandas as pd
import numpy as np

np.random.seed(42)

# Настройки
n_samples = 700
default_rate = 0.3

# Генерируем признаки
data = {
    'client_id': np.arange(1, n_samples + 1),
    'age': np.random.randint(21, 70, n_samples),
    'income': np.random.randint(15000, 150000, n_samples),
    'years_employed': np.random.randint(0, 40, n_samples),
    'credit_score': np.random.randint(300, 850, n_samples),
    'debt_to_income': np.random.uniform(0, 1, n_samples),
    'num_credit_cards': np.random.randint(0, 8, n_samples),
    'num_late_payments': np.random.randint(0, 14, n_samples),
    'has_mortgage': np.random.choice([0, 1], n_samples),
    'has_car_loan': np.random.choice([0, 1], n_samples),
    'savings_balance': np.random.randint(-3000, 75000, n_samples),
    'checking_balance': np.random.randint(-3000, 25000, n_samples),
    'region_risk_score': np.random.uniform(0, 1, n_samples),
    'phone_calls_to_support_last_3m': np.random.randint(0, 20, n_samples),
    'active_loans': np.random.randint(0, 5, n_samples),
    'customer_tenure_years': np.random.randint(0, 15, n_samples),
}

df = pd.DataFrame(data)

# Генерируем таргет
# Дефолт зависит от кредитного скора и числа опозданий
default_prob = (1 - (df['credit_score'] / 850)) * 0.5 + (df['num_late_payments'] / 14) * 0.5
df['default'] = (np.random.random(n_samples) < default_prob).astype(int)

print(f"Generated {len(df)} samples")
print(f"Default rate: {df['default'].mean():.1%}")
print(f"\nSample:\n{df.head()}")

df.to_csv('data_generated.csv', index=False)
print(f"\nSaved to data_generated.csv")
