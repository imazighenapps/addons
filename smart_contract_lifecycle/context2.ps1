$h = Get-Content odoo19_releasenotes.html -Raw
# Find context around "Product access rights"
$idx = $h.IndexOf('Product access rights')
if ($idx -lt 0) { Write-Host "Not found"; exit }
$start = [Math]::Max(0, $idx - 100)
$len = [Math]::Min($h.Length - $start, 3000)
$snippet = $h.Substring($start, $len)
$text = [regex]::Replace($snippet, '<script[^>]*>.*?</script>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<style[^>]*>.*?</style>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<[^>]+>', ' ')
$text = [regex]::Replace($text, '&[a-z#0-9]+;', ' ')
$text = [regex]::Replace($text, '\s+', ' ')
Write-Host $text
