$h = Get-Content odoo19_dev_security.html -Raw
$patterns = @('res\.groups[^\"<>]*', 'ir\.model\.access[^\"<>]*', 'privilege[^\"<>]*', 'category_id[^\"<>]*', 'res\.groups\.category[^\"<>]*', 'ir\.module\.category[^\"<>]*')
foreach ($p in $patterns) {
    Write-Host "=== Pattern: $p ==="
    [regex]::Matches($h, $p) | ForEach-Object { Write-Host $_.Value }
}
