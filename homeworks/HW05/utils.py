"""Utility functions for HW05"""

import pandas as pd
import numpy as np
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score


def evaluate_model(y_true, y_pred, y_proba=None):
    """Оценить модель"""
    print("=" * 50)
    print(f"Classification Report:")
    print(classification_report(y_true, y_pred))
    
    print(f"\nConfusion Matrix:")
    print(confusion_matrix(y_true, y_pred))
    
    if y_proba is not None:
        auc = roc_auc_score(y_true, y_proba)
        print(f"\nROC-AUC: {auc:.4f}")
        return auc
    return None


def get_feature_importance(model, feature_names, top_n=10):
    """Получить важность признаков"""
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
    elif hasattr(model, 'coef_'):
        importances = np.abs(model.coef_[0])
    else:
        return None
    
    feat_importance = pd.DataFrame({
        'feature': feature_names,
        'importance': importances
    }).sort_values('importance', ascending=False)
    
    return feat_importance.head(top_n)
