param([string]$Url, [string]$Target)
$ErrorActionPreference = 'Stop'
# Usa la validación TLS y el almacén de certificados del sistema; no omite errores.
Invoke-WebRequest -Uri $Url -OutFile $Target -UseBasicParsing -TimeoutSec 45
