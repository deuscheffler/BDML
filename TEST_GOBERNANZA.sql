EXEC sp_spaceused 'Pedido';
GO

EXEC sp_spaceused 'Producto';
GO

EXEC sp_spaceused 'Destino';
GO

EXEC sp_spaceused 'Categoria';
GO

EXEC sp_spaceused 'UbicacionCliente';
GO

SELECT
    OBJECT_NAME(I.object_id) AS Tabla,
    I.name AS Indice,
    S.user_seeks,
    S.user_scans,
    S.user_lookups,
    S.user_updates
FROM sys.dm_db_index_usage_stats S
INNER JOIN sys.indexes I
    ON S.object_id = I.object_id
   AND S.index_id = I.index_id
WHERE database_id = DB_ID()
ORDER BY Tabla;

DBCC CHECKDB
WITH NO_INFOMSGS;
GO

SELECT
    'Pedido' AS Tabla,
    COUNT(*) AS Registros
FROM Pedido

UNION ALL

SELECT
    'Producto',
    COUNT(*)
FROM Producto

UNION ALL

SELECT
    'Categoria',
    COUNT(*)
FROM Categoria

UNION ALL

SELECT
    'Destino',
    COUNT(*)
FROM Destino

UNION ALL

SELECT
    'UbicacionCliente',
    COUNT(*)
FROM UbicacionCliente;
