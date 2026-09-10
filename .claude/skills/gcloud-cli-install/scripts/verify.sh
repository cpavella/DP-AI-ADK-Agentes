#!/usr/bin/env bash
# Verifica que gcloud, las credenciales ADC y el acceso a BigQuery funcionan.
# Uso: bash verify.sh
set -uo pipefail

ok()   { printf '\033[1;32m✔ %s\033[0m\n' "$*"; }
fail() { printf '\033[1;31m✘ %s\033[0m\n' "$*"; FAILS=$((FAILS+1)); }
FAILS=0

echo "== 1. Binarios"
if command -v gcloud >/dev/null 2>&1; then ok "gcloud: $(gcloud --version 2>/dev/null | head -1)"; else fail "gcloud no está en el PATH (instala con scripts/install.sh)"; exit 1; fi
if command -v bq >/dev/null 2>&1; then ok "bq disponible"; else fail "bq no disponible: gcloud components install bq"; fi

echo; echo "== 2. Cuenta y proyecto de gcloud"
ACCOUNT="$(gcloud config get-value account 2>/dev/null)"
PROJECT="$(gcloud config get-value project 2>/dev/null)"
[ -n "$ACCOUNT" ] && ok "cuenta: $ACCOUNT" || fail "sin cuenta: ejecuta 'gcloud init' o 'gcloud auth login'"
[ -n "$PROJECT" ] && ok "proyecto: $PROJECT" || fail "sin proyecto: gcloud config set project <PROJECT_ID>"

echo; echo "== 3. Application Default Credentials (lo que usa Python / ADK)"
if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
  echo "  GOOGLE_APPLICATION_CREDENTIALS está definida (cuenta de servicio). Se usará ese JSON en lugar del login de usuario."
  [ -f "$GOOGLE_APPLICATION_CREDENTIALS" ] && ok "el archivo existe" || fail "el archivo indicado no existe"
fi
ADC="${CLOUDSDK_CONFIG:-$HOME/.config/gcloud}/application_default_credentials.json"
[ -f "$ADC" ] && ok "archivo ADC presente" || fail "falta $ADC: ejecuta 'gcloud auth application-default login'"
if gcloud auth application-default print-access-token >/dev/null 2>&1; then ok "token ADC válido"; else fail "no se pudo obtener token ADC (repite 'gcloud auth application-default login')"; fi
if [ -f "$ADC" ] && command -v python3 >/dev/null 2>&1; then
  QP="$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1])).get("quota_project_id",""))' "$ADC" 2>/dev/null)"
  [ -n "$QP" ] && ok "quota project: $QP" || fail "ADC sin quota project: gcloud auth application-default set-quota-project $PROJECT"
fi

if [ -n "$PROJECT" ]; then
  echo; echo "== 4. APIs habilitadas en $PROJECT"
  if ENABLED="$(gcloud services list --enabled --project="$PROJECT" --format='value(config.name)' 2>&1)"; then
    for api in bigquery.googleapis.com aiplatform.googleapis.com; do
      echo "$ENABLED" | grep -qx "$api" && ok "$api" || fail "$api no habilitada: gcloud services enable $api --project=$PROJECT"
    done
  else
    fail "no se pudo consultar las APIs (sesión de gcloud caducada o sin permisos). Ejecuta 'gcloud auth login' y repite:"
    echo "$ENABLED" | head -5 | sed 's/^/    /'
  fi

  echo; echo "== 5. Consulta de prueba a BigQuery (dataset público CitiBike)"
  if command -v bq >/dev/null 2>&1; then
    if OUT="$(bq --project_id="$PROJECT" query --use_legacy_sql=false --format=csv 'SELECT COUNT(*) AS estaciones FROM `bigquery-public-data.new_york_citibike.citibike_stations`' 2>&1)"; then
      ok "BigQuery responde: $(echo "$OUT" | tail -1) estaciones"
    else
      fail "la consulta falló:"; echo "$OUT" | sed 's/^/    /'
    fi
  fi
fi

echo
if [ "$FAILS" -eq 0 ]; then ok "Todo listo. Ya puedes ejecutar 'adk web'."; else printf '\033[1;31m%s comprobaciones fallaron. Revisa los mensajes de arriba.\033[0m\n' "$FAILS"; exit 1; fi
