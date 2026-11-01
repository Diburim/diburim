# Serve Diburim from the repo root (required for data/ and content/ paths).
Set-Location $PSScriptRoot + "\.."
Write-Host "Serving Diburim at http://127.0.0.1:8765/"
Write-Host "Project root: $(Get-Location)"
Write-Host "Catalog pieces: $((Get-Content 'data\catalog.json' -Raw | ConvertFrom-Json).pieces.Count)"
python -m http.server 8765
