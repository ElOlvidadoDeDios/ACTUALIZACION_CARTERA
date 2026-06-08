import os
import pyodbc
import pandas as pd
from dotenv import load_dotenv

# Cargar variables del .env
load_dotenv()

# Construcción de cadenas de conexión
REMOTE_DB = (
    f"DRIVER={{SQL Server}};"
    f"SERVER={os.getenv('DB_UPSTREAM_SERVER')};"
    f"DATABASE={os.getenv('DB_UPSTREAM_DATABASE')};"
    f"UID={os.getenv('DB_UPSTREAM_USER')};"
    f"PWD={os.getenv('DB_UPSTREAM_PASSWORD')};"
)

LOCAL_DB = (
    f"DRIVER={{SQL Server}};"
    f"SERVER={os.getenv('DB_DOWNSTREAM_SERVER')};"
    f"DATABASE={os.getenv('DB_DOWNSTREAM_DATABASE')};"
    f"Trusted_Connection=yes;"  # Asumimos Windows Auth en local
)


def sync_data(vista_origen, tabla_destino, periodo):
    try:
        logging.info(f"Iniciando sincronización: {vista_origen} -> {tabla_destino}")

        # 1. Extraer del servidor principal
        conn_remote = pyodbc.connect(REMOTE_DB)
        query = f"SELECT * FROM [TRANSACMIF].[dbo].[{vista_origen}] WHERE Periodo = '{periodo}'"
        df = pd.read_sql(query, conn_remote)
        conn_remote.close()

        if df.empty:
            logging.warning(
                f"No se encontraron datos para el periodo {periodo} en {vista_origen}"
            )
            return

        # 2. Cargar en servidor local (Borrado + Inserción)
        conn_local = pyodbc.connect(LOCAL_DB)
        cursor = conn_local.cursor()

        # Usamos una transacción para asegurar que no se pierdan datos si falla a la mitad
        cursor.execute("BEGIN TRANSACTION")
        cursor.execute(
            f"DELETE FROM [dm_productividad].[dbo].[{tabla_destino}] WHERE Periodo = '{periodo}'"
        )

        # Insertar registros
        for _, row in df.iterrows():
            cols = ", ".join(df.columns)
            placeholders = ", ".join(["?"] * len(row))
            cursor.execute(
                f"INSERT INTO [dm_productividad].[dbo].[{tabla_destino}] ({cols}) VALUES ({placeholders})",
                tuple(row),
            )

        conn_local.commit()
        logging.info(
            f"✅ Sincronización exitosa: {len(df)} registros cargados en {tabla_destino}"
        )

    except Exception as e:
        if "conn_local" in locals():
            conn_local.rollback()
        logging.error(f"❌ Error crítico en {tabla_destino}: {e}")
    finally:
        if "conn_local" in locals():
            conn_local.close()


if __name__ == "__main__":
    PERIODO_ACTUAL = "202606"
    sync_data("gc_cartera_agencia", "fct_stock_manubl_agencia_month", PERIODO_ACTUAL)
    sync_data("gc_cartera_asesor", "fct_stock_manubl_asesor_month", PERIODO_ACTUAL)
