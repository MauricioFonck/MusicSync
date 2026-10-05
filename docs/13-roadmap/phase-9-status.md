# Estado de la Fase 9 — Robustez

La Fase 9 incorpora `RetryPolicy` y refuerza `DownloadOrchestrator` con reintentos acotados por item, aislamiento de errores y reanudación de jobs en estados fallidos o parcialmente completados. Los items completados se omiten al reanudar y un job ya completado retorna sin repetir descargas, haciendo el flujo idempotente.

`DownloadJob.resume()` formaliza las transiciones desde `PAUSED`, `FAILED` y `PARTIALLY_COMPLETED`. Las pruebas cubren errores transitorios, tercer intento exitoso y reejecución sin duplicar trabajo.
