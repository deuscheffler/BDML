SELECT
    COUNT(*) AS TotalRegistros,

    COUNT(DISTINCT ciudad_cliente + '|' + pais_cliente) AS ClientesUnicos,

    COUNT(DISTINCT nombre_producto) AS Productos,

    COUNT(DISTINCT categoria) AS Categorias,

    COUNT(DISTINCT ciudad_destino + '|' + estado_destino + '|' + pais_destino) AS Destinos

FROM dbo.DataCoSupplyChain_RAW;

CREATE TABLE UbicacionCliente
(
    id_ubicacion_cliente INT IDENTITY(1,1) PRIMARY KEY,

    ciudad_cliente VARCHAR(100) NOT NULL,

    pais_cliente VARCHAR(100) NOT NULL,

    CONSTRAINT UQ_UbicacionCliente
        UNIQUE (ciudad_cliente, pais_cliente)
);
GO

CREATE TABLE Pedido
(
    id_pedido INT IDENTITY(1,1) PRIMARY KEY,

    fecha_pedido DATETIME NOT NULL,

    fecha_envio DATETIME NOT NULL,

    tipo_transaccion VARCHAR(50),

    estado_pedido VARCHAR(50),

    estado_entrega VARCHAR(100),

    modo_envio VARCHAR(50),

    dias_envio_real INT,

    dias_envio_prog INT,

    latitud DECIMAL(10,7),

    longitud DECIMAL(10,7),

    beneficio_pedido DECIMAL(12,2),

    ventas_cliente DECIMAL(12,2),

    margen_ganancia_item DECIMAL(12,4),

    cantidad INT,

    ventas DECIMAL(12,2),

    total_item DECIMAL(12,2),

    ganancia_pedido DECIMAL(12,2),

    riesgo_retraso BIT,

    id_producto INT NOT NULL,

    id_destino INT NOT NULL,

    id_ubicacion_cliente INT NOT NULL
);
GO

INSERT INTO UbicacionCliente
(
    ciudad_cliente,
    pais_cliente
)

SELECT DISTINCT

       ciudad_cliente,

       pais_cliente

FROM DataCoSupplyChain_RAW;