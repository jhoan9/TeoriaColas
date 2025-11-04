# ===============================
# PASO 2: PRUEBAS DE BONDAD DE AJUSTE
# Proyecto: Teoría de Colas - Frisby
# ===============================

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import sys
from datetime import datetime

# -------------------------------
# 1. Cargar los datos
# -------------------------------
base_dir = Path(__file__).resolve().parent
excel_path = base_dir / "RecoleccionDatos.xlsx"

try:
    df = pd.read_excel(excel_path, engine="openpyxl")  # Usa el mismo archivo del paso 1
except FileNotFoundError:
    print(f"❌ No se encontró el archivo Excel en: {excel_path}")
    print("Asegúrate de que 'RecoleccionDatos.xlsx' esté en la misma carpeta que este script.")
    sys.exit(1)
except ImportError:
    print("❌ Falta la dependencia 'openpyxl' requerida para leer archivos .xlsx.")
    print("Instálala con: pip install openpyxl")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error al leer el archivo Excel: {e}")
    print("Intenta verificar que el archivo no esté dañado y que el formato sea .xlsx.")
    sys.exit(1)

# 2️⃣ Eliminar filas con valores no numéricos, NaN o infinitos
df = df.replace([np.inf, -np.inf], np.nan)
df = df.dropna(subset=['llegadas', 'servicio'])

# 3️⃣ Convertir a tipo numérico (por si hay texto)
df['llegadas'] = pd.to_numeric(df['llegadas'], errors='coerce')
df['servicio'] = pd.to_numeric(df['servicio'], errors='coerce')

# Mostrar conteo para verificar
print(f"Datos válidos: {len(df)} filas")

# -------------------------------
# 2. Función para probar distribuciones
# -------------------------------
def pruebas_bondad(variable, nombre):
    datos = df[variable].astype(float)
    resultados = []

    # Parámetros guardados para graficar luego
    params = {
        'Exponencial': None,
        'Normal': None,
        'Lognormal': None,
        'Gamma': None,
    }

    # --- Exponencial (MLE) ---
    try:
        exp_loc, exp_scale = stats.expon.fit(datos)
        ks_exp = stats.kstest(datos, 'expon', args=(exp_loc, exp_scale))
        ad_exp = stats.anderson(datos, dist='expon')
        resultados.append(['Exponencial', ks_exp.pvalue, ad_exp.statistic])
        params['Exponencial'] = (exp_loc, exp_scale)
    except Exception:
        resultados.append(['Exponencial', np.nan, np.nan])

    # --- Normal (MLE) ---
    try:
        norm_loc, norm_scale = stats.norm.fit(datos)
        ks_norm = stats.kstest(datos, 'norm', args=(norm_loc, norm_scale))
        ad_norm = stats.anderson(datos, dist='norm')
        resultados.append(['Normal', ks_norm.pvalue, ad_norm.statistic])
        params['Normal'] = (norm_loc, norm_scale)
    except Exception:
        resultados.append(['Normal', np.nan, np.nan])

    # --- Lognormal (solo datos positivos) ---
    datos_pos = datos[datos > 0]
    try:
        if len(datos_pos) >= 3:
            shape, loc_logn, scale_logn = stats.lognorm.fit(datos_pos, floc=0)
            ks_logn = stats.kstest(datos_pos, 'lognorm', args=(shape, loc_logn, scale_logn))
            ad_logn = stats.anderson(np.log(datos_pos), dist='norm')
            resultados.append(['Lognormal', ks_logn.pvalue, ad_logn.statistic])
            params['Lognormal'] = (shape, loc_logn, scale_logn)
        else:
            resultados.append(['Lognormal', np.nan, np.nan])
    except Exception:
        resultados.append(['Lognormal', np.nan, np.nan])

    # --- Gamma (solo datos positivos) ---
    try:
        if len(datos_pos) >= 3:
            a_g, loc_g, scale_g = stats.gamma.fit(datos_pos)
            ks_gamma = stats.kstest(datos_pos, 'gamma', args=(a_g, loc_g, scale_g))
            # Anderson-Darling para gamma no está directo; usamos expon como aproximación
            ad_gamma = stats.anderson(datos_pos, dist='expon')
            resultados.append(['Gamma', ks_gamma.pvalue, ad_gamma.statistic])
            params['Gamma'] = (a_g, loc_g, scale_g)
        else:
            resultados.append(['Gamma', np.nan, np.nan])
    except Exception:
        resultados.append(['Gamma', np.nan, np.nan])

    resumen = pd.DataFrame(resultados, columns=['Distribución', 'K-S (p)', 'A-D (stat)'])
    print(f"\n===== {nombre.upper()} =====")
    print(resumen)

    # Visualización del mejor ajuste
    # Selecciona el mayor p-value disponible
    if resumen['K-S (p)'].notna().any():
        mejor = resumen.loc[resumen['K-S (p)'].idxmax(), 'Distribución']
    else:
        mejor = None

    sns.histplot(datos, kde=True, stat="density", color='lightblue', label='Datos')
    x = np.linspace(float(np.nanmin(datos)), float(np.nanmax(datos)), 200)
    if mejor == 'Exponencial' and params['Exponencial'] is not None:
        loc, scale = params['Exponencial']
        plt.plot(x, stats.expon.pdf(x, loc, scale), 'r--', label='Exponencial')
    elif mejor == 'Normal' and params['Normal'] is not None:
        loc, scale = params['Normal']
        plt.plot(x, stats.norm.pdf(x, loc, scale), 'r--', label='Normal')
    elif mejor == 'Lognormal' and params['Lognormal'] is not None:
        shape, loc, scale = params['Lognormal']
        plt.plot(x, stats.lognorm.pdf(x, shape, loc, scale), 'r--', label='Lognormal')
    elif mejor == 'Gamma' and params['Gamma'] is not None:
        a, loc, scale = params['Gamma']
        plt.plot(x, stats.gamma.pdf(x, a, loc, scale), 'r--', label='Gamma')
    plt.title(f"Ajuste de distribuciones: {nombre}")
    plt.legend()
    plt.show()

    return resumen

