param(
  [int]$Top = 20,
  [string]$Since = ""
)

# Usage:
#   .\scripts\most-changed.ps1
#   .\scripts\most-changed.ps1 -Top 50
#   .\scripts\most-changed.ps1 -Since "2025-01-01"

$sinceArgs = @()
if ($Since -ne "") {
  $sinceArgs = @("--since=$Since")
}

git log --pretty=format: --name-only @sinceArgs |
  Where-Object { $_ -and ($_ -notmatch '^\s*$') } |
  ForEach-Object { $_.Trim() } |
  Group-Object |
  Sort-Object Count -Descending |
  Select-Object -First $Top |
  ForEach-Object {
    [PSCustomObject]@{
      Changes = $_.Count
      File    = $_.Name
    }
  } |
  Format-Table -AutoSize

