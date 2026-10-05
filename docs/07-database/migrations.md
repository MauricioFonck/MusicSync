# Migraciones

Usar Alembic.

Reglas:

1. Nunca modificar una migración ya aplicada.
2. Crear una nueva migración para cambios.
3. Probar upgrade y downgrade cuando sea viable.
4. Versionar migraciones en Git.
5. Ejecutar migraciones antes de iniciar el backend en entornos empaquetados cuando corresponda.