# -------------------------------
# 3. Aplicar a ambas variables
# -------------------------------
tabla_llegadas = pruebas_bondad('llegadas', 'Tiempos entre llegadas')
tabla_servicio = pruebas_bondad('servicio', 'Tiempos de servicio')

# -------------------------------
# 4. Exportar tabla resumen
# -------------------------------
tabla_final = pd.concat([
    tabla_llegadas.assign(Tipo='Llegadas'),
    tabla_servicio.assign(Tipo='Servicio')
])

def guardar_excel_con_fallback(df_out: pd.DataFrame, nombre_base: str) -> str:
    try:
        df_out.to_excel(nombre_base, index=False)
        print(f"\nArchivo '{nombre_base}' generado con los resultados.")
        return nombre_base
    except PermissionError:
        # Si está abierto en Excel, escribir con sufijo de timestamp
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        nombre_alt = f"{Path(nombre_base).stem}_{ts}{Path(nombre_base).suffix}"
        df_out.to_excel(nombre_alt, index=False)
        print(f"\nNo se pudo escribir '{nombre_base}' (¿abierto en Excel?). Se guardó como '{nombre_alt}'.")
        return nombre_alt

guardar_excel_con_fallback(tabla_final, "bondad_ajuste_frisby.xlsx")

# -------------------------------
# 5. Exportar tabla resumen con evaluación
# -------------------------------

def evaluar_fila(row):
    # Decisión basada en p-value
    if row['K-S (p)'] > 0.05:
        decision = "✅ Se acepta"
    else:
        decision = "❌ Se descarta"
    return decision

def letra_notacion(distribucion):
    if distribucion == 'Exponencial':
        return 'M'
    elif distribucion in ['Gamma', 'Lognormal', 'Weibull']:
        return 'G'
    elif distribucion == 'Normal':
        return 'N'
    else:
        return 'D'

# Unimos ambas tablas
tabla_final = pd.concat([
    tabla_llegadas.assign(Tipo='Tiempos entre llegadas'),
    tabla_servicio.assign(Tipo='Tiempos de servicio')
])

# Asignar evaluación visual automática según p-value
def eval_visual(p):
    if p >= 0.9:
        return "Excelente"
    elif p >= 0.5:
        return "Bueno"
    elif p >= 0.2:
        return "Aceptable"
    elif p >= 0.05:
        return "Regular"
    else:
        return "Malo"

tabla_final['Evaluación Visual'] = tabla_final['K-S (p)'].apply(eval_visual)

# Agregar decisión final y letra notación
tabla_final['Decisión Final'] = tabla_final.apply(evaluar_fila, axis=1)
tabla_final['Letra Notación'] = tabla_final['Distribución'].apply(letra_notacion)

# Reordenar columnas
tabla_final = tabla_final[['Tipo', 'Distribución', 'K-S (p)', 'A-D (stat)',
                           'Evaluación Visual', 'Decisión Final', 'Letra Notación']]

# Guardar resultado
guardar_excel_con_fallback(tabla_final, "bondad_ajuste_frisby.xlsx")
