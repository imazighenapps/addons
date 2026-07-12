$h = Get-Content odoo19_dev_security.html -Raw
# Get context around res.groups.category_id
$idx = 0
while (($idx = $h.IndexOf('res.groups.category_id', $idx)) -ge 0) {
    $start = [Math]::Max(0, $idx - 200)
    $len = [Math]::Min($h.Length - $start, 800)
    $snippet = $h.Substring($start, $len)
    # strip HTML tags
    $text = [regex]::Replace($snippet, '<[^>]+>', ' ')
    $text = [regex]::Replace($text, '\s+', ' ')
    Write-Host "---"
    Write-Host $text
    $idx += 20
}
