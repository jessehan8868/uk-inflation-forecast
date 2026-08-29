# UK Inflation Forecasting Project Roadmap

## 1. Project purpose

Build an end-to-end Python forecasting pipeline that collects raw economic and market data, cleans and aligns it, engineers economically meaningful features, trains forecasting models, backtests them correctly through time, and produces interpretable UK inflation forecasts.

The project should be useful preparation for research work involving:
- collecting raw market and macroeconomic data
- handling inconsistent and messy data sources
- building forward-looking forecasting models
- comparing model performance
- interpreting results economically
- producing outputs that finance/economics researchers can use

The emphasis is not on building the most complicated model possible. The emphasis is on building a clean, reproducible research pipeline and understanding every step.

---

## 2. Main research question

Primary question:

> Given information available today, how accurately can UK CPI inflation be forecast 3, 6, and 12 months ahead?

Secondary questions:
- Which variables add useful predictive information?
- Do market variables improve forecasts beyond past inflation alone?
- How stable are model relationships through time?
- Which periods produce the largest forecast errors, and why?
- Do more complex machine learning models materially outperform simpler economic models?

---

## 3. Initial target variable

Primary target:
- UK CPI annual inflation rate

Forecast horizons:
- 3 months ahead
- 6 months ahead
- 12 months ahead

Example target construction:

```python
df["target_3m"] = df["cpi_yoy"].shift(-3)
df["target_6m"] = df["cpi_yoy"].shift(-6)
df["target_12m"] = df["cpi_yoy"].shift(-12)
```

Start with one horizon, preferably 6 months, before generalising.

---

## 4. Suggested data

Start small. Add variables gradually after the basic pipeline works.

### Core macro variables

Potential sources:
- Office for National Statistics
- Bank of England
- FRED
- OECD
- World Bank
- IMF

Potential features:
- CPI inflation
- core CPI
- Bank Rate
- unemployment rate
- average earnings / wage growth
- retail sales
- industrial production
- producer prices
- money supply
- GDP growth

### Market variables

Potential features:
- Brent crude oil prices
- UK / European natural gas prices
- GBP/USD
- GBP/EUR
- UK government bond yields
- yield-curve slope
- equity index returns
- commodity price indices

### Optional later additions

Only add these after the core pipeline is working:
- PMI data
- inflation expectations
- shipping/freight measures
- global supply chain pressure indicators
- food commodity prices
- housing indicators

Avoid collecting twenty variables immediately. The first working dataset can contain only CPI, Bank Rate, Brent crude and GBP/USD.

---

## 5. Repository structure

Use this structure:

```text
uk-inflation-forecast/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── notebooks/
│   └── 01_exploration.ipynb
│
├── src/
│   ├── __init__.py
│   ├── fetch_data.py
│   ├── clean_data.py
│   ├── features.py
│   ├── models.py
│   └── evaluate.py
│
├── outputs/
│   ├── charts/
│   ├── forecasts/
│   └── tables/
│
├── tests/
│
├── main.py
├── requirements.txt
├── README.md
├── PROJECT_ROADMAP.md
└── .gitignore
```

### Folder responsibilities

#### `data/raw/`
Original downloaded data.

Rules:
- do not manually edit raw files
- preserve original column names and values where practical
- use clear source-specific filenames

Examples:
- `ons_cpi.csv`
- `boe_bank_rate.csv`
- `brent_daily.csv`

#### `data/interim/`
Partially transformed datasets.

Examples:
- `brent_monthly.csv`
- `cpi_clean.csv`

#### `data/processed/`
Final model-ready datasets.

Example:
- `forecast_dataset.csv`

#### `notebooks/`
Exploratory analysis only.

Use notebooks for:
- plotting
- checking distributions
- examining missingness
- understanding source data
- trying transformations

Do not allow the final pipeline to become one giant notebook.

#### `src/`
Reusable project logic.

#### `outputs/`
Generated forecasts, tables and charts.

#### `tests/`
Unit tests and data-validation checks.

---

