"""Compile a proposed wording review. No sampling or live scoring is performed."""
from __future__ import annotations

from collections import Counter
import hashlib
from itertools import combinations
import json


RELATIONS = {
    "equivalent": "Equivalencia propuesta",
    "related": "Variante con diferencias",
    "distinct": "Decisiones independientes",
    "contrasting": "Opciones contrapuestas, no complementarias",
}


def fingerprint(bank):
    content = json.dumps(bank, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def compile_review(bank, review):
    assert review["schemaVersion"] == 1
    assert review["status"] == "proposed-wording-review" and review["liveEligible"] is False
    assert review["bankVersion"] == bank["version"]
    assert review["bankFingerprint"] == fingerprint(bank), "Revisar la agrupación con la edición actual del banco"
    design = review["selectionDesign"]
    assert design["status"] == "proposal-only" and design["implemented"] is False
    assert design["targetLength"] is None and design["categoryQuotas"] is None
    questions = {q["id"]: q for q in bank["questions"]}
    assert len(questions) == len(bank["questions"])
    assert review["scope"]["questionCount"] == len(questions)
    assert review["scope"]["candidatePairsReviewed"] == len(review["reviews"])
    parties = bank["scope"]["analyzedParties"]
    parent = {qid: qid for qid in questions}

    def find(qid):
        while parent[qid] != qid:
            parent[qid] = parent[parent[qid]]
            qid = parent[qid]
        return qid

    ids, pairs, covered = set(), set(), set()
    for item in review["reviews"]:
        assert item["id"] not in ids
        ids.add(item["id"])
        assert item["relation"] in RELATIONS and item["rationale"].strip()
        assert len(item["questionIds"]) == 2
        a, b = item["questionIds"]
        assert a != b and a in questions and b in questions
        key = tuple(sorted((a, b)))
        assert key not in pairs, "Par repetido"
        pairs.add(key)
        covered.update((a, b))
        assert questions[a]["category"] == questions[b]["category"]
        if item["relation"] == "equivalent":
            parent[find(b)] = find(a)
    for item in review["reviews"]:
        if item["relation"] != "equivalent":
            a, b = item["questionIds"]
            assert find(a) != find(b), "Una variante distinta no puede quedar fusionada por transitividad"

    clusters = {}
    for qid in sorted(questions):
        clusters.setdefault(find(qid), []).append(qid)
    equivalents = {tuple(sorted(r["questionIds"])) for r in review["reviews"] if r["relation"] == "equivalent"}
    for members in clusters.values():
        assert all(tuple(pair) in equivalents for pair in combinations(members, 2)), "Revisar cada par antes de unir un grupo por transitividad"
    units = []
    for members in clusters.values():
        # A stable representative is a navigation anchor, not approved final wording.
        representative = min(members)
        digest = hashlib.sha256("\n".join(members).encode()).hexdigest()[:16]
        positions = {}
        for party in parties:
            known, ambiguous = [], []
            for qid in members:
                pos = questions[qid]["positions"][party]
                assert pos["proposedValue"] in (None, -2, 2)
                assert pos["proposedValue"] is None or pos["evidence"]
                if pos["proposedValue"] is not None:
                    known.append(qid)
                elif pos["evidence"]:
                    ambiguous.append(qid)
            values = {questions[qid]["positions"][party]["proposedValue"] for qid in known}
            conflict = len(values) > 1
            value = next(iter(values)) if len(values) == 1 and not ambiguous else None
            positions[party] = {
                "candidateValue": value,
                "status": "conflicting-draft" if conflict else "ambiguous-draft" if ambiguous else "consistent-draft" if value is not None else "undetermined",
                "sourceQuestionIds": known,
                "ambiguousQuestionIds": ambiguous,
            }
        units.append({
            "id": "decision-" + digest,
            "category": questions[representative]["category"],
            "questionIds": members,
            "representativeQuestionId": representative,
            "reviewIds": sorted(r["id"] for r in review["reviews"] if r["relation"] == "equivalent" and set(r["questionIds"]).issubset(members)),
            "positions": positions,
            "liveEligible": False,
        })
    units.sort(key=lambda u: (u["category"], u["id"]))
    equivalent = [u for u in units if len(u["questionIds"]) > 1]
    unit_by_question = {qid: u for u in units for qid in u["questionIds"]}
    families, family_ids, assigned_units = [], set(), set()
    for family in review.get("selectionFamilies", []):
        assert family["id"] not in family_ids
        family_ids.add(family["id"])
        assert family["status"] == "proposal-only" and family["maxPerShortSessionProposed"] == 1
        assert family["title"].strip() and family["rationale"].strip()
        members = family["questionIds"]
        assert len(members) >= 2 and len(set(members)) == len(members)
        assert all(qid in questions for qid in members)
        selected_units = {unit_by_question[qid]["id"] for qid in members}
        assert len(selected_units) >= 2, "Una familia de variantes necesita decisiones distintas, no solo alias equivalentes"
        assert not selected_units & assigned_units, "Familias solapadas: revisar las restricciones antes de proponer límites"
        assigned_units.update(selected_units)
        expanded = sorted({qid for member in members for qid in unit_by_question[member]["questionIds"]})
        categories = {questions[qid]["category"] for qid in expanded}
        assert len(categories) == 1
        families.append({
            **family,
            "category": next(iter(categories)),
            "expandedQuestionIds": expanded,
            "proposedUnitIds": sorted(selected_units),
            "liveEligible": False,
        })
    original_known = [sum(p["proposedValue"] is not None for p in q["positions"].values()) for q in questions.values()]
    grouped_known = [sum(p["candidateValue"] is not None for p in u["positions"].values()) for u in units]
    category_counts = []
    for category in bank["categories"]:
        source = [q for q in questions.values() if q["category"] == category["id"]]
        proposed = [u for u in units if u["category"] == category["id"]]
        category_counts.append({
            **category,
            "bankQuestions": len(source),
            "proposedUnits": len(proposed),
            "proposedUnitsWithTwoOrMoreParties": sum(sum(p["candidateValue"] is not None for p in u["positions"].values()) >= 2 for u in proposed),
        })
    histogram = Counter(original_known)
    counts = {
        "bankQuestions": len(questions),
        "reviewedPairs": len(review["reviews"]),
        "questionsInReviewedPairs": len(covered),
        "relations": dict(sorted(Counter(r["relation"] for r in review["reviews"]).items())),
        "proposedEquivalentGroups": len(equivalent),
        "questionsInEquivalentGroups": sum(len(u["questionIds"]) for u in equivalent),
        "potentialReduction": len(questions) - len(units),
        "proposedUnits": len(units),
        "originalQuestionsWithTwoOrMoreParties": sum(n >= 2 for n in original_known),
        "proposedUnitsWithTwoOrMoreParties": sum(n >= 2 for n in grouped_known),
        "commonToAllParties": sum(n == len(parties) for n in grouped_known),
        "maxDocumentedPartiesInOneUnit": max(grouped_known, default=0),
        "conflictingEquivalentGroups": sum(any(p["status"] == "conflicting-draft" for p in u["positions"].values()) for u in equivalent),
        "proposedSelectionFamilies": len(families),
        "questionsInSelectionFamilies": sum(len(f["expandedQuestionIds"]) for f in families),
        "approvedForProduction": 0,
    }
    return {
        "schemaVersion": 1,
        "status": "proposed-wording-review",
        "liveEligible": False,
        "reviewVersion": review["version"],
        "bankVersion": bank["version"],
        "bankFingerprint": review["bankFingerprint"],
        "reviewedAt": review["reviewedAt"],
        "counts": counts,
        "originalCoverageHistogram": [{"partiesWithPosition": n, "questions": histogram[n]} for n in sorted(histogram)],
        "categories": category_counts,
        "categoriesWithoutTwoPartyUnits": [c["id"] for c in category_counts if not c["proposedUnitsWithTwoOrMoreParties"]],
        # Singletons are implicit: this is an audit, not another editable bank.
        "equivalentGroups": equivalent,
        "selectionFamilies": families,
        "selectionDesign": design,
    }


def render_plan(bank, review, compiled, party_names, reference):
    counts = compiled["counts"]
    questions = {q["id"]: q for q in bank["questions"]}
    category_names = {c["id"]: c["title"] for c in bank["categories"]}
    out = []

    def line(value=""):
        out.append(value)

    line("PLAN DE AGRUPACIÓN Y SELECCIÓN · CUESTIONARIO")
    line(f"Propuesta editorial {review['version']} · {review['reviewedAt']} · banco {bank['version']}")
    line("No modifica el test piloto ni aprueba posiciones para calcular afinidades.")
    line()
    line("BANCO, DECISIONES Y DURACIÓN")
    line(f"Se conservan las {counts['bankQuestions']} formulaciones originales, sus identificadores, posiciones y fuentes. Las {len(bank['categories'])} categorías serán los apartados. El banco no es una encuesta individual.")
    line(f"Esta primera pasada revisa {counts['reviewedPairs']} pares, que afectan a {counts['questionsInReviewedPairs']} formulaciones. Propone {counts['proposedEquivalentGroups']} grupos de equivalencia de redacción, con {counts['questionsInEquivalentGroups']} formulaciones. De confirmarse, evitarían {counts['potentialReduction']} repeticiones y dejarían {counts['proposedUnits']} unidades provisionales; esa cifra tampoco es la longitud de una encuesta.")
    for relation, label in RELATIONS.items():
        line(f"{label}: {counts['relations'].get(relation, 0)} pares.")
    line("Las diferencias de cantidades, edades, ámbitos, condiciones, instrumentos o grado de compromiso se conservan. Opciones contrapuestas no se tratan como negaciones exactas: no ampliar un servicio no significa suprimirlo.")
    line("La reducción principal de la sesión vendrá de seleccionar decisiones, además de retirar equivalencias. No se decide todavía duración, cupos ni longitud definitiva. Si se exige al menos una pregunta por cada apartado no vacío, el mínimo aritmético es el número de apartados seleccionados; no demuestra que una pregunta mida adecuadamente un tema.")
    line()
    line("COBERTURA COMPARATIVA PENDIENTE")
    line(f"En el banco original, {counts['originalQuestionsWithTwoOrMoreParties']} formulaciones tienen posición propuesta para dos o más partidos. Una ausencia de vínculo no es neutralidad ni prueba de ausencia de postura.")
    for row in compiled["originalCoverageHistogram"]:
        parties_label = "partido" if row["partiesWithPosition"] == 1 else "partidos"
        questions_label = "formulación" if row["questions"] == 1 else "formulaciones"
        line(f"{row['partiesWithPosition']} {parties_label} con posición propuesta: {row['questions']} {questions_label}.")
    line(f"Reuniendo provisionalmente referencias de los grupos equivalentes se obtienen {counts['proposedUnitsWithTwoOrMoreParties']} unidades con dos o más partidos, {counts['commonToAllParties']} comunes a los {len(party_names)} partidos y un máximo de {counts['maxDocumentedPartiesInOneUnit']} partidos documentados en una unidad. Son candidatas de revisión, no atribuciones nuevas aprobadas.")
    gaps = [category_names[c] for c in compiled["categoriesWithoutTwoPartyUnits"]]
    if gaps:
        line("Apartados sin una unidad provisional con dos partidos documentados: " + ", ".join(gaps) + ".")
    line("Prioridad de investigación: comparar las mismas decisiones entre programas antes de ampliar indiscriminadamente el número de preguntas. No inferir apoyo, rechazo ni neutralidad por afinidad ideológica. Una contradicción o una evidencia ambigua bloquea el valor candidato de ese partido en el grupo; no se decide por mayoría de referencias.")
    line("Escaños en Blanco conserva únicamente su artículo institucional. No forzar posiciones sectoriales para incorporarlo a una comparación general. Los documentos pertenecen a ediciones distintas y siguen sin acreditar programas de una misma convocatoria actual.")
    line()
    line("PROPUESTA DE SELECCIÓN · SIN ALGORITMO ACTIVADO")
    for i, rule in enumerate(review["selectionDesign"]["proposal"], 1):
        line(f"{i}. {rule}")
    line("Una selección uniforme sobre las formulaciones favorecería a los asuntos y documentos más desdoblados. Primero deben revisarse decisiones y presupuestos por tema; después se sortea dentro de las unidades aprobadas. El número de referencias de un partido nunca aumenta la probabilidad de una decisión ni su peso.")
    line("La semilla y la versión permitirán reproducir una selección cuando se implemente. No se recopilan respuestas, no se ejecuta ahora un sorteo y no se ha elegido una longitud por defecto. La importancia pondera la respuesta; no cambia el signo de la posición partidista ni la probabilidad del sorteo.")
    line("Una parte aleatoria adicional requiere distinguir cobertura del perfil personal y cobertura del ranking. Dos personas con selecciones distintas no han respondido necesariamente a pruebas equivalentes. No presentar porcentajes de distintos conjuntos como si compartieran denominador.")
    line(f"Se proponen además {counts['proposedSelectionFamilies']} familias para elegir, en una modalidad breve, como máximo una variante de cada debate. Abarcan {counts['questionsInSelectionFamilies']} formulaciones contando sus alias. No declaran equivalentes los distintos umbrales ni reúnen sus posiciones; son propuestas de selección, no límites activados.")
    line()
    line("DECISIONES PENDIENTES ANTES DE ACTIVAR EL SELECTOR")
    for pending in review["selectionDesign"]["pendingDecisions"]:
        line("- " + pending)
    line()
    line("APARTADOS Y CAPACIDAD DOCUMENTAL")
    line("Categoría | Formulaciones | Unidades provisionales | Con dos o más partidos")
    for c in compiled["categories"]:
        line(f"{c['title']} | {c['bankQuestions']} | {c['proposedUnits']} | {c['proposedUnitsWithTwoOrMoreParties']}")
    line(); line("FAMILIAS PROPUESTAS PARA UNA SESIÓN BREVE")
    line("Se propone una variante como máximo por familia. No se sortean aquí preguntas ni se combinan posiciones entre variantes diferentes. Los alias equivalentes se incluyen para evitar que una segunda redacción eluda el límite futuro.")
    for family in compiled["selectionFamilies"]:
        line(); line(family["id"] + " · " + family["title"])
        for qid in family["expandedQuestionIds"]:
            line("  " + qid + " · " + questions[qid]["statement"])
        line("  Criterio: " + family["rationale"])
    line()
    line("GRUPOS DE EQUIVALENCIA PROPUESTOS")
    line("El representante es un ancla de consulta, no una formulación final aprobada. No se transfiere ni reescribe ninguna posición del banco.")
    for group in compiled["equivalentGroups"]:
        line(); line(group["id"] + " · " + category_names[group["category"]])
        for qid in group["questionIds"]:
            line("  " + qid + " · " + questions[qid]["statement"])
        for party, pos in group["positions"].items():
            if not pos["sourceQuestionIds"] and not pos["ambiguousQuestionIds"]:
                continue
            value = pos["candidateValue"]
            label = "respaldo candidato +2" if value == 2 else "oposición candidata −2" if value == -2 else "sin valor candidato · " + pos["status"]
            line("  " + party_names[party] + ": " + label)
            for qid in pos["sourceQuestionIds"] + pos["ambiguousQuestionIds"]:
                for ev in questions[qid]["positions"][party]["evidence"]:
                    line("    " + qid + " · " + ev["proposalId"] + " · " + reference(ev))
        line("  Revisiones: " + ", ".join(group["reviewIds"]))
    line(); line("REGISTRO COMPLETO DE LOS PARES REVISADOS")
    for item in review["reviews"]:
        line(); line(item["id"] + " · " + RELATIONS[item["relation"]])
        for qid in item["questionIds"]:
            line("  " + qid + " · " + questions[qid]["statement"])
        line("  Criterio: " + item["rationale"])
    line(); line("LÍMITES DE ESTA PASADA")
    for limit in review["scope"]["limits"]:
        line("- " + limit)
    line("Banco de referencia, SHA-256 canónico: " + review["bankFingerprint"])
    return "\n".join(out) + "\n"
