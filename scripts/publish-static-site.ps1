$ErrorActionPreference = "Stop"

$Repo = Split-Path -Parent $PSScriptRoot
$Node = "C:\nvm4w\nodejs\node.exe"
$Wrangler = Join-Path $Repo "workers\askme\node_modules\wrangler\bin\wrangler.js"
$Pages = Join-Path $Repo "pages-demo"
$AskMe = Join-Path $Repo "workers\askme"
$TempWork = Join-Path $env:TEMP "healthcode-pages-publish"

Set-Location $Repo
python scripts\export_static_site.py --source http://127.0.0.1:8889 --public-url https://healthcodeanalysis.pages.dev --output pages-demo --clean
if ($LASTEXITCODE -ne 0) { throw "Static export failed" }

& $Node $Wrangler deploy --dry-run --config (Join-Path $AskMe "wrangler.toml") --outdir (Join-Path $env:TEMP "askme-dry-run")
if ($LASTEXITCODE -ne 0) { throw "AskMe validation failed" }

New-Item -ItemType Directory -Force -Path $TempWork | Out-Null
Remove-Item Env:\CLOUDFLARE_API_TOKEN -ErrorAction SilentlyContinue
Set-Location $TempWork

& $Node $Wrangler pages deploy $Pages --project-name healthcodeanalysis --branch main --commit-dirty=true
if ($LASTEXITCODE -ne 0) { throw "Pages deployment failed" }

& $Node $Wrangler deploy --config (Join-Path $AskMe "wrangler.toml")
if ($LASTEXITCODE -ne 0) { throw "AskMe deployment failed" }

Write-Host "Published static frontend and AskMe content index successfully."
