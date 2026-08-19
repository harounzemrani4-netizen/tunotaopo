"""Python twin of js/engine/scoring.js for independent verification."""

from __future__ import annotations

import math
from typing import Any


def is_finite(value: Any) -> bool:
    return isinstance(value, (int, float)) and math.isfinite(value)


def round_to(value: float, digits: int) -> float:
    factor = 10**digits
    return math.floor(value * factor + 0.5 + 1e-12) / factor


def clamp(value: float, min_value: float | None, max_value: float | None) -> float:
    out = value
    if min_value is not None and out < min_value:
        out = min_value
    if max_value is not None and out > max_value:
        out = max_value
    return out


def to_int(value: Any, label: str) -> int:
    if value in ("", None):
        raise ValueError(f"Indica {label}.")
    if isinstance(value, str) and value.strip() == "":
        raise ValueError(f"Indica {label}.")
    if isinstance(value, bool) or (isinstance(value, float) and not value.is_integer()):
        raise ValueError(f"{label} debe ser un número entero.")
    n = int(value) if isinstance(value, int) else float(value)
    if isinstance(n, float):
        if not n.is_integer():
            raise ValueError(f"{label} debe ser un número entero.")
        n = int(n)
    if n < 0:
        raise ValueError(f"{label} no puede ser negativo.")
    return n


def optional_number(value: Any) -> float | None:
    if value in ("", None):
        return None
    if isinstance(value, str) and value.strip() == "":
        return None
    if isinstance(value, str):
        value = value.replace(",", ".")
    return float(value)


def optional_int(value: Any, label: str) -> int | None:
    n = optional_number(value)
    if n is None:
        return None
    if n != int(n) or n < 0:
        raise ValueError(f"{label} debe ser un entero mayor o igual que 0.")
    return int(n)


def penalty_per_error(stage: dict[str, Any]) -> float:
    if is_finite(stage.get("incorrect_penalty")):
        return float(stage["incorrect_penalty"])
    correct = float(stage["correct_value"]) if is_finite(stage.get("correct_value")) else 1.0
    divisor = stage.get("incorrect_divisor")
    if not is_finite(divisor) and is_finite(stage.get("options_count")):
        divisor = stage["options_count"] - 1
    if is_finite(divisor) and divisor != 0:
        return correct / divisor
    return 0.0


def resolve_valid_questions(stage: dict[str, Any], inputs: dict[str, Any]) -> int:
    override = optional_int(inputs.get(f"{stage['id']}_valid"), f"preguntas válidas de {stage['label']}")
    fallback = stage["valid_questions"] if is_finite(stage.get("valid_questions")) else stage["questions"]
    valid = fallback if override is None else override
    if not is_finite(valid) or valid < 1:
        raise ValueError(f"{stage['label']}: las preguntas válidas deben ser al menos 1.")
    original = stage["questions"] if is_finite(stage.get("questions")) else valid
    if valid > original + (stage.get("reserve_questions") or 0):
        raise ValueError(f"{stage['label']}: las preguntas válidas no pueden superar el cuestionario más la reserva.")
    return int(valid)


def apply_round_clamp(raw: float, stage: dict[str, Any]) -> dict[str, float]:
    min_v = stage["clamp_min"] if is_finite(stage.get("clamp_min")) else None
    max_v = stage["clamp_max"] if is_finite(stage.get("clamp_max")) else (
        stage["maximum"] if is_finite(stage.get("maximum")) else None
    )
    score = clamp(raw, min_v, max_v)
    digits = stage.get("rounding")
    rounded = round_to(score, digits) if is_finite(digits) else score
    return {"raw": raw, "score": score, "rounded": rounded}


def evaluate_net_or_fixed(stage: dict[str, Any], hits: int, errors: int, valid: int) -> dict[str, Any]:
    blanks = valid - hits - errors
    if blanks < 0:
        raise ValueError(f"{stage['label']}: aciertos + errores no pueden superar {valid} preguntas válidas.")
    correct = float(stage["correct_value"]) if is_finite(stage.get("correct_value")) else 1.0
    blank_value = float(stage["blank_value"]) if is_finite(stage.get("blank_value")) else 0.0
    raw = hits * correct - errors * penalty_per_error(stage) + blanks * blank_value
    packed = apply_round_clamp(raw, stage)
    packed["penalty"] = errors * penalty_per_error(stage)
    return _scored_result(stage, hits, errors, blanks, valid, packed)


