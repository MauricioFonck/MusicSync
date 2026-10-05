# Frontend Angular

## Stack

- Angular
- TypeScript
- Angular Material
- Angular CDK
- RxJS
- Signals
- ESLint
- Prettier
- Vitest
- Playwright

## Estructura

```text
src/app/
├── core/
│   ├── config/
│   ├── guards/
│   ├── interceptors/
│   ├── services/
│   ├── websocket/
│   └── models/
├── shared/
│   ├── components/
│   ├── directives/
│   ├── pipes/
│   └── utils/
├── features/
│   ├── dashboard/
│   ├── downloads/
│   ├── storage/
│   ├── history/
│   └── settings/
├── layout/
│   ├── shell/
│   ├── sidebar/
│   ├── header/
│   └── footer/
├── app.routes.ts
└── app.config.ts
```

## Regla

`core` contiene servicios globales.

`shared` contiene piezas reutilizables.

`features` contiene comportamiento específico de negocio.

Cada feature debe intentar mantener cerca sus componentes, servicios, modelos y estado.