## 6. Python environment

Use a local virtual environment.

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Initial packages:

```bash
pip install pandas numpy matplotlib scikit-learn requests openpyxl jupyter statsmodels
```

Possible later additions:

```bash
pip install xgboost fredapi
```

Record dependencies:

```bash
pip freeze > requirements.txt
```

Do not install libraries without a clear reason.

---

## 7. Git and GitHub workflow

Git should track meaningful development milestones.

Typical workflow:

```bash
git status
git add .
git commit -m "Add ONS CPI data fetch"
git push
```

Good commit examples:
- `Initial project setup`
- `Add CPI data source`
- `Clean CPI series`
- `Add Brent crude data`
- `Align monthly datasets`
- `Add lagged inflation features`
- `Add naive forecast benchmark`
- `Add rolling backtest`
- `Add Ridge regression model`
- `Add forecast visualisation`

Avoid meaningless commits such as:
- `update`
- `stuff`
- `fixed thing`

Do not commit:
- `.venv/`
- API keys
- passwords
- secrets
- temporary Python caches

Recommended `.gitignore`:

```text
.venv/
__pycache__/
.ipynb_checkpoints/
.DS_Store
*.pyc
.env
```

---

## 8. Development philosophy

Build the project in small working stages.

Do not attempt to build the final forecasting system in one pass.

Each stage should:
1. run successfully
2. produce a useful output
3. be committed to Git
4. be understood before progressing

---

# Milestone roadmap

## Milestone 0: Project setup

Status: complete when repository, environment and folder structure work.

Tasks:
- create repository
- initialise Git
- set `.gitignore`
- create virtual environment
- install dependencies
- create folder structure
- create basic README

Deliverable:
- clean GitHub repository

---

## Milestone 1: Fetch one CPI series

Goal:
Successfully download UK CPI data and save it unchanged to `data/raw/`.

Tasks:
- identify reliable ONS CPI source
- inspect the raw response or downloaded file
- write a fetch function in `src/fetch_data.py`
- save raw data
- add error handling for failed requests

Possible interface:

```python
def fetch_cpi() -> pd.DataFrame:
    ...
```

Questions to answer:
- what is the exact measure?
- monthly or quarterly?
- seasonally adjusted?
- percentage rate or index level?
- how far back does the series go?

Deliverable:
- `data/raw/ons_cpi.csv`

Suggested commit:

```text
Add ONS CPI data fetch
```

---

## Milestone 2: Clean CPI data

Goal:
Create a clean monthly CPI time series.

Tasks:
- parse dates
- rename columns
- ensure numeric values
- sort chronologically
- detect duplicates
- inspect missing values
- document transformations

Possible function:

```python
def clean_cpi(df: pd.DataFrame) -> pd.DataFrame:
    ...
```

Expected output columns:

```text
date,cpi_yoy
```

Deliverable:
- `data/interim/cpi_clean.csv`

Suggested commit:

```text
Clean CPI series
```

---

## Milestone 3: Add first market variable

Recommended first variable:
- Brent crude oil price

Goal:
Fetch and transform a higher-frequency market series into monthly data.

Tasks:
- fetch daily or weekly Brent data
- clean dates and values
- convert to monthly frequency
- choose monthly mean or end-of-month value
- justify the choice

Possible transformation:

```python
monthly = daily.resample("ME").mean()
```

Do not use resampling blindly. Confirm the date index is correct first.

Deliverable:
- `data/interim/brent_monthly.csv`

Suggested commit:

```text
Add Brent crude data
```

---

## Milestone 4: Merge datasets

Goal:
Create the first combined modelling dataset.

Initial variables:
- CPI
- Brent crude

Then add:
- Bank Rate
- GBP/USD

Tasks:
- align all data to monthly timestamps
- check merge behaviour
- inspect missing values after joins
- avoid blindly calling `dropna()`
- document how different frequencies are handled

Possible output:

```text
date,cpi_yoy,brent,bank_rate,gbpusd
```

Deliverable:
- `data/processed/base_dataset.csv`

