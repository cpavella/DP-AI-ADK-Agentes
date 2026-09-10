# Instala la CLI de Google Cloud (gcloud + bq) en Windows.
# Uso:  powershell -ExecutionPolicy Bypass -File install.ps1 [-Auth]
#   -Auth  Al terminar, lanza gcloud init y gcloud auth application-default login (abren el navegador).
param([switch]$Auth)

$ErrorActionPreference = "Stop"
function Log($m)  { Write-Host "`n==> $m" -ForegroundColor Cyan }
function Ok($m)   { Write-Host "OK  $m" -ForegroundColor Green }
function Warn($m) { Write-Host "!   $m" -ForegroundColor Yellow }

# --- Paso 0: ¿ya está instalado? -------------------------------------------
$gcloud = Get-Command gcloud -ErrorAction SilentlyContinue
if ($gcloud) {
    Ok "gcloud ya está instalado: $((gcloud --version 2>$null | Select-Object -First 1))"
} else {
    if (Get-Command winget -ErrorAction SilentlyContinue) {
        Log "Instalando con winget (Google.CloudSDK)"
        winget install --id Google.CloudSDK -e --accept-source-agreements --accept-package-agreements
    } else {
        Log "winget no disponible: descargando el instalador oficial"
        $installer = Join-Path $env:TEMP "GoogleCloudSDKInstaller.exe"
        (New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", $installer)
        Log "Sigue el asistente gráfico; deja marcada la opción de añadir gcloud al PATH"
        Start-Process -FilePath $installer -Wait
    }
    # Recargar PATH en esta sesión para poder verificar sin reabrir la terminal
    $env:Path = [Environment]::GetEnvironmentVariable("Path", "Machine") + ";" + [Environment]::GetEnvironmentVariable("Path", "User")
}

# --- Verificación ---------------------------------------------------------
Log "Verificando instalación"
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Warn "gcloud aún no está en el PATH de esta terminal. Cierra y abre PowerShell (y Claude Code) y vuelve a ejecutar: gcloud --version"
    exit 1
}
gcloud --version
if (Get-Command bq -ErrorAction SilentlyContinue) { Ok "bq disponible" } else { Warn "bq no disponible; prueba: gcloud components install bq" }

# --- Autenticación (opcional, interactiva) ---------------------------------
if ($Auth) {
    Log "gcloud init (se abrirá el navegador)"
    gcloud init
    Log "gcloud auth application-default login (se abrirá el navegador)"
    gcloud auth application-default login
    $project = (gcloud config get-value project 2>$null)
    if ($project) {
        gcloud auth application-default set-quota-project $project
        Log "Habilitando APIs de BigQuery y Vertex AI en $project"
        gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com --project=$project
    } else {
        Warn "No hay proyecto configurado. Ejecuta: gcloud config set project <PROJECT_ID>"
    }
}

Write-Host ""
Ok "Instalación terminada."
Write-Host @"
Siguientes pasos (interactivos, ejecútalos tú en la terminal o con '!' en Claude Code):
  1. gcloud init
  2. gcloud auth application-default login
  3. gcloud auth application-default set-quota-project (gcloud config get-value project)
  4. gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com
  5. gcloud auth application-default print-access-token   (debe imprimir un token)
  6. bq query --use_legacy_sql=false 'SELECT 1'
"@
