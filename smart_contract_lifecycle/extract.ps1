$h = Get-Content odoo19_dev_security.html -Raw
# Strip all HTML to plain text
$text = [regex]::Replace($h, '<script[^>]*>.*?</script>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<style[^>]*>.*?</style>', ' ', 'Singleline')
$text = [regex]::Replace($text, '<[^>]+>', ' ')
$text = [regex]::Replace($text, '&[a-z]+;', ' ')
$text = [regex]::Replace($text, '\s+', ' ')
# Look for "new" or "since 19" mentions
$sentences = [regex]::Split($text, '(?<=[\.\!\?])\s+')
foreach ($s in $sentences) {
    if ($s -match '(?i)(new in|deprecat|since 19|breaking|record ?rule|access ?rights|ir\.rule|ir\.model\.access|res\.groups|privilege|category)') {
        Write-Host "---"
        Write-Host $s
    }
}
