#!/usr/bin/env bash
# Instala la CLI de Google Cloud (gcloud + bq) en macOS o Linux.
# Uso:  bash install.sh [--auth]
#   --auth  Al terminar, lanza gcloud init y gcloud auth application-default login
#           (interactivos: abren el navegador). Sin la bandera solo instala.
set -euo pipefail

BASE_URL="https://dl.google.com/dl/cloudsdk/channels/rapid/downloads"
SDK_DIR="$HOME/google-cloud-sdk"
DO_AUTH=false
[ "${1:-}" = "--auth" ] && DO_AUTH=true

log()  { printf '\n\033[1;34m==> %s\033[0m\n' "$*"; }
ok()   { printf '\033[1;32m✔ %s\033[0m\n' "$*"; }
warn() { printf '\033[1;33m! %s\033[0m\n' "$*"; }
die()  { printf '\033[1;31m✘ %s\033[0m\n' "$*" >&2; exit 1; }

# --- Paso 0: ¿ya está instalado? -------------------------------------------
if command -v gcloud >/dev/null 2>&1; then
  ok "gcloud ya está instalado: $(gcloud --version 2>/dev/null | head -1)"
  INSTALLED=true
else
  INSTALLED=false
fi

OS="$(uname -s)"
ARCH_RAW="$(uname -m)"

install_tarball() {
  local platform="$1" arch="$2"
  local url="${BASE_URL}/google-cloud-cli-${platform}-${arch}.tar.gz"
  local tmp; tmp="$(mktemp -d)"
  log "Descargando instalador oficial: $url"
  curl -fsSL -o "$tmp/gcloud.tar.gz" "$url" || die "No se pudo descargar $url"
  [ -d "$SDK_DIR" ] && { warn "Ya existe $SDK_DIR, se reutiliza"; } || tar -xzf "$tmp/gcloud.tar.gz" -C "$HOME"
  log "Ejecutando install.sh (añade gcloud al PATH del shell)"
  "$SDK_DIR/install.sh" --quiet --path-update true --command-completion true --install-python false
  export PATH="$SDK_DIR/bin:$PATH"
  rm -rf "$tmp"
}

if [ "$INSTALLED" = false ]; then
  case "$OS" in
    Darwin)
      if command -v brew >/dev/null 2>&1; then
        log "macOS con Homebrew: brew install --cask google-cloud-sdk"
        brew install --cask google-cloud-sdk
      else
        ARCH=$([ "$ARCH_RAW" = "arm64" ] && echo arm || echo x86_64)
        install_tarball darwin "$ARCH"
      fi
      ;;
    Linux)
      if command -v apt-get >/dev/null 2>&1; then
        log "Linux con apt: repositorio oficial cloud-sdk"
        SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
        $SUDO apt-get update
        $SUDO apt-get install -y apt-transport-https ca-certificates gnupg curl
        curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | $SUDO gpg --dearmor --yes -o /usr/share/keyrings/cloud.google.gpg
        echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | $SUDO tee /etc/apt/sources.list.d/google-cloud-sdk.list >/dev/null
        $SUDO apt-get update
        $SUDO apt-get install -y google-cloud-cli
      else
        ARCH=$([ "$ARCH_RAW" = "aarch64" ] && echo arm || echo x86_64)
        install_tarball linux "$ARCH"
      fi
      ;;
    *)
      die "Sistema no soportado por este script: $OS. En Windows usa scripts/install.ps1"
      ;;
  esac
fi

# --- Verificación de la instalación ----------------------------------------
log "Verificando instalación"
if ! command -v gcloud >/dev/null 2>&1; then
  if [ -x "$SDK_DIR/bin/gcloud" ]; then
    export PATH="$SDK_DIR/bin:$PATH"
    warn "gcloud instalado en $SDK_DIR pero aún no está en el PATH de esta terminal."
    warn "Cierra y abre la terminal, o ejecuta:  source $SDK_DIR/path.$(basename "${SHELL:-bash}").inc"
  else
    die "gcloud no aparece en el PATH tras la instalación. Revisa la salida anterior."
  fi
fi
gcloud --version
command -v bq >/dev/null 2>&1 && ok "bq disponible" || warn "bq no está disponible; prueba: gcloud components install bq"

# --- Autenticación (opcional, interactiva) ---------------------------------
if [ "$DO_AUTH" = true ]; then
  log "gcloud init (se abrirá el navegador)"
  gcloud init
  log "gcloud auth application-default login (se abrirá el navegador)"
  gcloud auth application-default login
  PROJECT_ID="$(gcloud config get-value project 2>/dev/null || true)"
  if [ -n "$PROJECT_ID" ]; then
    gcloud auth application-default set-quota-project "$PROJECT_ID"
    log "Habilitando APIs de BigQuery y Vertex AI en $PROJECT_ID"
    gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com --project="$PROJECT_ID"
  else
    warn "No hay proyecto configurado. Ejecuta: gcloud config set project <PROJECT_ID>"
  fi
fi

cat <<MSG

$(ok "Instalación terminada.")
Siguientes pasos (interactivos, ejecútalos tú en la terminal o con '!' en Claude Code):
  1. gcloud init
  2. gcloud auth application-default login
  3. gcloud auth application-default set-quota-project "\$(gcloud config get-value project)"
  4. gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com
  5. bash .claude/skills/gcloud-cli-install/scripts/verify.sh
MSG
