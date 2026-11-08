# Build bennyg83/shulchan_aruch web reader into repo-root shulchan_aruch/ for diburim.org
# Requires: git, Node 20+, npm
param(
  [string]$SourceRepo = "https://github.com/bennyg83/shulchan_aruch.git",
  [string]$BasePath = "/shulchan_aruch/"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
$Work = Join-Path $Root "_import\shulchan_aruch_src"
$Dest = Join-Path $Root "shulchan_aruch"
$Reader = Join-Path $Work "newtry\OC_Mobile\oc-web-reader"

Write-Host "Diburim root: $Root"

if (Test-Path (Join-Path $Work ".git")) {
  Write-Host "Updating existing sparse checkout..."
  Push-Location $Work
  git pull --ff-only
  git sparse-checkout set "newtry/OC_Mobile/oc-web-reader" "newtry/OC_Mobile/oc318-mobile-reader/public"
  Pop-Location
} else {
  if (Test-Path $Work) {
    $fallback = Join-Path $Root ("_import\shulchan_aruch_build_" + [Guid]::NewGuid().ToString("n").Substring(0, 8))
    Write-Host "Work dir busy; using $fallback"
    $Work = $fallback
  }
  Write-Host "Sparse clone (corpus + reader only)..."
  git clone --depth 1 --filter=blob:none --sparse $SourceRepo $Work
  Push-Location $Work
  git sparse-checkout set "newtry/OC_Mobile/oc-web-reader" "newtry/OC_Mobile/oc318-mobile-reader/public"
  Pop-Location
}

if (-not (Test-Path (Join-Path $Reader "package.json"))) {
  throw "Reader checkout failed."
}

$catalog = Join-Path $Work "newtry\OC_Mobile\oc318-mobile-reader\public\corpus\oc1\catalog.json"
if (-not (Test-Path $catalog)) {
  throw "Corpus missing after sparse checkout."
}

Push-Location $Reader
Write-Host "npm ci..."
npm ci
$env:GITHUB_ACTIONS = "true"
$env:VITE_BASE = $BasePath
Write-Host "vite build (base $BasePath)..."
npm run build
Pop-Location

$Dist = Join-Path $Reader "dist"
if (-not (Test-Path (Join-Path $Dist "index.html"))) {
  throw "Build did not produce dist/index.html"
}

New-Item -ItemType Directory -Path $Dest -Force | Out-Null

# Copy-Item and Remove-Item fail on deep corpus paths; robocopy /MIR handles long paths.
$robocopyArgs = @(
  $Dist, $Dest,
  "/MIR", "/COPY:DAT", "/DCOPY:DAT", "/R:2", "/W:2", "/XJ", "/256", "/NFL", "/NDL", "/NJH", "/NJS"
)
$robocopy = Start-Process -FilePath robocopy.exe -ArgumentList $robocopyArgs -Wait -PassThru -NoNewWindow
# Robocopy: 0–7 = success (with informative bits); 8+ = hard failure.
if ($robocopy.ExitCode -ge 8) {
  throw "robocopy failed with exit code $($robocopy.ExitCode)"
}
if ($robocopy.ExitCode -ge 1) {
  Write-Host "robocopy exit code $($robocopy.ExitCode) (copied/updated files; re-run to fill any gaps)."
}

Write-Host "Deployed static reader to $Dest"
Write-Host "Commit shulchan_aruch/ and push to publish on diburim.org/shulchan_aruch/"
