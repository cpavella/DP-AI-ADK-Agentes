---
name: gcloud-cli-install
description: Instala la CLI de Google Cloud (gcloud + bq) en macOS, Linux o Windows, la autentica con la cuenta de Google del alumno (gcloud init + Application Default Credentials), fija el proyecto de cuota y habilita las APIs de BigQuery y Vertex AI que necesitan los agentes ADK de este repo. Incluye scripts automáticos, verificación end-to-end y solución de problemas. Use when the user asks to "instalar gcloud", "instalar la CLI de Google Cloud", "configurar Google Cloud", "no me reconoce gcloud", "command not found gcloud", "default credentials were not found", "autenticarme con BigQuery", "gcloud auth application-default login", or types /gcloud-cli-install.
---

# Instalar y configurar la CLI de Google Cloud (gcloud)

Objetivo: que el alumno tenga `gcloud` y `bq` funcionando en su máquina, autenticado con su cuenta de Google, con las **Application Default Credentials (ADC)** creadas y las APIs habilitadas. Eso es lo que necesitan los agentes ADK de este repo para conectarse a BigQuery y a Vertex AI.

Esta skill es paso a paso. Ejecuta cada paso, comprueba la salida y no avances hasta que el anterior funcione. Habla al alumno en español.

## Regla importante: comandos interactivos

`gcloud init`, `gcloud auth login` y `gcloud auth application-default login` abren el navegador y esperan a que el alumno inicie sesión. **No los ejecutes tú desde la tool Bash**: se quedan colgados. Pídele al alumno que los escriba él en el prompt de Claude Code con el prefijo `!`, por ejemplo:

```
! gcloud auth application-default login
```

Así el comando corre en su terminal y la salida vuelve a la conversación.

## Paso 0: ¿Ya está instalado?

```bash
gcloud --version 2>/dev/null && echo "OK: gcloud instalado" || echo "FALTA: gcloud no está en el PATH"
```

Si ya está instalado, salta directamente al **Paso 2 (autenticación)**. Si aparece `command not found` pero el alumno dice que lo instaló, revisa primero la sección *Solución de problemas* (casi siempre es el PATH).

## Paso 1: Instalar

Detecta el sistema operativo (`uname -s` en macOS/Linux; en Windows el alumno lo sabrá) y usa **una** de estas vías. La forma más rápida es el script de esta skill:

- macOS / Linux: `bash .claude/skills/gcloud-cli-install/scripts/install.sh`
- Windows (PowerShell): `powershell -ExecutionPolicy Bypass -File .claude\skills\gcloud-cli-install\scripts\install.ps1`

El script detecta el sistema, instala con el gestor de paquetes si existe (Homebrew, apt, winget) y si no, con el instalador oficial de Google. Es idempotente: si `gcloud` ya existe, solo muestra la versión.

Si prefieres hacerlo a mano:

### macOS

Con Homebrew (recomendado):
```bash
brew install --cask google-cloud-sdk
```

Sin Homebrew (instalador oficial, se instala en `~/google-cloud-sdk`):
```bash
ARCH=$([ "$(uname -m)" = "arm64" ] && echo arm || echo x86_64)
curl -fsSL -o /tmp/gcloud.tar.gz "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-darwin-${ARCH}.tar.gz"
tar -xzf /tmp/gcloud.tar.gz -C "$HOME"
"$HOME/google-cloud-sdk/install.sh" --quiet --path-update true --command-completion true
exec -l $SHELL   # recarga la terminal para que el PATH tome efecto
```

### Linux

Debian / Ubuntu (misma receta que el `Dockerfile.dev` del repo):
```bash
sudo apt-get update && sudo apt-get install -y apt-transport-https ca-certificates gnupg curl
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list
sudo apt-get update && sudo apt-get install -y google-cloud-cli
```

Otras distribuciones (instalador oficial):
```bash
ARCH=$([ "$(uname -m)" = "aarch64" ] && echo arm || echo x86_64)
curl -fsSL -o /tmp/gcloud.tar.gz "https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-cli-linux-${ARCH}.tar.gz"
tar -xzf /tmp/gcloud.tar.gz -C "$HOME"
"$HOME/google-cloud-sdk/install.sh" --quiet --path-update true --command-completion true
exec -l $SHELL
```

### Windows

Con winget (PowerShell):
```powershell
winget install --id Google.CloudSDK -e
```

Sin winget: descargar y ejecutar el instalador oficial:
```powershell
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/GoogleCloudSDKInstaller.exe", "$env:Temp\GoogleCloudSDKInstaller.exe")
& "$env:Temp\GoogleCloudSDKInstaller.exe"
```

En Windows hay que **cerrar y abrir de nuevo la terminal** (y Claude Code) después de instalar para que `gcloud` aparezca en el PATH.

### Comprobar la instalación

```bash
gcloud --version
```

Debe listar `Google Cloud SDK <versión>` y `bq <versión>`. Si `bq` no aparece: `gcloud components install bq` (solo con el instalador oficial; con apt/brew ya viene incluido).

## Paso 2: Autenticar la CLI y elegir el proyecto

El alumno ejecuta (con `!`):

```
! gcloud init
```

Le pedirá iniciar sesión en el navegador con su cuenta de Google del curso y elegir el proyecto de GCP. Si ya tiene una configuración anterior, que elija *Create a new configuration* o *Re-initialize*. Al terminar, comprueba:

