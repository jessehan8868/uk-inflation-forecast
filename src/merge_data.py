from pathlib import Path
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CPI_PATH = PROJECT_ROOT / "data" / "interim" / "cpi_clean.csv"
BRENT_PATH = PROJECT_ROOT / "data" / "interim" / "brent_monthly.csv"
BASE_DATASET_PATH = (
    PROJECT_ROOT / "data" / "processed" / "base_dataset.csv"
)

def build_base_dataset(
        cpi_path: Path = CPI_PATH,
        brent_path: Path = BRENT_PATH,
        output_path: Path = BASE_DATASET_PATH,
) -> pd.DataFrame:
    
    for input_path in (cpi_path, brent_path):
        if not input_path.exists():
            raise FileNotFoundError(
                f"Required input file not found: {input_path}"
            )
        
    cpi = pd.read_csv(cpi_path)
    brent = pd.read_csv(brent_path)

    if cpi.empty:
        raise ValueError("The clean CPI dataset is empty")
    if brent.empty:
        raise ValueError("The monthly Brent dataset is empty")
    
    expected_cpi_columns = ["date", "cpi_yoy"]
    expected_brent_columns = ["date", "brent_usd_per_barrel"]

    if cpi.columns.tolist() != expected_cpi_columns:
        raise ValueError(
            f"Unexpected CPI columns: {cpi.columns.tolist()}"
        )
    
    if brent.columns.tolist() != expected_brent_columns:
        raise ValueError(
            f"Unexpected Brent columns: {brent.columns.tolist()}"
        )
    
    cpi["date"] = pd.to_datetime(
        cpi["date"],
        format="%Y-%m-%d",
        errors="raise",
    )

    brent["date"] = pd.to_datetime(
        brent["date"],
        format="%Y-%m-%d",
        errors="raise",
    )

    if not cpi["date"].dt.is_month_start.all():
        raise ValueError("CPI dates must use month-start timestamp.")
    if not brent["date"].dt.is_month_start.all():
        raise ValueError("Brent dates must use month-start timestamps.")
    
    if cpi["date"].duplicated().any():
        raise ValueError("Duplicate CPI dates were found")
    if brent["date"].duplicated().any():
        raise ValueError("Duplicate Brent dates were found")
    
    cpi["cpi_yoy"] = pd.to_numeric(
        cpi["cpi_yoy"],
        errors="raise",
    )

    brent["brent_usd_per_barrel"] = pd.to_numeric(
        brent["brent_usd_per_barrel"],
        errors="raise",
    )

    if cpi.isna().any().any():
        raise ValueError("Missing values were found in the CPI input.")

    if brent.isna().any().any():
        raise ValueError("Missing values were found in the Brent input.")
    
    cpi = cpi.sort_values("date").reset_index(drop=True)
    brent = brent.sort_values("date").reset_index(drop=True)

    merged = cpi.merge(
        brent,
        on="date",
        how="left",
        validate="one_to_one",
        indicator=True,
    )

    unmatched_dates = merged.loc[
        merged["_merge"] == "left_only",
        "date",
    ]

    if not unmatched_dates.empty:
        raise ValueError(
            "CPI months without matching Brent data: "
            f"{unmatched_dates.dt.strftime('%Y-%m-%d').tolist()}"
        )
    
    merged = merged.drop(columns="_merge")

    if len(merged) != len(cpi):
        raise ValueError(
            "The merged row count does not match the CPI row count"
        )
    
    if merged.isna().any().any():
        raise ValueError(
            "Missing values were found after merging CPI and Brent."
        )
    
    if merged["date"].duplicated().any():
        raise ValueError("Duplicate dates were found after merging")
    
    if not merged["date"].is_monotonic_increasing:
        raise ValueError("Merged dates are not chronological.")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)

    merged.to_csv(
        output_path,
        index=False,
        date_format="%Y-%m-%d",
    )

    return merged


if __name__ == "__main__":
    base_dataset = build_base_dataset()

    print(
        f"Saved {len(base_dataset)} monthly observations "
        f"to {BASE_DATASET_PATH}"
    )

