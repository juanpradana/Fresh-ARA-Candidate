#requires -Version 5.1
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidatePattern('^\d{4}-\d{2}-\d{2}$')]
    [string]$Date,

    [string]$Preset = "balanced",
    [string]$FeatureVersion = "v2",
    [double]$Qps = 2.0,
    [int]$BatchSize = 50
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Run-Step {
    param(
        [Parameter(Mandatory = $true)][string]$Title,
        [Parameter(Mandatory = $true)][scriptblock]$Action
    )
    Write-Host "`n=== $Title ===" -ForegroundColor Cyan
    & $Action
    if ($LASTEXITCODE -ne 0) {
        throw "Step failed: $Title (exit code $LASTEXITCODE)"
    }
}

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Push-Location $repoRoot
try {
    $exportPath = "data/features_$Date.parquet"

    Run-Step "Update market data" {
        python -m app.backend.cli.main update-market --date $Date --qps $Qps --batch-size $BatchSize --universe-mode external_live
    }

    Run-Step "Daily smoke check" {
        python -m app.backend.cli.main daily-smoke --date $Date --qps $Qps --batch-size $BatchSize --universe-mode external_live
    }

    Run-Step "Compute features (rich)" {
        python -m app.backend.cli.main compute-features --date $Date --feature-version $FeatureVersion
    }

    Run-Step "Run screening (rich)" {
        python -m app.backend.cli.main run-screening --date $Date --preset $Preset --feature-version $FeatureVersion
    }

    Run-Step "Export features dataset" {
        python -m app.backend.cli.main export-market-data --date $Date --dataset features --feature-version $FeatureVersion --output $exportPath --format parquet
    }

    Run-Step "Sanity checks in SQLite" {
        $dbPath = if ($env:APP_DB_PATH) { $env:APP_DB_PATH } else { "./data/fresh_ara.sqlite" }
        if (-not [System.IO.Path]::IsPathRooted($dbPath)) {
            $dbPath = Join-Path $repoRoot $dbPath
        }
        $dbPath = [System.IO.Path]::GetFullPath($dbPath)

        if (-not (Test-Path $dbPath)) {
            throw "Database file not found at: $dbPath"
        }

        $sanityCode = @'
import sqlite3
import sys

d = sys.argv[1]
feature_version = sys.argv[2]
preset = sys.argv[3]
db_path = sys.argv[4]

con = sqlite3.connect(db_path)
cur = con.cursor()

required_tables = {"prices_daily", "features_daily", "screening_results"}
cur.execute("select name from sqlite_master where type='table'")
existing_tables = {row[0] for row in cur.fetchall()}
missing_tables = sorted(required_tables - existing_tables)
if missing_tables:
    print(f"UAT FAILED: missing tables in {db_path}: {', '.join(missing_tables)}")
    sys.exit(1)

checks = {
    "prices_rows": f"select count(*) from prices_daily where trade_date='{d}'",
    "features_rows": f"select count(*) from features_daily where trade_date='{d}' and feature_version='{feature_version}'",
    "screening_rows": f"select count(*) from screening_results where screen_date='{d}' and preset_name='{preset}'",
    "missing_new_cols": f"""
        select count(*) from features_daily
        where trade_date='{d}' and feature_version='{feature_version}' and (
            consecutive_green_days is null or
            rsi14 is null or
            rsi14_slope is null or
            atr5_atr20_ratio is null or
            dist_to_52w_high_pct is null
        )
    """,
    "rsi_out_of_range": f"""
        select count(*) from features_daily
        where trade_date='{d}' and feature_version='{feature_version}' and (rsi14 < 0 or rsi14 > 100)
    """,
    "negative_cgd": f"""
        select count(*) from features_daily
        where trade_date='{d}' and feature_version='{feature_version}' and consecutive_green_days < 0
    """,
    "negative_atr_ratio": f"""
        select count(*) from features_daily
        where trade_date='{d}' and feature_version='{feature_version}' and atr5_atr20_ratio < 0
    """,
}

results = {}
for name, query in checks.items():
    cur.execute(query)
    results[name] = int(cur.fetchone()[0])

con.close()

print("UAT Sanity Results:")
for k, v in results.items():
    print(f"  {k}: {v}")

failures = []
if results["prices_rows"] <= 0:
    failures.append("prices_rows must be > 0")
if results["features_rows"] <= 0:
    failures.append("features_rows must be > 0")
if results["screening_rows"] <= 0:
    failures.append("screening_rows must be > 0")
if results["missing_new_cols"] != 0:
    failures.append("missing_new_cols must be 0")
if results["rsi_out_of_range"] != 0:
    failures.append("rsi_out_of_range must be 0")
if results["negative_cgd"] != 0:
    failures.append("negative_cgd must be 0")
if results["negative_atr_ratio"] != 0:
    failures.append("negative_atr_ratio must be 0")

if failures:
    print("\nUAT FAILED:")
    for item in failures:
        print(" -", item)
    sys.exit(1)

print("\nUAT PASSED")
'@
        $sanityFile = Join-Path $env:TEMP "fresh_ara_uat_sanity.py"
        Set-Content -Path $sanityFile -Value $sanityCode -Encoding UTF8
        try {
            python $sanityFile $Date $FeatureVersion $Preset $dbPath
        }
        finally {
            Remove-Item -Path $sanityFile -ErrorAction SilentlyContinue
        }
    }

    Run-Step "API contract smoke tests" {
        pytest -q tests/backend/test_api_contract.py
    }

    Run-Step "Frontend build check" {
        npm --prefix app/frontend run build
    }

    Write-Host "`nAll UAT steps PASSED for $Date." -ForegroundColor Green
    Write-Host "Export file: $exportPath"
}
finally {
    Pop-Location
}
