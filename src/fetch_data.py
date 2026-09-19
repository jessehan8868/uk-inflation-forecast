from pathlib import Path
import requests

ONS_CPI_URL = (
    "https://www.ons.gov.uk/generator?format=csv&uri=/economy/inflationandpriceindices/timeseries/d7g7/mm23"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
CPI_OUTPUT_PATH = PROJECT_ROOT / "data" / "raw" / "ons_cpi.csv"

def fetch_cpi(output_path: Path = CPI_OUTPUT_PATH) -> Path:
    try:
        response = requests.get(ONS_CPI_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            f"Failed to download ONS CPI data: {error}"
        ) from error
    
    if b'"CDID","D7G7"' not in response.content:
        raise ValueError(
            "The downloaded response does not contain ONS series D7G7"
        )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)

    return output_path

# BRENT

FRED_BRENT_URL = (
    "https://fred.stlouisfed.org/graph/"
    "fredgraph.csv?id=DCOILBRENTEU"
)

RAW_BRENT_PATH = (
    PROJECT_ROOT / "data" / "raw" / "fred_brent_daily.csv"
)

def fetch_brent(
        output_path: Path = RAW_BRENT_PATH,
) -> Path:
    
    try:
        response = requests.get(FRED_BRENT_URL, timeout=30)
        response.raise_for_status()
    except requests.RequestException as error:
        raise RuntimeError(
            f"Failed to download FRED Brent data: {error}"
        ) from error
    
    if b"observation_date,DCOILBRENTEU" not in response.content[:200]:
        raise ValueError(
            "The downloaded response is not FRED Brent series "
            "DCOILBRENTEU"
        )
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_bytes(response.content)

    return output_path


    
if __name__ == "__main__":

    cpi_file = fetch_cpi()
    brent_file = fetch_brent()

    print(f"Saved CPI data to {cpi_file}")
    print(f"Saved Brent data to {brent_file}")

