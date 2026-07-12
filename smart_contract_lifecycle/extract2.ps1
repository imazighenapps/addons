$h = Get-Content odoo19_releasenotes.html -Raw
$text = [regex]::Replace($h, '<script[^>]*>.*?</script>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<style[^>]*>.*?</style>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<[^>]+>', ' ')
$text = [regex]::Replace($text, '&[a-z#0-9]+;', ' ')
$text = [regex]::Replace($text, '\s+', ' ')
$sentences = [regex]::Split($text, '(?<=[\.\!\?])\s+')
foreach ($s in $sentences) {
    if ($s -match '(?i)(security|access right|record rule|ir\.rule|ir\.model\.access|res\.groups|privilege|user ?rights|permission|groups?)') {
        Write-Host "---"
        Write-Host $s.Substring(0, [Math]::Min(400, $s.Length))
    }
}
