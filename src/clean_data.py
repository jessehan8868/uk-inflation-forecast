from pathlib import Path

import pandas as pd 

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RAW_CPI_PATH = PROJECT_ROOT / "data" / "raw" / "ons_cpi.csv"
CLEAN_CPI_PATH = PROJECT_ROOT / "data" / "interim" / "cpi_clean.csv"

def clean_cpi(
        raw_path: Path = RAW_CPI_PATH,
        output_path: Path = CLEAN_CPI_PATH,
) -> pd.DataFrame:
    
    raw = pd.read_csv(
        raw_path,
        header=None,
        names=["period", "value"],
        dtype=str,
    )

    if raw.empty:
        raise ValueError("The raw CPI file is empty")
    
    monthly_mask = raw["period"].str.fullmatch(
        r"\d{4} [A-Z]{3}",
        na=False
    )

    monthly = raw.loc[monthly_mask].copy()

    if monthly.empty:
        raise ValueError("No Monthly CPI observations were found")
    
    monthly["date"] = pd.to_datetime(
        monthly["period"],
        format="%Y %b",
        errors="raise",
    )

    monthly["cpi_yoy"] = pd.to_numeric(
        monthly["value"],
        errors="raise",
    )

    clean = monthly[["date", "cpi_yoy"]].copy()
    clean = clean.sort_values("date").reset_index(drop=True)

    if clean["date"].duplicated().any():
        raise ValueError("Duplicate monthly CPI dates were found")
    
    if clean.isna().any().any():
        raise ValueError("Missing values were found in the clean CPI data")
    
    if not clean["date"].is_monotonic_increasing:
        raise ValueError("CPI dates are not sorted chronologically")
    
    expected_dates = pd.date_range(
        start=clean["date"].min(),
        end=clean["date"].max(),
        freq="MS",
    )

    missing_dates = expected_dates.difference(clean["date"])

    if not missing_dates.empty:
        raise ValueError(
            f"Missing monthy CPI dates: {missing_dates.tolist()}"
        )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    clean.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    return clean


if __name__ == "__main__":
    clean_cpi_data = clean_cpi()
    print(
        f"Saved {len(clean_cpi_data)} monthly CPI observations "
        f"to {CLEAN_CPI_PATH}"
    )
