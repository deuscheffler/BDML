ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_Cantidad
CHECK (cantidad > 0);
GO

ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_DiasProg
CHECK (dias_envio_prog >= 0);
GO


ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_DiasReal
CHECK (dias_envio_real >= 0);
GO

ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_PrecioProducto
CHECK (precio_producto >= 0);
GO

ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_PrecioBase
CHECK (precio_base >= 0);
GO

ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_Latitud
CHECK (latitud BETWEEN -90 AND 90);
GO

ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_Longitud
CHECK (longitud BETWEEN -180 AND 180);
GO

ALTER TABLE Pedido
ADD CONSTRAINT CK_Pedido_Riesgo
CHECK (riesgo_retraso IN (0,1));
GO


--  VALORES POR DEFECTO

--Fecha del pedido
ALTER TABLE Pedido
ADD CONSTRAINT DF_Pedido_FechaPedido
DEFAULT(GETDATE()) FOR fecha_pedido;
GO
--Fecha de envío
ALTER TABLE Pedido
ADD CONSTRAINT DF_Pedido_FechaEnvio
DEFAULT(GETDATE()) FOR fecha_envio;
GO
--Riesgo de retraso
ALTER TABLE Pedido
ADD CONSTRAINT DF_Pedido_Riesgo
DEFAULT(0) FOR riesgo_retraso;
GO
--Cantidad
ALTER TABLE Pedido
ADD CONSTRAINT DF_Pedido_Cantidad
DEFAULT(1) FOR cantidad;
GO

-- INDICES

--Índice para Producto
CREATE NONCLUSTERED INDEX IX_Pedido_Producto
ON Pedido(id_producto);
GO
--Índice para Destino
CREATE NONCLUSTERED INDEX IX_Pedido_Destino
ON Pedido(id_destino);
GO
--Índice para Cliente
CREATE NONCLUSTERED INDEX IX_Pedido_Cliente
ON Pedido(id_ubicacion_cliente);
GO
--Índice para Fecha
CREATE NONCLUSTERED INDEX IX_Pedido_Fecha
ON Pedido(fecha_pedido);
GO
--Índice para Estado
CREATE NONCLUSTERED INDEX IX_Pedido_Estado
ON Pedido(estado_pedido);
GO
--Índice para Riesgo
CREATE NONCLUSTERED INDEX IX_Pedido_Riesgo
ON Pedido(riesgo_retraso);
GO


CREATE NONCLUSTERED INDEX IX_Pedido_ML
ON Pedido
(
    estado_pedido,
    fecha_pedido,
    riesgo_retraso
);
GO

SELECT
    name,
    type_desc
FROM sys.indexes
WHERE object_id = OBJECT_ID('Pedido');