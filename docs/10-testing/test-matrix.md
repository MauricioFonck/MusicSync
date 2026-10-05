# Matriz mínima

| Caso | Resultado esperado |
|---|---|
| URL válida | análisis correcto |
| URL inválida | error controlado |
| pista nueva | descarga |
| source ID existente | omitida |
| checksum existente | duplicada |
| metadata equivalente | posible duplicado |
| USB ausente | trabajo no inicia |
| USB desconectada | pausa segura |
| USB reconectada | reanudación |
| poco espacio | error antes de escribir |
| archivo corrupto | no se marca completado |
| reinicio | recuperación |
| cancelación | estado CANCELLED |
