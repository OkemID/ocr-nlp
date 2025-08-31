param()
$ErrorActionPreference = "Stop"

Write-Host "[*] Checking Docker..."
docker --version | Out-Null

Write-Host "[*] Building containers..."
docker compose up --build -d

Write-Host "[*] Installing mobile deps..."
Push-Location apps/mobile
npm i
Pop-Location

Write-Host "Done. Node API: http://localhost:4000  OCR: http://localhost:8000"
Write-Host "Set EXPO_PUBLIC_NODE_API_BASE in apps/mobile/.env"
