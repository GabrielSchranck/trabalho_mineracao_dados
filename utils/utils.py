import re
import pandas as pd


def normalize_text(text: str):
    """Remove espaços e evita quebra de CSV."""
    if text is None:
        return ""
    return str(text).strip().replace(';', ',')


def normalize_value(value: str):
    """Converte valor monetário para float."""
    try:
        return round(
            float(
                str(value)
                .replace('.', '')
                .replace(',', '.')
                .replace('R$', '')
                .strip()
            ),
            2
        )
    except:
        return 0.0


def clean_string(text: str):
    """Remove caracteres especiais."""
    if text is None:
        return ""
    return re.sub(r'[^\w\s]', '', str(text).lower()).strip()


def normalize_minmax(series: pd.Series):
    """Normalização Min-Max."""
    min_val = series.min()
    max_val = series.max()

    if pd.isna(min_val) or pd.isna(max_val) or min_val == max_val:
        return pd.Series([0] * len(series))

    return (series - min_val) / (max_val - min_val)


def detect_outliers_iqr(series: pd.Series):
    """Retorna máscara de outliers usando IQR."""
    q1 = series.quantile(0.25)
    q3 = series.quantile(0.75)
    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    return (series < lower) | (series > upper)