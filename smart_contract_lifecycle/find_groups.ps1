Get-Content res_users_19.py | Select-String -Pattern 'class\s+ResGroups|class\s+ResUsers|privilege|category_id|class\s+\w*Group\w*' | Select-Object -First 30