def evaluate_scaled(stage: dict[str, Any], hits: int, errors: int, valid: int) -> dict[str, Any]:
    blanks = valid - hits - errors
    if blanks < 0:
        raise ValueError(f"{stage['label']}: aciertos + errores no pueden superar {valid} preguntas válidas.")
    divisor = stage.get("incorrect_divisor")
    if not is_finite(divisor) and is_finite(stage.get("options_count")):
        divisor = stage["options_count"] - 1
    if not is_finite(divisor) or divisor == 0:
        raise ValueError(f"{stage['label']}: falta incorrect_divisor u options_count.")
    maximum = stage["maximum"] if is_finite(stage.get("maximum")) else valid
    raw = maximum * (hits - errors / divisor) / valid
    packed = apply_round_clamp(raw, stage)
    packed["penalty"] = errors / divisor
    return _scored_result(stage, hits, errors, blanks, valid, packed)


def _scored_result(stage: dict[str, Any], hits: int, errors: int, blanks: int, valid: int, packed: dict[str, Any]) -> dict[str, Any]:
    minimum = stage["minimum"] if is_finite(stage.get("minimum")) else None
    rounded = packed["rounded"]
    passed = None if minimum is None else rounded >= minimum
    verdict = "supera_minimo" if passed is True else "no_alcanza_minimo" if passed is False else None
    return {
        "id": stage["id"],
        "label": stage["label"],
        "model": stage["model"],
        "hits": hits,
        "errors": errors,
        "blanks": blanks,
        "valid_questions": valid,
        "penalty": packed.get("penalty"),
        "raw": packed["raw"],
        "score": packed["score"],
        "rounded": rounded,
        "verdict": verdict,
        "passed": passed,
        "minimum": minimum,
        "maximum": stage.get("maximum"),
        "eliminatory": stage.get("eliminatory") is True,
    }


def evaluate_pass_fail_errors(stage: dict[str, Any], errors: int) -> dict[str, Any]:
    limit = stage.get("questions", stage.get("valid_questions"))
    if is_finite(limit) and errors > limit:
        raise ValueError(f"{stage['label']}: los errores no pueden superar {limit}.")
    threshold = stage.get("fail_if_errors_gte")
    passed = errors < threshold
    return {
        "id": stage["id"],
        "label": stage["label"],
        "model": "pass_fail_errors",
        "errors": errors,
        "rounded": None,
        "verdict": "apto" if passed else "no_apto",
        "passed": passed,
        "eliminatory": stage.get("eliminatory") is True,
    }


def evaluate_transform(stage: dict[str, Any], source: dict[str, Any] | None) -> dict[str, Any]:
    if not source or not is_finite(source.get("rounded")) or not is_finite(stage.get("cut")):
        return {
            "id": stage["id"],
            "label": stage["label"],
            "model": "transform",
            "rounded": None,
            "passed": None,
            "verdict": "sin_umbral",
            "pd": source.get("rounded") if source else None,
            "cut": stage.get("cut"),
        }
    pd = source["rounded"]
    cut = stage["cut"]
    if pd < cut:
        return {
            "id": stage["id"],
            "label": stage["label"],
            "model": "transform",
            "rounded": None,
            "passed": False,
            "verdict": "no_alcanza_minimo",
            "pd": pd,
            "cut": cut,
        }
    pd_max = stage.get("pd_max", source.get("maximum"))
    raw = stage["cal_max"] if pd >= pd_max else stage["cal_min"] + (stage["cal_max"] - stage["cal_min"]) * (pd - cut) / (pd_max - cut)
    rounded = round_to(raw, stage["rounding"]) if is_finite(stage.get("rounding")) else raw
    return {
        "id": stage["id"],
        "label": stage["label"],
        "model": "transform",
        "rounded": rounded,
        "passed": True,
        "verdict": "supera_minimo",
        "pd": pd,
        "cut": cut,
    }


