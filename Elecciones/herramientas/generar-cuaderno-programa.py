"""Validate an editorial programme analysis and regenerate its readable notebook.

Standard library only. The JSON is the editorial source of truth. This tool does
not extract policy positions or modify the live questionnaire.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "Elecciones/Generales Julio 2023/analisis/pp/analisis.json"


def read(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def validate(data: dict) -> None:
    assert data["schemaVersion"] == 1
    assert data["liveEligible"] is False
    assert data["coding"]["productionChange"] is False
    assert [x["value"] for x in data["scale"]["options"]] == [-2, -1, 0, 1, 2]
    assert [x["value"] for x in data["importance"]["options"]] == [1, 2, 3]
    categories = {x["id"] for x in data["categories"]}
    sources = {s["id"]: s for s in data["sources"]}
    assert len(categories) == len(data["categories"])
    assert len(sources) == len(data["sources"])
    for source in sources.values():
        local = (ROOT / "Elecciones" / source["file"]).resolve()
        assert local.is_relative_to((ROOT / "Elecciones").resolve())
        assert hashlib.sha256(local.read_bytes()).hexdigest() == source["sha256"]
        assert source["kind"] == "historical"
        assert source["scoringEligible"] is False
    proposals = {p["id"]: p for p in data["proposals"]}
    questions = {q["id"]: q for q in data["questions"]}
    assert len(proposals) == len(data["proposals"])
    assert len(questions) == len(data["questions"])
    assert len(proposals) == data["quality"]["expectedMeasures"]
    assert sorted(p["number"] for p in proposals.values()) == list(
        range(1, data["quality"]["expectedMeasures"] + 1)
    )
    statements = Counter(q["statement"].casefold().strip() for q in questions.values())
    assert max(statements.values()) == 1, "Pregunta literal duplicada"
    for p in proposals.values():
        assert p["category"] in categories
        assert p["concept"] and p["summary"] and p["questionIds"]
        assert len(p["questionIds"]) == len(set(p["questionIds"]))
        assert p["reviewStatus"] == "editorial-draft"
        source = sources[p["source"]["documentId"]]
        assert p["source"]["measure"] == p["number"]
        assert all(1 <= n <= source["pages"] for n in p["source"]["pdfPages"])
        assert p["source"]["printedPages"] == [n - 2 for n in p["source"]["pdfPages"]]
        for qid in p["questionIds"]:
            assert p["id"] in questions[qid]["proposalIds"]
    for q in questions.values():
        assert q["category"] in categories
        assert q["status"] == "editorial-draft" and q["liveEligible"] is False
        assert q["axisAssignment"] is None
        assert not re.search(r"\[(?:\?|=|-2)\]", q["statement"])
        assert q["statement"].endswith("."), q["id"]
        for pid in q["proposalIds"]:
            assert q["id"] in proposals[pid]["questionIds"]
        assert set(q["positions"]) <= set(data["scope"]["analyzedParties"])
        for party, position in q["positions"].items():
            value = position["proposedValue"]
            assert value is None or value in [-2, -1, 0, 1, 2]
            assert position["reviewStatus"] == "editorial-draft"
            assert bool(position["evidence"])
            assert {e["proposalId"] for e in position["evidence"]} == set(q["proposalIds"])
            for evidence in position["evidence"]:
                p = proposals[evidence["proposalId"]]
                for key in ["documentId", "measure", "pdfPages", "printedPages"]:
                    assert evidence[key] == p["source"][key], (q["id"], key)
            assert (value is None) == (position["status"] == "undetermined")
            assert q["comparisonRule"] == (None if value is None else "A" if value == 2 else "B")
    # Verify the published examples instead of merely mirroring serialized values.
    for name, party_value in [("ruleA", 2), ("ruleB", -2)]:
        for answer in range(-2, 3):
            percent = 100 * (1 - abs(answer - party_value) / 4)
            assert data["coding"][name]["agreementByAnswer"][str(answer)] == percent
    assert (75 * 1 + 25 * 3) / 4 == 37.5
    assert (75 * 1 + 25 * 1) / 2 == 50


def statistics(data: dict) -> dict:
    questions = data["questions"]
    return {
        "reviewedAt": data["reviewedAt"],
        "sourceElection": data["scope"]["sourceElection"],
        "numberedMeasures": len(data["proposals"]),
        "expectedMeasures": data["quality"]["expectedMeasures"],
        "missingMeasures": [],
        "categories": len(data["categories"]),
        "uniqueDraftQuestions": len(questions),
        "proposedSupportCodings": sum(q["comparisonRule"] == "A" for q in questions),
        "proposedOppositionCodings": sum(q["comparisonRule"] == "B" for q in questions),
        "undeterminedCodings": sum(q["comparisonRule"] is None for q in questions),
        "sharedQuestions": sum(len(q["proposalIds"]) > 1 for q in questions),
        "supplementaryUnattributedConcepts": len(data["pendingConcepts"]),
        "liveEligibleQuestions": 0,
        "independentValidation": False,
        "coverageUnit": data["quality"]["coverageUnit"],
        "coverageLimit": data["quality"]["coverageLimit"],
    }


def render(data: dict) -> str:
    stats = statistics(data)
    source = data["sources"][0]
    questions = {q["id"]: q for q in data["questions"]}
    lines = []

    def add(*items: str) -> None:
        for item in items:
            lines.extend([item, ""])

    add(
        "# Propuestas del Partido Popular y preguntas para su comparación",
        "Cuaderno de investigación de Elecciones · Primera versión editorial · 18 de octubre de 2026",
        "Este documento recoge las 365 medidas numeradas del programa del Partido Popular para las elecciones generales del 23 de julio de 2023. Propone preguntas para comparar decisiones políticas y explica qué respuestas coincidirían con ese texto. Es material de revisión: no se ha incorporado al cuestionario público.",
        "La fuente es un antecedente de 2023, no un programa acreditado para noviembre de 2026. Se conserva la fecha de descarga separada de la convocatoria. No se ha evaluado aquí si las promesas se ejecutaron ni si describen la legislación vigente.",
        f"El inventario contiene {stats['categories']} categorías y {stats['uniqueDraftQuestions']} borradores únicos de preguntas. Hay {stats['undeterminedCodings']} preguntas sin posición numérica suficientemente determinada y {stats['supplementaryUnattributedConcepts']} conceptos adicionales reservados. Las posiciones de PSOE, Vox y Podemos quedan pendientes de estudiar; no se les asigna un cero ni una oposición por ausencia de análisis.",
        "Se ha registrado cada medida numerada. Algunas agrupan varias decisiones y se desdoblan; otras repiten propuestas y comparten pregunta. Esta cobertura documental no certifica que cada subcláusula esté ya traducida a una pregunta final independiente. Los objetivos generales y aspectos no concretados se conservan en resúmenes y notas.",
        "## Cómo leer las fichas",
        "Cada ficha identifica la medida original, sus páginas impresas y sus páginas del archivo PDF, un resumen redactado para este cuaderno y las preguntas propuestas. La página del PDF es la que muestra el visor al contar desde la portada. En esta edición, la página impresa corresponde a la página del PDF menos dos.",
        "Los identificadores M001 a M365 corresponden a la numeración del programa. Los identificadores de preguntas son estables: q-pp23-129-a, por ejemplo, nació al analizar la medida 129. Su origen no la hace exclusiva del PP: cuando se estudie otro partido se añadirá su evidencia a la misma pregunta si coincide exactamente el concepto y el alcance.",
        "Cada afirmación se presenta al lector precedida por «Indique su grado de acuerdo con esta propuesta». Se evita preguntar por simpatía hacia un partido. Una pregunta sobre consentimiento de menores para abortar no se interpreta como una respuesta sobre todo el régimen del aborto.",
        "## Escala de respuesta e importancia",
        "La escala es la misma para todas las preguntas. La importancia se elige por separado y, por defecto, es normal.",
        "| Respuesta | Valor |\n| --- | ---: |\n| Muy en desacuerdo | -2 |\n| En desacuerdo | -1 |\n| Neutral | 0 |\n| De acuerdo | +1 |\n| Muy de acuerdo | +2 |\n| No lo sé o prefiero omitir | Sin valor |",
        "| Importancia | Peso |\n| --- | ---: |\n| Normal | 1 |\n| Alta | 2 |\n| Esencial | 3 |",
        "Neutral es una respuesta numérica intermedia. «No lo sé» y «Prefiero omitir» quedan fuera tanto del numerador como del denominador. No deben contarse como desacuerdo, indiferencia ni una respuesta neutral. La importancia de una respuesta omitida tampoco añade peso.",
        "## Qué significa la posición atribuida al PP",
        "Las fichas muestran una propuesta de codificación editorial, no una puntuación aprobada para producción. +2 significa que el programa respalda la opción concreta enunciada; -2, que propone la opción contraria. Los extremos no miden entusiasmo, radicalidad ni frecuencia de adjetivos. No se asigna +1 o -1 porque el lenguaje parezca moderado. Para usar niveles intermedios habría que definir primero alternativas y umbrales comprobables.",
        "Cuando el texto solo promete estudiar una medida, revisar una ley sin precisar el cambio o conseguir un resultado sin instrumento suficiente, se indica «Sin determinar». No se transforma el silencio en neutralidad. Una condición expresa se conserva dentro de la pregunta: apoyar prolongar centrales con autorización de seguridad no equivale a apoyarlo sin esa condición.",
        f"En esta versión hay {stats['proposedSupportCodings']} codificaciones propuestas de respaldo, {stats['proposedOppositionCodings']} de oposición y {stats['undeterminedCodings']} sin determinar. La abundancia de respaldos se debe a que las preguntas se han extraído primero de propuestas del propio PP. No demuestra superioridad del partido ni convierte este banco en una muestra equilibrada de toda la política. La selección final requiere analizar otros programas.",
        "## Qué respuestas aumentan la coincidencia",
        "La coincidencia describe cercanía a la posición documentada sobre una propuesta. No concede beneficios electorales, no mide quién gobierna mejor y no recomienda un voto. Las reglas A y B de esta tabla permiten leer todas las fichas sin repetir la misma tabla en cada una.",
        "| Respuesta del usuario | Regla A PP +2 | Regla B PP -2 |\n| --- | ---: | ---: |\n| Muy en desacuerdo -2 | 0 % | 100 % |\n| En desacuerdo -1 | 25 % | 75 % |\n| Neutral 0 | 50 % | 50 % |\n| De acuerdo +1 | 75 % | 25 % |\n| Muy de acuerdo +2 | 100 % | 0 % |",
        "Si una pregunta muestra «PP +2 · Regla A», estar más de acuerdo aumenta la coincidencia con esa propuesta del PP. Si muestra «PP -2 · Regla B», estar más en desacuerdo aumenta la coincidencia. «Sin determinar» no aporta coincidencia al cálculo.",
        "Para cada pregunta comparable se calcula la distancia absoluta entre la respuesta del usuario y la posición del partido, dividida entre cuatro. La coincidencia es cien veces uno menos la media de esas distancias, ponderada por la importancia. Solo se utilizan preguntas respondidas con una posición partidista respaldada y aprobada.",
        "En notación textual: coincidencia = 100 × [1 − suma(peso × distancia absoluta / 4) / suma(pesos)]. Si no hay ninguna pregunta comparable, el resultado es «sin base suficiente», no cero por ciento.",
        "Ejemplo con dos preguntas de regla A: en una se responde «de acuerdo» con importancia normal, y en otra «en desacuerdo» con importancia esencial. Las coincidencias son 75 % y 25 %. El resultado es (75 × 1 + 25 × 3) / (1 + 3) = 37,5 %. Si ambas fueran normales sería 50 %. Cambiar la importancia no cambia la coincidencia de una única pregunta aislada: cambia su influencia relativa en el conjunto.",
        "Las coordenadas ideológicas son un cálculo distinto de la coincidencia con un partido. Este cuaderno no asigna ejes, direcciones ni etiquetas ideológicas. Ninguna pregunta modifica todavía las coordenadas del cuestionario público. Antes de hacerlo habrá que justificar qué concepto mide cada eje y revisar cómo se combinan las preguntas relacionadas.",
        "## Cobertura y preguntas repetidas",
        f"Hay {stats['sharedQuestions']} preguntas compartidas por varias medidas. Se contestarán una sola vez si se incorporan al banco. Otras preguntas próximas están marcadas con un grupo de selección para revisar su solapamiento. Una propuesta que ocupa más páginas no debería pesar más solo por su extensión.",
        "La fórmula anterior explica el cálculo actual por pregunta; no corrige por sí sola la acumulación de asuntos semejantes. Antes de usar este inventario se deberá seleccionar una pregunta por decisión redundante o definir y publicar un presupuesto de peso por concepto. No se ha aplicado un corrector oculto.",
        "Al comparar partidos se deberá mostrar cuántas respuestas tienen evidencia común y cuánto peso representan. Un partido con pocas posiciones conocidas no puede presentarse como mejor coincidencia sin advertir esa menor cobertura. Para una clasificación comparable conviene ofrecer también el resultado sobre un subconjunto común de preguntas.",
        "## Índice de categorías",
    )
    for c in data["categories"]:
        ps = [p for p in data["proposals"] if p["category"] == c["id"]]
        qs = [q for q in data["questions"] if q["category"] == c["id"]]
        add(f"- {c['title']}: {len(ps)} medidas y {len(qs)} preguntas de origen.")
    for c in data["categories"]:
        add("## " + c["title"])
        for p in [p for p in data["proposals"] if p["category"] == c["id"]]:
            printed = ", ".join(map(str, p["source"]["printedPages"]))
            pdf = ", ".join(map(str, p["source"]["pdfPages"]))
            add(f"### M{p['number']:03} {p['concept']}",
                f"Fuente: medida {p['number']}. Páginas impresas {printed}; páginas del PDF {pdf}.",
                "Propuesta del PP: " + p["summary"])
            for qid in p["questionIds"]:
                q = questions[qid]
                pos = q["positions"]["pp"]
                value = pos["proposedValue"]
                label = "Sin determinar · No entra en el cálculo" if value is None else (
                    "PP +2 · Regla A" if value == 2 else "PP -2 · Regla B")
                shared = " · Pregunta compartida entre medidas" if len(q["proposalIds"]) > 1 else ""
                add(f"**{qid}** · {label}{shared}", q["statement"])
                if value is None and pos["basis"] != p["editorialNotes"]:
                    add("Motivo de reserva: " + pos["basis"])
            if p["editorialNotes"]:
                add("Límites de lectura: " + p["editorialNotes"])
    add("## Conceptos reservados sin atribución al PP",
        "Estos conceptos ayudan a preparar la comparación posterior. No son propuestas adicionales atribuidas al PP y no se suman al número de preguntas del inventario.")
    for gap in data["pendingConcepts"]:
        add("### " + gap["concept"], "Borrador para estudio: " + gap["statement"],
            "Posición del PP: sin determinar. " + gap["reason"], gap["use"])
    add("## Revisión necesaria antes del cuestionario")
    for item in data["quality"]["requiredBeforeLive"]:
        add("- " + item)
    add(
        "La primera lectura y la redacción se han realizado con asistencia automatizada. No hay revisión independiente de personas expertas ni prueba de comprensión con usuarios. Conviene revisar especialmente aborto, eutanasia, derechos trans, consentimiento y datos, sanciones penales y requisitos de elegibilidad por sus matices y efectos.",
        "La próxima incorporación puede estudiar el PSOE manteniendo los conceptos e identificadores existentes. Se añadirán sus propuestas y fuentes por pregunta, se crearán preguntas nuevas cuando cambie el instrumento o el alcance, y se añadirán categorías si aparecen asuntos no cubiertos. No se deben forzar posiciones diferentes dentro de un enunciado que no permita distinguirlas.",
        "## Fuente original y archivos de trabajo",
        "Partido Popular. Programa electoral para las elecciones generales del 23 de julio de 2023. Edición titulada Un proyecto al servicio de un gran país. 365 medidas. 112 páginas de archivo PDF.",
        "Servidor oficial: " + source["source"],
        "Copia local en el repositorio: Elecciones/" + source["file"],
        "Fecha de descarga: " + source["retrievedAt"] + ". Fecha exacta de publicación no acreditada en los metadatos conservados.",
        "Huella SHA256 del original: " + source["sha256"],
        "El archivo analisis.json es la base editorial. El cuaderno en texto y Markdown y cobertura.json se regeneran desde él con Elecciones/herramientas/generar-cuaderno-programa.py. Los resúmenes son paráfrasis; para una comprobación literal debe consultarse la medida y página del PDF original. No se sustituye el programa por este análisis.",
    )
    return "\n".join(lines).rstrip() + "\n"


def outputs(data: dict) -> dict[str, str]:
    markdown = render(data)
    plain = re.sub(r"(?m)^#{1,3} ", "", markdown).replace("**", "")
    return {
        "cuaderno-pp-2023.md": markdown,
        "cuaderno-pp-2023.txt": plain,
        "cobertura.json": json.dumps(statistics(data), ensure_ascii=False, indent=2) + "\n",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", type=Path, nargs="?", default=DEFAULT)
    parser.add_argument("--check", action="store_true", help="Check without changing files")
    args = parser.parse_args()
    data = read(args.path)
    validate(data)
    for name, content in outputs(data).items():
        path = args.path.parent / name
        if args.check:
            assert path.read_text(encoding="utf-8") == content, f"Desactualizado: {path}"
        else:
            path.write_text(content, encoding="utf-8")
    print(json.dumps(statistics(data), ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, KeyError, ValueError) as error:
        print(f"Error de validación: {error}", file=sys.stderr)
        raise SystemExit(1)