```bash
gcloud auth list
gcloud config list
```

`gcloud config list` debe mostrar `account = <su-correo>` y `project = <id-del-proyecto>`. Si el proyecto no quedó fijado:

```bash
gcloud projects list --format="table(projectId,name)"
gcloud config set project <PROJECT_ID>
```

## Paso 3: Crear las Application Default Credentials (ADC)

Este es el paso que los agentes de Python realmente usan. La librería `google-cloud-bigquery` y el ADK leen las credenciales de este archivo, **no** de la sesión de `gcloud init`. El alumno ejecuta:

```
! gcloud auth application-default login
```

Vuelve a abrir el navegador. Al terminar debe existir el archivo:

- macOS / Linux: `~/.config/gcloud/application_default_credentials.json`
- Windows: `%APPDATA%\gcloud\application_default_credentials.json`

Después fija el proyecto de cuota (evita el aviso *quota project* y errores 403 al consultar datasets públicos):

```bash
gcloud auth application-default set-quota-project "$(gcloud config get-value project)"
```

## Paso 4: Habilitar las APIs del curso

```bash
PROJECT_ID="$(gcloud config get-value project)"
gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com --project="$PROJECT_ID"
gcloud services list --enabled --project="$PROJECT_ID" --filter="name:(bigquery OR aiplatform)" --format="value(config.name)"
```

Deben aparecer `bigquery.googleapis.com` y `aiplatform.googleapis.com`. Si falla con *billing account*, el proyecto necesita facturación activa en https://console.cloud.google.com/billing.

## Paso 5: Verificar end-to-end

Ejecuta el script de verificación (macOS/Linux):

```bash
bash .claude/skills/gcloud-cli-install/scripts/verify.sh
```

O a mano:

```bash
gcloud auth application-default print-access-token >/dev/null && echo "ADC OK"
bq query --use_legacy_sql=false --format=pretty 'SELECT COUNT(*) AS estaciones FROM `bigquery-public-data.new_york_citibike.citibike_stations`'
```

La consulta debe devolver un número (unos cientos o miles de estaciones). Con eso el alumno ya puede levantar el agente con `adk web`.

## Paso 6: Variables del proyecto (.env)

Cada carpeta de agente (por ejemplo `project_agent_text_to_sql_bigquery/`) lleva un `.env` con estas variables. Comprueba que existan; **no imprimas sus valores en la conversación**:

```
GOOGLE_CLOUD_PROJECT=<id-del-proyecto>
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_GENAI_USE_VERTEXAI=TRUE
```

Y recuerda al alumno que en `tools/run_sql_query.py` la constante `TU_PROYECTO_GCP_ID` debe apuntar a **su** proyecto, no al del profesor.

## Solución de problemas

| Síntoma | Causa | Solución |
|---|---|---|
| `command not found: gcloud` justo después de instalar | La terminal no recargó el PATH | Cerrar y abrir la terminal (y Claude Code). Con el instalador oficial en zsh: añadir `source ~/google-cloud-sdk/path.zsh.inc` a `~/.zshrc` |
| `Your default credentials were not found` / `DefaultCredentialsError` | Falta el paso 3 | `! gcloud auth application-default login` |
| Aviso `quota project` o 403 `Permission denied` al consultar `bigquery-public-data` | ADC sin proyecto de cuota | `gcloud auth application-default set-quota-project <PROJECT_ID>` |
| `Reauthentication required` / `invalid_grant` | Token caducado o cuenta cambiada | Repetir pasos 2 y 3 |
| 403 `API has not been used in project ... or it is disabled` | API sin habilitar | Paso 4 |
| `The project ... does not have billing enabled` | Proyecto sin facturación | Activar facturación en la consola de GCP |
| La librería usa un proyecto o una cuenta distinta a la de `gcloud` | `GOOGLE_APPLICATION_CREDENTIALS` apunta a un JSON de cuenta de servicio | Decidir: o se quita la variable para usar ADC, o se usa el JSON. No mezclar |
| `gcloud components update` dice que no está permitido | Instalado con apt o Homebrew | Actualizar con `sudo apt-get upgrade google-cloud-cli` o `brew upgrade --cask google-cloud-sdk` |
| Windows: `gcloud` funciona en CMD pero no en PowerShell | Política de ejecución bloquea `gcloud.ps1` | Usar `gcloud.cmd` o `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `bq` pide `Python not found` | Instalador oficial sin Python | Reinstalar con `install.sh --install-python true` o instalar Python 3.9+ |
| Red corporativa / proxy | gcloud no sale a internet | `gcloud config set proxy/type http`, `proxy/address` y `proxy/port` según el proxy de la red |

## Desinstalar

- Homebrew: `brew uninstall --cask google-cloud-sdk`
- apt: `sudo apt-get remove google-cloud-cli`
- Instalador oficial: `rm -rf ~/google-cloud-sdk` y quitar las líneas `source .../path.*.inc` del `~/.zshrc` o `~/.bashrc`
- Windows: *Agregar o quitar programas* → Google Cloud SDK
- Credenciales locales (en todos los casos): `rm -rf ~/.config/gcloud`

## Referencias

- Instalación oficial: https://cloud.google.com/sdk/docs/install
- Application Default Credentials: https://cloud.google.com/docs/authentication/provide-credentials-adc
- `gcloud init`: https://cloud.google.com/sdk/gcloud/reference/init
- Google ADK: https://google.github.io/adk-docs/
