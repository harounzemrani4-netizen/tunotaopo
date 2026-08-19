# Arquitectura — NotaOpo

Modo: **STATIC**.

```
notaopo/
  index.html
  assets/
  css/app.css
  js/engine/scoring.js
  js/components/
  data/oposiciones/*.json
  calculadoras/...
  metodologia/ fuentes/ aviso-legal/ privacidad/ cookies/ contacto/
```

- Motor: funciones puras. Autoridad de la fórmula = JSON.
- Generador local: `scripts/generate_pages.py` produce HTML indexable.
- Tests: `scripts/engine.py` (gemelo) + `tests/fixtures.json` con expected independientes.
- JavaScript solo para la calculadora interactiva.
- Sin `if (opposition === "...")`.