def evaluate_stage(stage: dict[str, Any], inputs: dict[str, Any], by_id: dict[str, Any]) -> dict[str, Any]:
    model = stage["model"]
    if model == "transform":
        cut = optional_number(inputs.get(f"{stage['id']}_cut", inputs.get(f"{stage['source_stage']}_cut")))
        clone = dict(stage)
        clone["cut"] = cut
        return evaluate_transform(clone, by_id.get(stage["source_stage"]))
    if model == "pass_fail_errors":
        return evaluate_pass_fail_errors(stage, to_int(inputs.get(f"{stage['id']}_errors"), f"errores de {stage['label']}"))
    hits = to_int(inputs.get(f"{stage['id']}_hits"), f"aciertos de {stage['label']}")
    errors = to_int(inputs.get(f"{stage['id']}_errors"), f"errores de {stage['label']}")
    valid = resolve_valid_questions(stage, inputs)
    if model == "scaled_score":
        return evaluate_scaled(stage, hits, errors, valid)
    if model in {"net_score", "fixed_value"}:
        return evaluate_net_or_fixed(stage, hits, errors, valid)
    raise ValueError(f"Modelo no soportado: {model}")


def evaluate(config: dict[str, Any], inputs: dict[str, Any] | None = None) -> dict[str, Any]:
    inputs = inputs or {}
    by_id: dict[str, Any] = {}
    order: list[str] = []
    pending = list(config["stages"])
    guard = 0
    while pending and guard < 40:
        guard += 1
        nxt = []
        progressed = False
        for stage in pending:
            if stage["model"] in {"aggregate", "multi_stage"}:
                progressed = True
                continue
            if stage["model"] == "transform" and stage["source_stage"] not in by_id:
                nxt.append(stage)
                continue
            result = evaluate_stage(stage, inputs, by_id)
            by_id[result["id"]] = result
            order.append(result["id"])
            progressed = True
        if not progressed:
            break
        pending = nxt

    aggregates_cfg = list(config.get("aggregates") or [])
    if config.get("aggregate") and not aggregates_cfg:
        aggregates_cfg = [config["aggregate"]]
    aggregates = {}
    for agg in aggregates_cfg:
        ids = agg.get("include") or agg.get("stages") or []
        if any(i not in by_id or not is_finite(by_id[i].get("rounded")) for i in ids):
            total = None
        else:
            total = sum(by_id[i]["rounded"] for i in ids)
            if is_finite(agg.get("rounding")):
                total = round_to(total, agg["rounding"])
        aggregates[agg["id"]] = {"id": agg["id"], "label": agg.get("label", agg["id"]), "value": total, "maximum": agg.get("maximum")}

    merits = None
    if config.get("merits"):
        m = config["merits"]
        value = optional_number(inputs.get(m.get("id"), inputs.get("merits", inputs.get("concurso"))))
        if value is not None:
            minimum = m.get("minimum", 0)
            maximum = m.get("maximum")
            if value < minimum or (is_finite(maximum) and value > maximum):
                raise ValueError("concurso out of range")
            merits = {
                "id": m.get("id", "merits"),
                "value": round_to(value, m["rounding"]) if is_finite(m.get("rounding")) else value,
            }

    opposition_id = (config.get("aggregate") or {}).get("id", "oposicion")
    opposition = aggregates.get(opposition_id, {}).get("value")
    process_total = opposition
    if merits is not None and is_finite(opposition):
        digits = config.get("process_rounding") or (config.get("aggregate") or {}).get("rounding") or 4
        process_total = round_to(opposition + merits["value"], digits)

    all_passed = all(item.get("passed") is not False for item in by_id.values() if item.get("eliminatory"))
    reqs = config.get("requirements") or []
    if reqs:
        all_passed = all(
            all(by_id.get(i, {}).get("passed") is not False for i in (req.get("stages") or by_id))
            for req in reqs
            if req.get("type") in {"all_passed", "all_eliminatory_passed"}
        )

    return {
        "slug": config.get("slug"),
        "stages": [by_id[i] for i in order],
        "byId": by_id,
        "aggregates": aggregates,
        "merits": merits,
        "opposition_total": opposition,
        "process_total": process_total,
        "all_required_passed": all_passed,
    }
