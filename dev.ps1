param(
  [string]$Host = "127.0.0.1",
  [int]$Port = 4000,
  [switch]$SkipNpm
)

$ErrorActionPreference = "Stop"

Write-Host "[1/3] Checking required tools..."
if (-not (Get-Command ruby -ErrorAction SilentlyContinue)) { throw "Ruby is not installed." }
if (-not (Get-Command bundle -ErrorAction SilentlyContinue)) { throw "Bundler is not installed." }

Write-Host "[2/3] Installing Ruby dependencies (bundle install)..."
bundle install

if (-not $SkipNpm -and (Test-Path "package.json")) {
  if (Get-Command npm -ErrorAction SilentlyContinue) {
    Write-Host "[optional] Installing Node dependencies (npm install)..."
    npm install
  } else {
    Write-Host "npm not found; skipping npm install."
  }
}

Write-Host "[3/3] Starting local site at http://${Host}:${Port}"
bundle exec jekyll serve --host $Host --port $Port --livereload