Suggested commit:

```text
Align monthly macro datasets
```

---

## Milestone 5: Feature engineering

Goal:
Turn raw economic variables into useful predictors.

Potential features:

### Inflation lags

```python
df["cpi_lag1"] = df["cpi_yoy"].shift(1)
df["cpi_lag3"] = df["cpi_yoy"].shift(3)
df["cpi_lag12"] = df["cpi_yoy"].shift(12)
```

### Oil changes

```python
df["oil_mom"] = df["brent"].pct_change(1)
df["oil_yoy"] = df["brent"].pct_change(12)
```

### Currency changes

```python
df["gbp_yoy"] = df["gbpusd"].pct_change(12)
```

### Rate changes

```python
df["rate_change_3m"] = df["bank_rate"].diff(3)
```

### Forecast target

```python
df["target_6m"] = df["cpi_yoy"].shift(-6)
```

Important:
Every feature must use information that would have been available at the forecast date.

Deliverable:
- model-ready dataset

Suggested commit:

```text
Add inflation forecasting features
```

---

## Milestone 6: Exploratory analysis

Goal:
Understand relationships before modelling.

Analyse:
- inflation through time
- oil prices through time
- relationship between oil changes and later inflation
- inflation persistence
- missingness
- unusual periods

Charts to consider:
- CPI time series
- oil price time series
- CPI vs lagged CPI scatter plot
- forecast-variable correlations

Avoid treating correlation as causation.

Deliverable:
- `notebooks/01_exploration.ipynb`
- useful charts in `outputs/charts/`

---

## Milestone 7: Naive benchmark

This is essential.

Before sophisticated models, build a simple baseline.

Example persistence forecast:

```text
future inflation = current inflation
```

Why:
A forecasting model is only useful if it beats a simple baseline.

Evaluation metrics:
- MAE
- RMSE

Possible functions:

```python
def naive_forecast(...):
    ...
```

Suggested commit:

```text
Add naive inflation forecast benchmark
```

---

## Milestone 8: Autoregressive model

Goal:
Forecast inflation using its own history.

Example:

```text
CPI(t+6) = b0 + b1 CPI(t) + b2 CPI(t-1) + b3 CPI(t-3) + error
```

Potential implementation:
- `statsmodels`
- scikit-learn linear regression over lagged features

Questions:
- how many lags help?
- does adding more lags improve out-of-sample performance?

Suggested commit:

```text
Add autoregressive inflation model
```

---

## Milestone 9: Macro linear model

Add external predictors.

Example specification:

```text
CPI(t+6)
= b0
+ b1 CPI(t)
+ b2 OilGrowth(t)
+ b3 WageGrowth(t)
+ b4 GBPChange(t)
+ b5 BankRate(t)
+ error
```

Start with ordinary linear regression.

Then consider:
- Ridge
- Lasso

Why Ridge/Lasso:
Macro variables can be correlated and the sample will not be enormous.

Suggested commit:

```text
Add macro regression forecast
```

---

## Milestone 10: Proper time-series backtesting

This is one of the most important parts of the project.

Do not use random train-test splitting.

Bad:

```python
train_test_split(..., shuffle=True)
```

This leaks future information.

Use expanding-window or rolling-window validation.

Example:

```text
Train 2005-2015 -> predict 2016
Train 2005-2016 -> predict 2017
Train 2005-2017 -> predict 2018
...
```

Possible tool:

```python
from sklearn.model_selection import TimeSeriesSplit
```

Better still, explicitly implement the forecast-date logic so it is easy to inspect.

Evaluate each model using identical forecast dates.

Deliverable:
- model comparison table

Example:

```text
Model                 RMSE    MAE
Naive                 1.42    1.08
Autoregressive        1.17    0.90
Ridge                 0.98    0.76
```

Suggested commit:

```text
Add expanding-window backtest
```

---

## Milestone 11: Machine learning models

Only after simpler models work.

Potential models:
- Random Forest
- Gradient Boosting
- XGBoost

