CREATE OR ALTER VIEW dbo.gc_cartera_agencia
WITH ENCRYPTION 
AS
SELECT 
    '202607' AS Periodo,
    
    -- Bloque de lógica unificado
    CASE
        WHEN T_ANA.ID_AGE = '98' THEN
            CASE
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%10' THEN '10'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%11' THEN '11'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%12' THEN '12'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%13' THEN '13'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%6'  THEN '06'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%7'  THEN '07'
                ELSE '98'
            END
        WHEN T_ANA.ID_AGE = '01' THEN
            CASE
                WHEN RIGHT(RTRIM(T_ANA.ID_USER), 1) <> '9' THEN '01'
                WHEN RIGHT(RTRIM(T_ANA.ID_USER), 1) = '9' THEN '09'
            END
        ELSE T_ANA.ID_AGE
    END AS IdSAgencia,

    SUM(T_PRE.SALDO_PRES) AS CarteraInicial,
    0.10 AS MetaMoraCPP,         
    0.02 AS MetaMoraDeficiente   

FROM PREEC T_PRE
INNER JOIN SEGURIDAD.DBO.ANAREC T_ANA
    ON T_ANA.ID_ANAREC = T_PRE.ID_ANA
    AND T_ANA.FLAG_ANAREC = 'A'
INNER JOIN SEGURIDAD.dbo.USUARIOS T_USU
    ON T_USU.ID_USER = T_ANA.ID_USER
INNER JOIN SEGURIDAD.dbo.GRUPOUSER T_GRU
    ON T_GRU.ID_GRUPO = T_USU.ID_GRUPO
    AND T_GRU.NOM_GRUPO = 'CREDITOS'
INNER JOIN SEGURIDAD.dbo.PERSONAL T_PER 
    ON T_PER.DNI = T_USU.DNI
WHERE
    T_PRE.PERIODO = '202607'           
    AND T_PRE.SALDO_PRES > 0            
    AND T_USU.ID_USER NOT IN (
        'PRECASTIGO', 'RJULI6', 'RJULIACA', 'RLIMA7', 'RQUILLA3', 'RSICUA4',
        'LHR5', 'HTEJ5', 'TKPN5', 'GHVJ5', 'OTA5', 'SDHF5', 'CMN5', 'HQND5'
    )
GROUP BY 
    -- Este bloque DEBE ser idéntico al del SELECT
    CASE
        WHEN T_ANA.ID_AGE = '98' THEN
            CASE
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%10' THEN '10'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%11' THEN '11'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%12' THEN '12'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%13' THEN '13'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%6'  THEN '06'
                WHEN RTRIM(T_ANA.ID_USER) LIKE '%7'  THEN '07'
                ELSE '98'
            END
        WHEN T_ANA.ID_AGE = '01' THEN
            CASE
                WHEN RIGHT(RTRIM(T_ANA.ID_USER), 1) <> '9' THEN '01'
                WHEN RIGHT(RTRIM(T_ANA.ID_USER), 1) = '9' THEN '09'
            END
        ELSE T_ANA.ID_AGE
    END;
GO