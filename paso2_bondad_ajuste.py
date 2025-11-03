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

tabla_final.to_excel("bondad_ajuste_frisby.xlsx", index=False)
print("\n📊 Archivo 'bondad_ajuste_frisby.xlsx' generado con los resultados.")
