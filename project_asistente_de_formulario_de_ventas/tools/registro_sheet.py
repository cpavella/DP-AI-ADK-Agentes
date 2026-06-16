import pygsheets
import pandas as pd
import os
# Este ID es de "Interesados en Comprar un Curso"
SHEET_ID = "1O9r3PzPaPRWIEc1x4A_XJhejX1yBFvmzKlUguaaq9Hs" #**************************************************************************************************************
SHEET_NAME = "Interesados" #*********************************************************************************************************************************************
# --- CAMBIO CLAVE AQUÍ ---
# Le decimos a Python que busque el archivo un nivel ARRIBA (en la carpeta del proyecto)

#SERVICE_ACCOUNT_PATH = '../project-mlops-10-streamlit-42bec9881718.json'
#Vamos a obtener la Clave en formato JSON de una Cuenta de Servicio de mi GCP.
SERVICE_ACCOUNT_PATH = os.path.join(os.path.dirname(__file__), '..', 'datapath-taller-goo4-inofuente-060ca29529b8.json') #*****************************************************

def registrar_interes_en_sheet(nombre: str, apellido: str, email: str, curso: str) -> str:
    """
    Registra los datos de un nuevo usuario interesado en un curso en una hoja de cálculo de Google Sheets.
    Usa la lógica de `df.loc` para añadir la nueva fila.
    """
    try:
        url = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"
        
        # Intentamos leer el CSV. Si la hoja está vacía, puede dar un error, así que lo manejamos.
        try:
            df = pd.read_csv(url)
        except Exception:
            # Si falla (ej. hoja vacía), creamos un DataFrame con las columnas correctas
            df = pd.DataFrame(columns=['ID', 'Nombre Completo', 'Correo', 'Programa'])
        
        # --- USANDO TU LÓGICA SIMPLIFICADA ---
        # Combinamos nombre y apellido
        nombre_completo = f"{nombre} {apellido}"
        # Creamos el ID para la nueva fila
        nuevo_id = len(df) + 1
        
        # Añadimos la nueva fila usando df.loc, como en tu ejemplo
        df.loc[len(df.index)] = [nuevo_id, nombre_completo, email, curso]

        # Autorizamos y escribimos en la hoja
        gc = pygsheets.authorize(service_file=SERVICE_ACCOUNT_PATH)
        sh = gc.open_by_key(SHEET_ID)
        wks = sh.worksheet_by_title(SHEET_NAME)
        # Escribimos el DataFrame completo desde la celda A1
        wks.set_dataframe(df, start='A1', copy_index=False, fit=True)
        
        print(f"✅ Registro exitoso para {email} en el curso {curso}")
        return f"Registro exitoso para {email} en el curso {curso}"

    except FileNotFoundError:
        error_msg = f"Error: No se pudo encontrar el archivo de credenciales en la ruta '{SERVICE_ACCOUNT_PATH}'."
        print(f"❌ {error_msg}")
        return error_msg
    except Exception as e:
        error_msg = f"Error inesperado al registrar en Google Sheets: {e}"
        print(f"❌ {error_msg}")
        return error_msg



#--- Bloque de Prueba para Ejecución Directa ---
# if __name__ == '__main__':
#     print("--- Iniciando prueba de registro directo en Google Sheet (versión simplificada) ---")
    
#     # Datos de prueba que quieres insertar
#     nombre_prueba = "Jeanpier"
#     apellido_prueba = "Ancori"
#     email_prueba = "jean.anc@gmail.com"
#     curso_prueba = "Curso de DJango"
    
#     # Llamamos a la función directamente
#     resultado = registrar_interes_en_sheet(
#         nombre=nombre_prueba,
#         apellido=apellido_prueba,
#         email=email_prueba,
#         curso=curso_prueba
#     )
    
#     print("\n--- Resultado de la prueba ---")
#     print(resultado)
#     print("---------------------------------")
#     print("Por favor, verifica la hoja de cálculo en tu navegador para confirmar el registro.")

#python3  registro_sheet.py