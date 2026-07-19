-- ============================================================================
-- Activar READ_COMMITTED_SNAPSHOT (RCSI) en BD_ML_RELACIONAL
-- ============================================================================
-- Requiere acceso exclusivo a la BD. WITH ROLLBACK IMMEDIATE revierte
-- cualquier transacción abierta de otras conexiones (seguro si no hay
-- nadie más trabajando sobre la base en este momento).

-- 1) Opcional: ver quién está conectado antes de forzar
SELECT session_id, status, login_name, host_name, program_name
FROM sys.dm_exec_sessions
WHERE database_id = DB_ID('BD_ML_RELACIONAL')
  AND session_id <> @@SPID;

-- 2) Activar RCSI
ALTER DATABASE BD_ML_RELACIONAL
SET READ_COMMITTED_SNAPSHOT ON
WITH ROLLBACK IMMEDIATE;

-- 3) Verificar que quedó activo
SELECT name, is_read_committed_snapshot_on
FROM sys.databases
WHERE name = 'BD_ML_RELACIONAL';