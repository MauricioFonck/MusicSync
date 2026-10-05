# GitHub Actions

Pipeline:

```text
push / pull_request
  |
  +-- backend lint
  +-- backend tests
  +-- backend type check
  +-- frontend lint
  +-- frontend tests
  +-- build
```

Los jobs deben usar versiones fijadas o rangos controlados y cachear dependencias cuando sea seguro.

Branches:

- `main`
- `develop`
- `feature/*`
- `fix/*`
