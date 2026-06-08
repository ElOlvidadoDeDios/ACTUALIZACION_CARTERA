import os
import pyodbc
import pandas as pd
import logging
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
load_dotenv()

# Conexiones
REMOTE_DB = f"DRIVER={{SQL Server}};SERVER={os.getenv('DB_UPSTREAM_SERVER')};DATABASE={os.getenv('DB_UPSTREAM_DATABASE')};UID={os.getenv('DB_UPSTREAM_USER')};PWD={os.getenv('DB_UPSTREAM_PASSWORD')};"
LOCAL_DB = f"DRIVER={{SQL Server}};SERVER={os.getenv('DB_DOWNSTREAM_SERVER')};DATABASE={os.getenv('DB_DOWNSTREAM_DATABASE')};Trusted_Connection=yes;"


def sync_data(vista, tabla, periodo, mapeo_columnas):
    conn_remote = None
    conn_local = None
    try:
        logging.info(f"--- Sincronizando: {vista} -> {tabla} ---")

        # 1. Extraer
        conn_remote = pyodbc.connect(REMOTE_DB)
        query = (
            f"SELECT * FROM [TRANSACMIF].[dbo].[{vista}] WHERE Periodo = '{periodo}'"
        )
        df = pd.read_sql(query, conn_remote)

        if df.empty:
            logging.warning(f"No hay datos para {periodo} en {vista}")
            conn_remote.close()
            return

        # 2. Preparar datos
        df = df.rename(columns=mapeo_columnas)
        columnas_finales = list(mapeo_columnas.values())
        df = df[columnas_finales]

        # 3. Cargar
        conn_local = pyodbc.connect(LOCAL_DB)
        cursor = conn_local.cursor()

        # Borrado y carga
        cursor.execute(
            f"DELETE FROM [dm_productividad].[dbo].[{tabla}] WHERE Periodo = '{periodo}'"
        )

        cols_str = ", ".join(columnas_finales)
        placeholders = ", ".join(["?"] * len(columnas_finales))
        sql_insert = f"INSERT INTO [dm_productividad].[dbo].[{tabla}] ({cols_str}) VALUES ({placeholders})"

        for _, row in df.iterrows():
            cursor.execute(sql_insert, tuple(row))

        conn_local.commit()
        logging.info(f"✅ Éxito: {len(df)} registros cargados en {tabla}")

    except Exception as e:
        if conn_local:
            conn_local.rollback()
        logging.error(f"❌ Error en {tabla}: {e}")
    finally:
        if conn_remote:
            conn_remote.close()
        if conn_local:
            conn_local.close()


if __name__ == "__main__":
    periodo = os.getenv("PERIODO_PROCESO")

    mapa_agencia = {
        "Periodo": "Periodo",
        "IdSAgencia": "IdSAgencia",
        "CarteraInicial": "CarteraInicial",
        "MetaMoraCPP": "Mora9Meta",
        "MetaMoraDeficiente": "Mora31Meta",
    }
    mapa_asesor = {
        "Periodo": "Periodo",
        "IdSAsesor": "IdSAsesor",
        "CarteraInicial": "CarteraInicial",
        "Mora9Meta": "Mora9Meta",
        "Mora31Meta": "Mora31Meta",
    }

    sync_data(
        os.getenv("VISTA_AGENCIA"), os.getenv("TABLA_AGENCIA"), periodo, mapa_agencia
    )
    sync_data(
        os.getenv("VISTA_ASESOR"), os.getenv("TABLA_ASESOR"), periodo, mapa_asesor
    )
