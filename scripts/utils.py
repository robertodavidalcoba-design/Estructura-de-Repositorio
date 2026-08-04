"""
utils.py - Funciones auxiliares reutilizables para Google Colab.
"""

import pandas as pd
import matplotlib.pyplot as plt

def cargar_datos(filepath: str) -> pd.DataFrame:
    """Carga un archivo CSV y retorna un DataFrame de pandas."""
    try:
        df = pd.read_csv(filepath)
        print(f"✅ Datos cargados correctamente. Forma: {df.shape}")
        return df
    except Exception as e:
        print(f"❌ Error al cargar los datos: {e}")
        raise e

def guardar_grafico(figura: plt.Figure, filename: str) -> None:
    """Guarda una figura de Matplotlib en la carpeta outputs/."""
    path = f"outputs/{filename}"
    figura.savefig(path, bbox_inches='tight', dpi=300)
    print(f"📊 Gráfico guardado en: {path}")
