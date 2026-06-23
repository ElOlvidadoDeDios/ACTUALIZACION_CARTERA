import os
import atexit
import logging
import warnings
import pyodbc
import pandas as pd
from dotenv import load_dotenv

# 1. Ajustes estéticos y de control de desbordamiento de logs
warnings.filterwarnings("ignore", category=UserWarning, module="pandas")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOG_FILE = os.path.join(BASE_DIR, "ejecucion_diaria.log")
MAX_REGISTROS = 10

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler(LOG_FILE, encoding="utf-8"), logging.StreamHandler()],
)


def purgar_logs_antiguos():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            lineas = f.readlines()
        if len(lineas) > MAX_REGISTROS:
            with open(LOG_FILE, "w", encoding="utf-8") as f:
                f.writelines(lineas[-MAX_REGISTROS:])


atexit.register(purgar_logs_antiguos)
load_dotenv()

# 2. Carga de credenciales dinámicas desde tu archivo .env
REMOTE_DB = f"DRIVER={{SQL Server}};SERVER={os.getenv('DB_UPSTREAM_SERVER')};DATABASE={os.getenv('DB_UPSTREAM_DATABASE')};UID={os.getenv('DB_UPSTREAM_USER')};PWD={os.getenv('DB_UPSTREAM_PASSWORD')};"
LOCAL_DB = f"DRIVER={{SQL Server}};SERVER={os.getenv('DB_DOWNSTREAM_SERVER')};DATABASE={os.getenv('DB_DOWNSTREAM_DATABASE')};Trusted_Connection=yes;"

# 💡 EXTRACCIÓN DINÁMICA DE LA CONFIGURACIÓN DE TU .ENV
BD_DESTINO = os.getenv("DB_DOWNSTREAM_DATABASE")
TABLA_DESTINO = os.getenv("TABLA_PRODIARIA")


def ejecutar_sincronizacion_diaria():
    logging.info(f"=== INICIANDO ACTUALIZACIÓN EN TIEMPO REAL: {TABLA_DESTINO} ===")
    conn_remote = None
    conn_local = None

    try:
        # 🚀 PASO 1: Extraer data parcial consolidada del día desde el servidor central (TRANSACMIF)
        query_extract = """
        SELECT
            CAST(GETDATE() AS DATE) AS Fecha,
            CONVERT(CHAR(6), GETDATE(), 112) AS Periodo,
            CAST(
                CASE
                    WHEN T_ANA.ID_AGE = '98' THEN
                        CASE
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%10' THEN '10'
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%11' THEN '11'
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%12' THEN '12'
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%13' THEN '13'
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%6'  THEN '06'
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%7'  THEN '07'
                            ELSE '98'
                        END
                    WHEN T_ANA.ID_AGE = '01' THEN
                        CASE
                            WHEN RTRIM(T_ANA.ID_USER) LIKE '%%9' THEN '09'
                            ELSE '01'
                        END
                    ELSE T_ANA.ID_AGE
                END AS INT
            ) AS IdSAgencia,
            COUNT(T_PTM.PAGARE) AS ColocacionNumReal,
            SUM(T_PTM.MONTO_PRESTAMO) AS ColocacionMontoReal
        FROM dbo.PRESTAMO T_PTM
        INNER JOIN dbo.PREEC T_PRE 
            ON T_PRE.CUENTA = T_PTM.CUENTA 
            AND T_PRE.OTORGA = T_PTM.OTORGA 
            AND T_PRE.PAGARE = T_PTM.PAGARE 
            AND T_PRE.PERIODO = CONVERT(CHAR(6), GETDATE(), 112)
        INNER JOIN SEGURIDAD.DBO.ANAREC T_ANA 
            ON T_ANA.ID_ANAREC = T_PRE.ID_ANA 
            AND T_ANA.FLAG_ANAREC = 'A'
        INNER JOIN SEGURIDAD.dbo.USUARIOS T_USU 
            ON T_USU.ID_USER = T_ANA.ID_USER
        INNER JOIN SEGURIDAD.dbo.GRUPOUSER T_GRU 
            ON T_GRU.ID_GRUPO = T_USU.ID_GRUPO 
            AND T_GRU.NOM_GRUPO = 'CREDITOS'
        WHERE CAST(T_PTM.OTORGA AS DATE) = CAST(GETDATE() AS DATE)
          AND T_PTM.TIPO_PROD <> '52'
          AND T_USU.ID_USER NOT IN (
              'PRECASTIGO', 'RJULI6', 'RJULIACA', 'RLIMA7', 'RQUILLA3', 'RSICUA4',
              'LHR5', 'HTEJ5', 'TKPN5', 'GHVJ5', 'OTA5', 'SDHF5', 'CMN5', 'HQND5'
          )
        GROUP BY
            CASE
                WHEN T_ANA.ID_AGE = '98' THEN
                    CASE
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%10' THEN '10'
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%11' THEN '11'
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%12' THEN '12'
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%13' THEN '13'
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%6'  THEN '06'
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%7'  THEN '07'
                        ELSE '98'
                    END
                WHEN T_ANA.ID_AGE = '01' THEN
                    CASE
                        WHEN RTRIM(T_ANA.ID_USER) LIKE '%%9' THEN '09'
                        ELSE '01'
                    END
                ELSE T_ANA.ID_AGE
            END;
        """

        conn_remote = pyodbc.connect(REMOTE_DB)
        df = pd.read_sql(query_extract, conn_remote)
        conn_remote.close()

        if df.empty:
            logging.warning(
                "⚠️ No se registran colocaciones transaccionadas en lo que va del día."
            )
            return

        # 🚀 PASO 2: Carga Destino Segura (Idempotente) utilizando variables del .env
        conn_local = pyodbc.connect(LOCAL_DB)
        cursor = conn_local.cursor()

        # Inyección dinámica de nombres de tablas y bases de datos mapeadas
        cursor.execute(
            f"DELETE FROM [{BD_DESTINO}].[dbo].[{TABLA_DESTINO}] WHERE Fecha = CAST(GETDATE() AS DATE);"
        )

        sql_insert = f"""
            INSERT INTO [{BD_DESTINO}].[dbo].[{TABLA_DESTINO}] 
            (Fecha, Periodo, IdSAgencia, ColocacionNumReal, ColocacionMontoReal) 
            VALUES (?, ?, ?, ?, ?)
        """

        params = list(
            zip(
                df["Fecha"],
                df["Periodo"],
                df["IdSAgencia"],
                df["ColocacionNumReal"],
                df["ColocacionMontoReal"],
            )
        )

        cursor.fast_executemany = True
        cursor.executemany(sql_insert, params)
        conn_local.commit()

        logging.info(
            f"✅ ÉXITO: {len(df)} agencias con actividad incremental diaria mapeadas en {TABLA_DESTINO}."
        )

    except Exception as e:
        if conn_local:
            conn_local.rollback()
        logging.error(f"❌ ERROR CRÍTICO en el pipeline diario: {str(e)}")
    finally:
        if conn_local:
            conn_local.close()


if __name__ == "__main__":
    ejecutar_sincronizacion_diaria()
