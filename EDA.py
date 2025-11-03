# ===============================
# ANÁLISIS EXPLORATORIO DE DATOS (EDA)
# Proyecto: Teoría de Colas - Frisby
# ===============================

# Importar librerías
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import skew, kurtosis, probplot

# -------------------------------
# 1. Cargar el archivo Excel
# -------------------------------
# Asegúrate de que el archivo .xlsx esté en el mismo directorio del script
# o coloca la ruta completa (por ejemplo: "C:/Users/Jhoan/Documentos/datos_frisby.xlsx")

df = pd.read_excel("RecoleccionDatos.xlsx")  # Cambia el nombre si tu archivo se llama diferente

# Debe contener columnas llamadas: 'llegadas' y 'servicio'
print("Vista previa de los datos:")
print(df.head())

# -------------------------------
# 2. Estadísticas descriptivas
# -------------------------------
print("\n===== ESTADÍSTICAS DESCRIPTIVAS =====")

for col in ['llegadas', 'servicio']:
    print(f"\n>>> Variable: {col}")
    print(df[col].describe())
    print(f"Asimetría (skewness): {skew(df[col])}")
    print(f"Curtosis: {kurtosis(df[col])}")

# -------------------------------
# 3. Visualizaciones
# -------------------------------
sns.set(style="whitegrid")

# Histograma + KDE (Tiempos entre llegadas)
plt.figure(figsize=(8, 4))
sns.histplot(df['llegadas'], kde=True, color='skyblue')
plt.title("Histograma de Tiempos entre Llegadas (con KDE)")
plt.xlabel("Tiempo entre llegadas (minutos)")
plt.ylabel("Frecuencia")
plt.show()

# Histograma + KDE (Tiempos de servicio)
plt.figure(figsize=(8, 4))
sns.histplot(df['servicio'], kde=True, color='orange')
plt.title("Histograma de Tiempos de Servicio (con KDE)")
plt.xlabel("Tiempo de servicio (minutos)")
plt.ylabel("Frecuencia")
plt.show()

# Boxplot (detectar valores atípicos)
plt.figure(figsize=(6, 4))
sns.boxplot(data=df[['llegadas', 'servicio']])
plt.title("Boxplot: Tiempos entre Llegadas y de Servicio")
plt.show()

# QQ-Plot (comparación con distribución normal)
plt.figure(figsize=(6, 4))
probplot(df['llegadas'], dist="norm", plot=plt)
plt.title("QQ-Plot: Tiempos entre Llegadas")
plt.show()

plt.figure(figsize=(6, 4))
probplot(df['servicio'], dist="norm", plot=plt)
plt.title("QQ-Plot: Tiempos de Servicio")
plt.show()

# ------------------------------
# 5. Detección de posibles errores
# ------------------------------
errores = df[(df['llegadas'] <= 0) | (df['servicio'] <= 0)]
if not errores.empty:
    print("\n⚠️ Se detectaron posibles errores en los datos (valores negativos o nulos):")
    print(errores)
else:
    print("\n✅ No se detectaron valores negativos o atípicos graves en las columnas medidas.")

# Eliminamos filas con llegadas <= 0 (porque representan errores o duplicados)
df = df[df['llegadas'] > 0]

# ------------------------------
# 6. Exportar resumen estadístico
# ------------------------------
cols_numericas = ['llegadas', 'servicio']

resumen = df[cols_numericas].describe().T
resumen['skewness'] = [skew(df[c]) for c in cols_numericas]
resumen['kurtosis'] = [kurtosis(df[c]) for c in cols_numericas]
resumen.to_excel("resumen_estadistico_frisby.xlsx")

print("\n📂 Archivo 'resumen_estadistico_frisby.xlsx' generado exitosamente con las columnas numéricas.")
