from pathlib import Path

import pandas as pd 

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_CPI_PATH = PROJECT_ROOT / "data" / "raw" / "ons_cpi.csv"
CLEAN_CPI_PATH = PROJECT_ROOT / "data" / "interim" / "cpi_clean.csv"

RAW_BRENT_PATH = PROJECT_ROOT / "data" / "raw" / "fred_brent_daily.csv"
MONTHLY_BRENT_PATH = PROJECT_ROOT / "data" / "interim" / "brent_monthly.csv"


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


def clean_brent(
        raw_path: Path = RAW_BRENT_PATH,
        output_path: Path = MONTHLY_BRENT_PATH,
) -> pd.DataFrame:
    
    raw = pd.read_csv(raw_path, dtype=str)

    if raw.empty:
        raise ValueError("The raw Brent is empty.")
    
    expected_columns = {
        "observation_date",
        "DCOILBRENTEU",
    }

    if set(raw.columns) != expected_columns:
        raise ValueError(
            f"Unexpected Brent columns: {raw.columns.tolist()}"
        )
    
    raw["date"] = pd.to_datetime(
        raw["observation_date"],
        format="%Y-%m-%d",
        errors="raise",
    )

    raw["brent_usd_per_barrel"] = pd.to_numeric(
        raw["DCOILBRENTEU"],
        errors="coerce",
    )

    invalid_values = (
        raw["DCOILBRENTEU"].notna()
        & raw["brent_usd_per_barrel"].isna()
    )

    if invalid_values.any():
        raise ValueError("Invalid non-numeric Brent prices were found")
    
    if raw["date"].duplicated().any():
        raise ValueError("Duplicate daily Brent dates were found")
    
    raw = raw.sort_values("date").reset_index(drop=True)

    current_month = pd.Timestamp.today().to_period("M")

    complete_month_mask = (
        raw["date"].dt.to_period("M") < current_month
    )

    complete_daily = raw.loc[complete_month_mask].copy()

    available_daily = complete_daily.dropna(
        subset=["brent_usd_per_barrel"]
    )

    monthly = (
        available_daily
        .set_index("date")["brent_usd_per_barrel"]
        .resample("MS")
        .mean()
        .rename("brent_usd_per_barrel")
        .reset_index()
    )

    if monthly["brent_usd_per_barrel"].isna().any():
        raise ValueError("Missing monthly Brent values were found")
    
    if monthly["date"].duplicated().any():
        raise ValueError("Duplicate monthly Brent dates were found")
    
    if not monthly["date"].is_monotonic_increasing:
        raise ValueError("Monthly Brent dates are not chronological")
    
    expected_dates = pd.date_range(
        start=monthly["date"].min(),
        end=monthly["date"].max(),
        freq="MS",
    )

    missing_months = expected_dates.difference(monthly["date"])

    if not missing_months.empty:
        raise ValueError(
            f"Missing Brent months: {missing_months.tolist()}"
        )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    monthly.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    return monthly



    

if __name__ == "__main__":
    clean_cpi_data = clean_cpi()
    monthly_brent_data = clean_brent()

    print(
        f"Saved {len(clean_cpi_data)} monthly CPI observations "
        f"to {CLEAN_CPI_PATH}"
    )
    print(
        f"Saved {len(monthly_brent_data)} monthly Brent "
        f"observations to {MONTHLY_BRENT_PATH}"
    )