Do not use neural networks for the sake of complexity.

Monthly macro data usually provides a relatively small sample.

Questions:
- do ML models actually beat Ridge or autoregression?
- are results stable across periods?
- which variables matter most?

Suggested commit:

```text
Add tree-based forecasting models
```

---

## Milestone 12: Forecast visualisation

Produce clear plots showing:
- actual inflation
- historical model forecasts
- latest forward forecast

Suggested output:

```text
outputs/charts/actual_vs_forecast.png
```

Also consider showing forecast errors over time.

Charts should be understandable to someone who has not read the code.

---

## Milestone 13: Economic interpretation

This project should not end with a model score.

Investigate:
- when did the model fail badly?
- why?
- were relationships unstable?
- were there regime changes?
- were energy shocks important?
- did inflation persistence change?

Possible case study:
- 2021-2023 inflation surge

Explain why models trained on historical relationships struggled or succeeded.

This is likely more useful for economic research than squeezing another 0.02 from RMSE.

---

## Milestone 14: Generalise the pipeline

Once the UK CPI system works, make the code configurable.

Possible configuration:

```python
TARGET = "UK_CPI"
HORIZON = 6
```

Later:

```python
TARGET = "UK_GDP"
HORIZON = 3
```

Or:

```python
TARGET = "US_UNEMPLOYMENT"
HORIZON = 6
```

Long-term goal:

```bash
python main.py --country UK --target CPI --horizon 6
```

Pipeline:

```text
fetch data
-> clean data
-> align frequencies
-> engineer features
-> train models
-> backtest
-> generate forecasts
-> produce charts/tables
```

Do not generalise prematurely. Build one working target first.

---

# Code architecture

## `src/fetch_data.py`

Responsibilities:
- API calls
- file downloads
- raw data loading
- request error handling

Example functions:

```python
def fetch_cpi():
    ...

def fetch_bank_rate():
    ...

def fetch_brent():
    ...

def fetch_gbpusd():
    ...
```

Do not mix major cleaning logic into fetching functions.

---

## `src/clean_data.py`

Responsibilities:
- date parsing
- numeric conversion
- column naming
- duplicate handling
- missing-data checks
- frequency conversion

Example:

```python
def clean_cpi(df):
    ...

def clean_brent(df):
    ...
```

---

## `src/features.py`

Responsibilities:
- lags
- percentage changes
- differences
- rolling statistics
- forecast target creation

Example:

```python
def add_lags(df):
    ...

def add_growth_features(df):
    ...

def create_target(df, horizon):
    ...
```

---

## `src/models.py`

Responsibilities:
- model definitions
- training functions
- prediction functions

Models may eventually include:
- naive benchmark
- linear regression
- Ridge
- Lasso
- Random Forest
- XGBoost

---

## `src/evaluate.py`

Responsibilities:
- MAE
- RMSE
- backtesting
- forecast comparison
- error analysis

Possible functions:

```python
def calculate_rmse(y_true, y_pred):
    ...

def expanding_window_backtest(...):
    ...
```

---

## `main.py`

Eventually acts as the pipeline entry point.

Possible structure:

```python
from src.fetch_data import fetch_cpi
from src.clean_data import clean_cpi


def main():
    raw_cpi = fetch_cpi()
    clean = clean_cpi(raw_cpi)
    ...


if __name__ == "__main__":
    main()
```

Keep `main.py` relatively small. Most logic should live in `src/`.

---

# Data-quality rules

Treat data quality as part of the project, not an inconvenience.

Every new dataset should be checked for:
- duplicate dates
- missing observations
- impossible values
- incorrect units
- frequency changes
- revisions
- inconsistent date conventions
- unexpected gaps

Useful checks:

```python
assert df.index.is_monotonic_increasing
assert not df.index.duplicated().any()
```

Do not blindly remove missing observations.

Always ask why observations are missing first.

---

# Forecasting rules

## Rule 1: No future leakage

At forecast time `t`, use only information available by time `t`.

