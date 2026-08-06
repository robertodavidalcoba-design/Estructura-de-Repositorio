# Proyecto Data Analysis en Google Colab

## Descripción
Este repositorio contiene una estructura reproducible pensada para ejecutarse directamente en Google Colab o entornos de Jupyter.

## Estructura del Repositorio
```text
project-root/
│
├── README.md           # Documentación del proyecto
├── requirements.txt    # Librerías necesarias
├── notebooks/          # Notebooks ordenados por etapa
├── scripts/            # Módulos Python reutilizables (utils.py)
├── data/               # Datasets de entrada
└── outputs/            # Gráficos y reportes generados

```

## 1. Instalación

### 1.1 En Google Colab (recomendado)

No requiere instalación local. Simplemente:

1. Abrí el notebook principal en Colab.
2. Ejecutá la celda de montaje de Google Drive (primera celda del proyecto).
   Esto crea automáticamente la estructura de carpetas dentro de
   `MyDrive/DataII/` si no existe.
3. Ejecutá la celda `%%writefile ../scripts/utils.py` para generar el módulo
   de funciones auxiliares.
4. Instalá las dependencias adicionales que no vienen preinstaladas en Colab:

```python
   !pip install -r requirements.txt
```

### 1.2 En un entorno local (Jupyter)


```bash
git clone https://github.com/<usuario>/<repo>.git
cd <repo>
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install -r requirements.txt
jupyter notebook
```

### 1.3 Credenciales

Este proyecto puede requerir un token personal de GitHub para hacer push
desde Colab. **Nunca lo pegues en texto plano en una celda.** Usá una de
estas dos opciones:

**Opción A — Colab Secrets (recomendada):**
```python
from google.colab import userdata
TOKEN = userdata.get('GH_TOKEN')
```

**Opción B — entrada oculta:**

```python
import getpass
TOKEN = getpass.getpass("Pega tu token de GitHub: ")
```

Si en algún momento un token quedó expuesto en un notebook, un commit o un
mensaje: **revocalo de inmediato** en GitHub (Settings → Developer settings
→ Personal access tokens) y generá uno nuevo. Revisá también el output
guardado de las celdas del `.ipynb`, porque `print()` o el eco de `input()`
puede haber quedado guardado ahí.

## 2. Extracción de datos

Los datos crudos van en `data/`. Si vienen de una fuente externa (API, base
de datos, archivo compartido), documentá acá el origen y el método de
descarga. Ejemplo genérico:

```python
from scripts.utils import cargar_datos

df_raw = cargar_datos("data/dataset_original.csv")
```

Si la fuente es una base de datos, preferí `sqlite3` o `sqlalchemy` en vez
de credenciales embebidas; guardá la cadena de conexión como secreto (ver
sección de Credenciales) y nunca la subas al repo.

## 3. Limpieza de datos

Convención sugerida: cada paso de limpieza es una función pura en
`scripts/utils.py` que recibe un DataFrame y devuelve uno nuevo, para poder
encadenarlas y testearlas por separado.

```python
def limpiar_nulos(df: pd.DataFrame) -> pd.DataFrame:
    """Elimina filas con valores nulos en columnas clave."""
    return df.dropna(subset=["columna_clave"])

def normalizar_columnas(df: pd.DataFrame) -> pd.DataFrame:
    """Estandariza nombres de columnas a snake_case."""
    df.columns = (
        df.columns.str.strip().str.lower().str.replace(" ", "_")
    )
    return df
```
Ejemplo de uso encadenado en el notebook:

```python
df = (
    df_raw
    .pipe(limpiar_nulos)
    .pipe(normalizar_columnas)
)
```

## 4. Almacenamiento
- **Datos intermedios/procesados**: guardalos en `data/processed/` (creá la
  subcarpeta si no existe) en formato `.parquet` para mejor rendimiento y
  tipado, o `.csv` si necesitás portabilidad total.

```python
  df.to_parquet("data/processed/dataset_limpio.parquet", index=False)
```

- **Resultados finales / gráficos**: usá `outputs/`, con la función
  `guardar_grafico()` de `utils.py`.

- Recordá que `data/` y `outputs/` están en `.gitignore`: si necesitás
  versionar un dataset liviano específico, agregá una excepción puntual
  (`!data/mi_dataset_pequeno.csv`) en lugar de sacar la regla general.

## 5. Ejecución de notebooks

Orden sugerido dentro de `notebooks/`:

1. `01_extraccion.ipynb` — carga y validación inicial de datos crudos.
2. `02_limpieza.ipynb` — aplica las funciones de `utils.py`, guarda el
   dataset procesado.
3. `03_analisis.ipynb` — exploración, consultas SQL, estadística descriptiva.
4. `04_visualizacion.ipynb` — gráficos finales, exportados a `outputs/`.

Cada notebook debe poder ejecutarse de punta a punta con
**Runtime → Run all** sin errores, partiendo del dataset procesado del paso
anterior (no de estado en memoria de otra sesión).

## 6. Outputs esperados

| Archivo | Ubicación | Descripción |
|---|---|---|
| `dataset_limpio.parquet` | `data/processed/` | Dataset tras limpieza, listo para análisis |
| `resumen_estadistico.csv` | `outputs/` | Estadísticas descriptivas por columna |
| `grafico_distribucion.png` | `outputs/` | Distribución de la variable principal |
| `reporte_final.md` o `.pdf` | `outputs/` | Resumen de hallazgos (opcional) |

## 7. Ejemplos de consultas SQL sobre los DataFrames

Podés consultar tus DataFrames con SQL directamente usando `sqlite3` en
memoria (sin dependencias extra) o `pandasql`/`duckdb` si preferís sintaxis
más directa.

**Con `sqlite3` (sin instalar nada extra):**

```python
import sqlite3

conn = sqlite3.connect(":memory:")
df.to_sql("datos", conn, index=False, if_exists="replace")

query = """
SELECT columna_categoria, COUNT(*) AS total, AVG(columna_numerica) AS promedio
FROM datos
GROUP BY columna_categoria
ORDER BY total DESC;
"""
resultado = pd.read_sql_query(query, conn)
resultado
```
**Con `duckdb` (recomendado para datasets grandes, más rápido):**

```python
# !pip install duckdb --quiet
import duckdb

resultado = duckdb.query("""
    SELECT columna_categoria, COUNT(*) AS total
    FROM df
    WHERE columna_numerica > 100
    GROUP BY columna_categoria
""").to_df()
```
## 8. Convenciones de commits

Usá mensajes descriptivos en modo imperativo:

```bash
git add .
git commit -m "Agrega función de limpieza de nulos en utils.py"
```

Ejemplos: `"Agrega..."`, `"Corrige..."`, `"Refactoriza..."`, `"Elimina..."`.

## 9. Seguridad

- Nunca commitees tokens, contraseñas ni cadenas de conexión. Usá Colab
  Secrets o variables de entorno.
- Revisá el `.gitignore` antes del primer commit, no después.
- Si un secreto llegó a subirse, revocalo inmediatamente y reescribí el
  historial de git (`git filter-repo`) antes de seguir trabajando en el
  repo — borrar el archivo en un commit nuevo **no** lo elimina del
  historial.

