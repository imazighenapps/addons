$h = Get-Content odoo19_releasenotes.html -Raw
# Get much wider context around "Product access rights"
$idx = $h.IndexOf('Product access rights')
if ($idx -lt 0) { Write-Host "Not found"; exit }
$start = [Math]::Max(0, $idx - 5000)
$len = [Math]::Min($h.Length - $start, 8000)
$snippet = $h.Substring($start, $len)
# Extract just text in this region
$text = [regex]::Replace($snippet, '<script[^>]*>.*?</script>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<style[^>]*>.*?</style>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<[^>]+>', ' ')
$text = [regex]::Replace($text, '&[a-z#0-9]+;', ' ')
$text = [regex]::Replace($text, '\s+', ' ')
# Find the position of "Product access rights" in this text
$pos = $text.IndexOf('Product access rights')
$before = $text.Substring([Math]::Max(0, $pos - 2000), [Math]::Min(2000, $pos))
$after = $text.Substring($pos, [Math]::Min(2000, $text.Length - $pos))
Write-Host "=== AFTER ==="
Write-Host $after
Write-Host "=== BEFORE ==="
Write-Host $before
