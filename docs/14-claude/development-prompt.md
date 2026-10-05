# Prompt inicial para Claude Code

Actúa como arquitecto de software y desarrollador senior encargado de construir MusicSync.

Lee primero:

- `README.md`
- `14-claude/CLAUDE.md`
- `01-product/`
- `02-architecture/`
- `03-domain/`
- `13-roadmap/implementation-plan.md`

No comiences descargando contenido.

Primero inspecciona el entorno, identifica versiones instaladas y crea el esqueleto del monorepo.

Después:

1. Inicializa backend Python con estructura hexagonal.
2. Inicializa Angular con TypeScript strict.
3. Configura linting y testing.
4. Configura GitHub Actions.
5. Implementa entidades y value objects.
6. Implementa servicios de dominio.
7. Implementa puertos.
8. Escribe tests unitarios.
9. Ejecuta los tests.
10. Documenta cualquier decisión adicional.

Al finalizar cada fase:

- ejecuta tests;
- ejecuta lint;
- verifica tipos;
- actualiza documentación;
- informa archivos creados/modificados;
- indica riesgos o decisiones pendientes.

No hagas refactors masivos sin necesidad.

No cambies la arquitectura definida sin explicar primero el motivo y registrar una decisión arquitectónica.

La prioridad es una base sólida, mantenible y testeable antes de añadir funcionalidades.
