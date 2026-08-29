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

if __name__ == "__main__":
    saved_file = fetch_cpi()
    print(f"Saved CPI data to {saved_file}")