Be particularly careful with:
- shifted variables
- rolling averages
- revised macroeconomic data
- normalisation/scaling

Scalers should be fitted only on training data inside each backtest window.

## Rule 2: Always compare against a baseline

A sophisticated model that fails to beat persistence is not useful.

## Rule 3: Prefer out-of-sample results

In-sample fit is not evidence of forecasting ability.

## Rule 4: Keep economic reasoning involved

Features should have plausible economic interpretation.

## Rule 5: Complexity must earn its place

Do not add complexity unless it produces useful improvements or insight.

---

# Evaluation plan

Primary metrics:
- RMSE
- MAE

Optional later metrics:
- directional accuracy
- forecast bias

For each model record:
- forecast horizon
- training period
- test period
- variables
- hyperparameters
- MAE
- RMSE

Save model comparison tables to:

```text
outputs/tables/
```

---

# Testing roadmap

Initially simple.

Example tests:

```python
def test_cpi_has_no_duplicate_dates():
    ...
```

```python
def test_target_shift_is_correct():
    ...
```

```python
def test_monthly_dataset_is_sorted():
    ...
```

Later test:
- feature functions
- expected columns
- missing-value rules
- backtest ordering

The most important tests are those preventing silent data errors and future leakage.

---

# README roadmap

The final README should allow a recruiter/researcher to understand the project quickly.

Suggested sections:

```text
# UK Inflation Forecasting Pipeline

## Overview
## Research Question
## Data Sources
## Pipeline
## Features
## Models
## Backtesting Methodology
## Results
## Forecast Visualisations
## Repository Structure
## Installation
## Usage
## Limitations
## Future Improvements
```

Keep the README concise and factual.

Do not claim predictive success unless supported by the backtest.

---

# Possible final outputs

The finished project should ideally produce:

```text
data/processed/forecast_dataset.csv
outputs/forecasts/latest_forecast.csv
outputs/tables/model_comparison.csv
outputs/charts/actual_vs_forecast.png
outputs/charts/forecast_errors.png
```

And console output resembling:

```text
UK CPI Forecast
Forecast date: 2026-08
Horizon: 6 months

Naive: 2.8%
Autoregressive: 2.6%
Ridge: 2.4%
XGBoost: 2.5%

Best historical RMSE: Ridge
```

---

# Suggested first ten commits

1. `Initial project setup`
2. `Add project directory structure`
3. `Add ONS CPI data fetch`
4. `Clean CPI series`
5. `Add Brent crude data`
6. `Align monthly datasets`
7. `Add inflation lag features`
8. `Add naive forecast benchmark`
9. `Add autoregressive model`
10. `Add expanding-window backtest`

---

# How Codex should assist

The purpose of this project is learning and preparation, not outsourcing the entire build.

Codex should behave like a technical pair programmer.

## Preferred behaviour

When helping with a task:
1. explain what is being built
2. explain important design choices
3. keep changes small
4. modify only relevant files
5. show what changed
6. run appropriate checks/tests
7. point out questionable assumptions
8. avoid silently introducing unnecessary dependencies

Codex should not automatically build large sections of the project without explanation.

For unfamiliar concepts, explain them before or alongside implementation.

Good request example:

> Help me implement the CPI fetching stage. First inspect the existing repository, then identify the cleanest approach for retrieving the ONS series. Explain the source structure and proposed implementation before changing files. Keep the first version simple.

Bad workflow:

> Build the entire forecasting project.

The user should remain able to explain:
- where each dataset comes from
- how it is cleaned
- why each feature exists
- how the forecast target works
- why the backtest avoids leakage
- why one model performs better than another

---

# Immediate next task

Start Milestone 1.

Objective:

> Fetch one official UK CPI series and save the raw result into `data/raw/`.

Before coding:
1. identify the exact CPI series
2. inspect the source/API format
3. decide what raw response should be preserved
4. implement the smallest working fetch function
5. run it locally
6. inspect the saved data
7. commit only after it works

Do not move onto oil, exchange rates or modelling until this first data pipeline works cleanly.
