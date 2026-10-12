
$ErrorActionPreference = "Continue"

New-Item -ItemType Directory -Force -Path ".\screenshots" | Out-Null

"=== DATE ===" | Out-File ".\screenshots\ollama_reality_check.txt" -Encoding utf8

Get-Date -Format "yyyy-MM-dd HH:mm:ss" |
    Out-File ".\screenshots\ollama_reality_check.txt" -Append -Encoding utf8

"`n=== OLLAMA LIST ===" |
    Out-File ".\screenshots\ollama_reality_check.txt" -Append -Encoding utf8

ollama list 2>&1 |
    Out-File ".\screenshots\ollama_reality_check.txt" -Append -Encoding utf8

"`n=== OLLAMA PS ===" |
    Out-File ".\screenshots\ollama_reality_check.txt" -Append -Encoding utf8

ollama ps 2>&1 |
    Out-File ".\screenshots\ollama_reality_check.txt" -Append -Encoding utf8

Write-Host "Saved output to screenshots\ollama_reality_check.txt"
