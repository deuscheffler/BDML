-- CREACION DE PROCEDIMIENTOS ALMACENADOS

CREATE OR ALTER PROCEDURE sp_BuscarPedidoPorId

    @IdPedido INT

AS
BEGIN

    SET NOCOUNT ON;

    SELECT

        P.id_pedido,
        P.id_raw,
        P.fecha_pedido,
        P.fecha_envio,
        P.estado_pedido,
        P.estado_entrega,
        P.tipo_transaccion,
        P.modo_envio,
        P.ventas,
        P.ganancia_pedido,
        PR.nombre_producto,
        C.nombre_categoria,
        D.pais_destino,
        U.ciudad_cliente

    FROM Pedido P

    INNER JOIN Producto PR
        ON P.id_producto = PR.id_producto

    INNER JOIN Categoria C
        ON PR.id_categoria = C.id_categoria

    INNER JOIN Destino D
        ON P.id_destino = D.id_destino

    INNER JOIN UbicacionCliente U
        ON P.id_ubicacion_cliente = U.id_ubicacion_cliente

    WHERE P.id_pedido = @IdPedido;

END;
GO

EXEC sp_BuscarPedidoPorId 1;


-- RESUMEN POR PAIS

CREATE OR ALTER PROCEDURE sp_ResumenVentasPorPais

AS
BEGIN

    SET NOCOUNT ON;

    SELECT

        D.pais_destino,

        COUNT(*) AS TotalPedidos,

        SUM(P.ventas) AS VentasTotales,

        SUM(P.ganancia_pedido) AS GananciaTotal,

        AVG(P.dias_envio_real) AS PromedioEntrega

    FROM Pedido P

    INNER JOIN Destino D

        ON P.id_destino = D.id_destino

    GROUP BY

        D.pais_destino

    ORDER BY

        VentasTotales DESC;

END;
GO

EXEC sp_ResumenVentasPorPais;

-- CONSULTA POR FECHAS

CREATE OR ALTER PROCEDURE sp_PedidosPorFecha

    @FechaInicio DATETIME,

    @FechaFin DATETIME

AS
BEGIN

    SET NOCOUNT ON;

    SELECT *

    FROM vw_ML_DataCoSupplyChain

    WHERE fecha_pedido
    BETWEEN @FechaInicio
        AND @FechaFin

    ORDER BY fecha_pedido;

END;
GO

EXEC sp_PedidosPorFecha
'2016-01-01',
'2016-02-01';

-- ESTADISTICAS PARA ML

CREATE OR ALTER PROCEDURE sp_EstadisticasML

AS
BEGIN

    SET NOCOUNT ON;

    SELECT

        COUNT(*) AS TotalRegistros,

        SUM(CASE
                WHEN estado_pedido='COMPLETE'
                THEN 1
                ELSE 0
            END) AS Completados,

        SUM(CASE
                WHEN estado_pedido='CANCELED'
                THEN 1
                ELSE 0
            END) AS Cancelados,

        AVG(dias_envio_real) AS PromedioEntrega,

        AVG(ventas) AS VentaPromedio,

        AVG(ganancia_pedido) AS GananciaPromedio

    FROM Pedido;

END;
GO

EXEC sp_EstadisticasML;

-- DATSET PARA ML

CREATE OR ALTER PROCEDURE sp_DatasetML

AS
BEGIN

    SET NOCOUNT ON;

    SELECT *

    FROM vw_ML_DataCoSupplyChain

    ORDER BY fecha_pedido;

END;
GO

SELECT
name

FROM sys.procedures

ORDER BY name;