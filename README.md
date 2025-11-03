# 🧠 Proyecto: Teoría de Colas - Frisby (Análisis EDA con Python)

Este proyecto realiza un **análisis exploratorio de datos (EDA)** sobre los tiempos de llegada y servicio de clientes observados en el punto de venta **Frisby C.C. Campanario**.  
El propósito es aplicar los conceptos de la **Teoría de Colas** (λ, μ, Wq, Ws, Lq, Ls) mediante el uso de Python, generando gráficos, métricas estadísticas y detección de patrones de atención.

---

## 🧩 1. Requisitos previos

Antes de comenzar, asegúrate de tener instalado en tu sistema:

- [Python 3.10 o superior](https://www.python.org/downloads/)
- [Visual Studio Code (VS Code)](https://code.visualstudio.com/) o cualquier editor de texto.
- Archivo de datos en Excel: `datos_frisby.xlsx` con al menos las siguientes columnas:

| llegadas | servicio |
|-----------|-----------|
| 1.3 | 2.5 |
| 1.1 | 2.9 |
| 0.8 | 2.1 |
| 1.5 | 3.0 |
| ... | ... |

---

## ⚙️ 2. Crear y activar el entorno virtual (.venv)

### 📁 Paso 1. Crear el entorno virtual

Abre una **terminal de Windows (CMD o PowerShell)** dentro de la carpeta del proyecto y ejecuta:

```bash
python -m venv .venv

### 📁 Paso 2. Activar el entorno virtual

```bash
.venv\Scripts\activate


Si la activación fue correcta, verás algo así en la terminal:
(.venv) C:\Users\Jhoan\Proyecto_Teoria_Colas>

### 📁 Paso 3. Instalar dependencias necesarias

Crea un archivo llamado requirements.txt y agrega el siguiente contenido:

```bash
pandas==2.2.3
matplotlib==3.9.2
seaborn==0.13.2
scipy==1.14.1
openpyxl==3.1.5

Luego, con el entorno virtual activado, instala las librerías:

```bash
pip install -r requirements.txt
