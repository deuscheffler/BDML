-- ============================================================================
-- Tabla para persistir los resultados del modelo no supervisado (KMeans).
-- Se deja fuera cluster_dbscan (no implementado en el pipeline actual).
-- ============================================================================
USE BD_ML_RELACIONAL;
GO

DROP TABLE IF EXISTS ResultadoModeloNoSupervisado;
GO

CREATE TABLE ResultadoModeloNoSupervisado
(
    id_pedido       INT NOT NULL PRIMARY KEY,
    cluster_kmeans  INT NOT NULL,
    es_anomalia     BIT NOT NULL DEFAULT 0,
    es_outlier      BIT NOT NULL DEFAULT 0,
    fecha_calculo   DATETIME NOT NULL DEFAULT GETDATE(),

    CONSTRAINT FK_ResultadoNoSup_Pedido
        FOREIGN KEY (id_pedido) REFERENCES Pedido(id_pedido)
);
GO

-- ============================================================================
-- Vista de ML actualizada: LEFT JOIN (no INNER) porque un pedido nuevo puede
-- no tener todavía cluster asignado hasta la próxima corrida del modelo.
-- ============================================================================
CREATE OR ALTER VIEW vw_ML_DataCoSupplyChain
AS
SELECT

    P.id_pedido,
    P.id_raw,

    P.fecha_pedido,
    P.fecha_envio,

    P.estado_pedido,
    P.estado_entrega,
    P.tipo_transaccion,
    P.modo_envio,

    P.dias_envio_real,
    P.dias_envio_prog,

    P.precio_producto,
    P.precio_base,

    P.beneficio_pedido,
    P.ventas_cliente,
    P.margen_ganancia_item,
    P.cantidad,
    P.ventas,
    P.total_item,
    P.ganancia_pedido,

    P.riesgo_retraso,

    P.latitud,
    P.longitud,

    C.nombre_categoria,

    PR.nombre_producto,

    U.ciudad_cliente,
    U.pais_cliente,

    D.ciudad_destino,
    D.estado_destino,
    D.pais_destino,
    D.region_destino,

    -- Resultados del modelo no supervisado (pueden ser NULL si el pedido
    -- todavía no ha pasado por una corrida de KMeans)
    R.cluster_kmeans,
    R.es_anomalia,
    R.es_outlier

FROM Pedido P

INNER JOIN Producto PR
    ON P.id_producto = PR.id_producto

INNER JOIN Categoria C
    ON PR.id_categoria = C.id_categoria

INNER JOIN Destino D
    ON P.id_destino = D.id_destino

INNER JOIN UbicacionCliente U
    ON P.id_ubicacion_cliente = U.id_ubicacion_cliente

LEFT JOIN ResultadoModeloNoSupervisado R
    ON P.id_pedido = R.id_pedido;
GO