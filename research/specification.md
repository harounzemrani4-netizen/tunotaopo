# Especificación MVP — NotaOpo

## Producto

Portal estático de calculadoras de nota atadas a convocatorias oficiales españolas.

Nombre de trabajo: **NotaOpo**. Dominio previsto: `https://notaopo.es` (pendiente de registro).

## Calculadoras V1

1. `/calculadoras/guardia-civil/calculadora-nota-2026/`
2. `/calculadoras/ayudantes-iipp/calculadora-nota-2026/`
3. `/calculadoras/auxilio-judicial/calculadora-nota-2026/`
4. `/calculadoras/auxiliar-administrativo-age/calculadora-nota-2026/`

No hay quinta. TAI y TCAE quedan en tanda 2, sin URL de producción.

## Motor

Declarativo. Una convocatoria combina modelos. El motor no contiene nombres de oposiciones.

Modelos: `net_score`, `scaled_score`, `fixed_value`, `pass_fail`, `pass_fail_errors`, `transform`, `multi_stage`, `aggregate`.

Blancos = preguntas válidas − aciertos − errores. Valor por defecto 0.

## UX

Herramienta above the fold. Desglose por prueba. Mínimo oficial ≠ corte de plaza. Sin “APROBADO” / “TIENES PLAZA” si la fórmula no lo permite.

## Monetización

Preparada e inactiva.

## Legal

Placeholders `[TITULAR]`, `[NIF]`, `[DOMICILIO]`, `[EMAIL]`.
