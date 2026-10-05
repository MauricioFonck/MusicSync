# Estado frontend

Preferir:

- Signals para estado local y derivado;
- RxJS para streams, HTTP y WebSocket;
- servicios por feature para operaciones;
- evitar un store global innecesario en el MVP.

El estado de una descarga debe sincronizarse con WebSocket y no depender únicamente de polling.
