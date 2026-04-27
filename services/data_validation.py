"""Input validation helpers for flood-clustering features."""
import math
from typing import Any

import pandas as pd


FIELD_RULES = {
    'curah_hujan': {
        'label': 'Curah Hujan',
        'min': 0,
        'max': 5000,
        'integer_only': False,
        'unit': 'mm/tahun',
        'outlier_message': 'rentang aman 0-5000 mm/tahun'
    },
    'kemiringan': {
        'label': 'Kemiringan',
        'min': 0,
        'max': 100,
        'integer_only': False,
        'unit': '%',
        'outlier_message': 'rentang aman 0-100%'
    },
    'banjir_histori': {
        'label': 'Histori Banjir',
        'min': 0,
        'max': 10,
        'integer_only': True,
        'unit': 'kejadian',
        'outlier_message': 'bilangan bulat 0-10 kejadian'
    }
}


def _coerce_numeric(value: Any):
    """Convert raw input into a numeric value."""
    if value is None:
        raise ValueError('kosong')

    raw_value = str(value).strip()
    if raw_value == '':
        raise ValueError('kosong')

    normalized_value = raw_value.replace(',', '.')
    try:
        number = float(normalized_value)
    except ValueError as exc:
        raise ValueError('bukan angka') from exc

    if not math.isfinite(number):
        raise ValueError('bukan angka valid')

    return number


def format_numeric_value(value: float, integer_only: bool = False) -> str:
    """Format cleaned numeric value back to a compact string."""
    if integer_only:
        return str(int(value))

    if float(value).is_integer():
        return str(int(value))

    return f"{value:.2f}".rstrip('0').rstrip('.')


def validate_feature_inputs(payload: dict[str, Any]):
    """Validate a single form payload for clustering features."""
    cleaned_payload = {}
    errors = []

    for field_name, rules in FIELD_RULES.items():
        raw_value = payload.get(field_name)

        try:
            number = _coerce_numeric(raw_value)
        except ValueError:
            errors.append(
                f"{rules['label']} wajib berupa angka yang valid."
            )
            continue

        if rules['integer_only'] and not number.is_integer():
            errors.append(
                f"{rules['label']} harus berupa bilangan bulat dengan {rules['outlier_message']}."
            )
            continue

        if number < rules['min'] or number > rules['max']:
            errors.append(
                f"{rules['label']} di luar batas valid, gunakan {rules['outlier_message']}."
            )
            continue

        cleaned_payload[field_name] = format_numeric_value(number, rules['integer_only'])

    return cleaned_payload, errors


def validate_dataframe_features(data: pd.DataFrame, context_label: str = 'dataset clustering'):
    """Validate feature columns before running K-means."""
    cleaned_data = data.copy()
    issues = []

    for field_name, rules in FIELD_RULES.items():
        numeric_series = pd.to_numeric(cleaned_data[field_name], errors='coerce')
        invalid_numeric_mask = numeric_series.isna()

        if invalid_numeric_mask.any():
            sample_rows = cleaned_data.loc[invalid_numeric_mask, 'nama_desa'].fillna('-').head(3).tolist()
            issues.append(
                f"{rules['label']} berisi nilai non-numerik pada desa: {', '.join(sample_rows)}."
            )
            continue

        if rules['integer_only']:
            invalid_integer_mask = (numeric_series % 1) != 0
            if invalid_integer_mask.any():
                sample_rows = cleaned_data.loc[invalid_integer_mask, 'nama_desa'].fillna('-').head(3).tolist()
                issues.append(
                    f"{rules['label']} harus bilangan bulat pada desa: {', '.join(sample_rows)}."
                )

        outlier_mask = (numeric_series < rules['min']) | (numeric_series > rules['max'])
        if outlier_mask.any():
            sample_rows = cleaned_data.loc[outlier_mask, 'nama_desa'].fillna('-').head(3).tolist()
            issues.append(
                f"{rules['label']} melewati {rules['outlier_message']} pada desa: {', '.join(sample_rows)}."
            )

        cleaned_data[field_name] = numeric_series.astype(int) if rules['integer_only'] else numeric_series.astype(float)

    if issues:
        issue_message = ' '.join(issues[:3])
        raise ValueError(
            f"Validasi {context_label} gagal. {issue_message}"
        )

    return cleaned_data
