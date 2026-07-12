$ErrorActionPreference = "Stop"

$Repo = "D:\Website and project\Demo\healthcodeanalysis"
$SourceHtml = Join-Path $Repo "debug\live-homepage.html"
$OutDir = Join-Path $Repo "pages-demo"
$SourceBase = "http://127.0.0.1:8888"
$OldBase = "https://healthcodeanalysis.com"
$NewBase = "https://healthcodeanalysis.pages.dev"

if (!(Test-Path $SourceHtml)) {
  throw "Missing source HTML: $SourceHtml"
}

$html = Get-Content -Raw -Path $SourceHtml

$assetPattern = 'https://healthcodeanalysis\.com/(?<path>(?:wp-content|wp-includes)/[^''"")<>\s]+)'
$matches = [regex]::Matches($html, $assetPattern)
$assetPaths = New-Object 'System.Collections.Generic.HashSet[string]'

foreach ($match in $matches) {
  $path = $match.Groups["path"].Value
  $path = ($path -replace '&amp;', '&')
  $path = ($path -split '[?#]')[0]
  if ($path) {
    [void]$assetPaths.Add($path)
  }
}

foreach ($path in $assetPaths) {
  $target = Join-Path $OutDir ($path -replace '/', '\')
  $targetDir = Split-Path -Parent $target
  New-Item -ItemType Directory -Force -Path $targetDir | Out-Null

  $uri = "$SourceBase/$path"
  try {
    Invoke-WebRequest -Uri $uri -OutFile $target -UseBasicParsing -TimeoutSec 45 | Out-Null
  } catch {
    Write-Warning "Failed asset: $uri"
  }
}

$html = $html -replace 'https://healthcodeanalysis\.com/wp-content/', "$NewBase/wp-content/"
$html = $html -replace 'https://healthcodeanalysis\.com/wp-includes/', "$NewBase/wp-includes/"
$html = $html -replace 'https://healthcodeanalysis\.com/wp-json/[^''"")<>\s]*', "$NewBase/"
$html = $html -replace 'https://healthcodeanalysis\.com/wp-admin/admin-ajax\.php', "$NewBase/"
$html = $html -replace 'https://healthcodeanalysis\.com/wp-login\.php', "http://127.0.0.1:8888/wp-login.php"
$html = $html -replace 'https://healthcodeanalysis\.com/', "$NewBase/"
$html = $html -replace 'https://healthcodeanalysis\.com', "$NewBase"

Set-Content -Path (Join-Path $OutDir "index.html") -Value $html -Encoding UTF8

Write-Host "Exported homepage and $($assetPaths.Count) asset references to $OutDir"
