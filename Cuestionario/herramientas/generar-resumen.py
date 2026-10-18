"""Validate the editorial corpus and render the unified question notebook.

Standard library only. analisis.json is the source of truth. This tool never
infers party positions and never changes the live questionnaire.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import re

from agrupacion import compile_review, render_plan

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / "Cuestionario"
PARTIES = {"pp": "PP", "psoe": "PSOE", "vox": "Vox", "erc": "ERC", "junts": "Junts", "eh-bildu": "EH Bildu", "pnv": "PNV", "bng": "BNG", "pacma": "PACMA", "registro-4086": "Escaños en Blanco", "registro-6359": "Frente Obrero", "registro-6040": "PCTE", "registro-7400": "Iustitia Europa", "registro-7458": "Se Acabó La Fiesta"}


def read(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def similarity(answers, positions, weights):
    usable = [
        (a, p, w)
        for a, p, w in zip(answers, positions, weights, strict=True)
        if a is not None and p is not None
    ]
    total = sum(w for _, _, w in usable)
    return None if not total else 100 * (1 - sum(w * abs(a - p) / 4 for a, p, w in usable) / total)


def validate(data):
    assert data["schemaVersion"] == 2
    assert data["liveEligible"] is False and data["coding"]["productionChange"] is False
    assert data["scope"]["sourceElection"] is None
    assert data["scope"]["sourceContext"] == "mixed-editions"
    assert data["scope"]["analyzedParties"] == list(PARTIES)
    assert [o["value"] for o in data["scale"]["options"]] == [-2, -1, 0, 1, 2]
    assert [o["value"] for o in data["importance"]["options"]] == [1, 2, 3]
    sources = {s["id"]: s for s in data["sources"]}
    assert len(sources) == len(PARTIES)
    for s in sources.values():
        local = (ROOT / s["file"]).resolve()
        assert local.is_relative_to(ROOT / "Elecciones"), s["file"]
        assert local.stat().st_size == s["bytes"]
        assert hashlib.sha256(local.read_bytes()).hexdigest() == s["sha256"], s["id"]
        assert s["kind"] in ("historical", "general", "permanent", "territorial") and s["scoringEligible"] is False
        if s["kind"] == "territorial":
            assert s["territory"] and s["electionScope"] == "autonomous"
            assert s["electionDate"] and "Autonómicas " in s["file"]
        if s["format"] == "PDF":
            assert s["pages"] > 0
        else:
            assert s["format"] == "TXT" and s["pages"] is None
            assert s["textLines"] == len(local.read_text(encoding="utf-8").splitlines())
        assert (s["electionDate"] == "2023-07-23") == (s["kind"] == "historical")
    units = {u["id"]: u for u in data["sourceUnits"]}
    proposals = {p["id"]: p for p in data["proposals"]}
    questions = {q["id"]: q for q in data["questions"]}
    concepts = {c["id"]: c for c in data["concepts"]}
    categories = {c["id"] for c in data["categories"]}
    for key, values in [(units, "sourceUnits"), (proposals, "proposals"), (questions, "questions"), (concepts, "concepts")]:
        assert len(key) == len(data[values]), values
    for party, expected in data["quality"]["sourceCoverage"].items():
        primary = [u for u in units.values() if u["party"] == party and u["kind"] != "editorial-passage"]
        assert sorted(u["number"] for u in primary) == list(range(1, expected + 1)), party
    for u in units.values():
        assert u["party"] in PARTIES
        assert sources[u["documentId"]]["organization"] == u["party"]
        source = sources[u["documentId"]]
        if source["format"] == "PDF":
            assert u["pdfPages"] and all(1 <= n <= source["pages"] for n in u["pdfPages"])
            assert not u.get("textLines")
        else:
            assert not u["pdfPages"] and u["textLines"]
            assert all(1 <= n <= source["textLines"] for n in u["textLines"])
    covered = set()
    for p in proposals.values():
        assert p["party"] in PARTIES and p["category"] in categories
        assert p["summary"] and p["concept"]
        assert p["reviewStatus"] == "editorial-draft"
        assert p["questionIds"] or p["coverage"] == "context-only"
        assert len(p["questionIds"]) == len(set(p["questionIds"]))
        source = sources[p["source"]["documentId"]]
        assert source["organization"] == p["party"]
        assert sorted(p["source"]["pdfPages"]) == sorted({n for uid in p["sourceUnitIds"] for n in units[uid]["pdfPages"]})
        assert sorted(p["source"].get("textLines", [])) == sorted({n for uid in p["sourceUnitIds"] for n in units[uid].get("textLines", [])})
        for uid in p["sourceUnitIds"]:
            assert units[uid]["party"] == p["party"]
            covered.add(uid)
        for qid in p["questionIds"]:
            assert p["id"] in questions[qid]["proposalIds"]
    assert covered == set(units), "Unidades documentales sin clasificación"
    assert max(Counter(" ".join(q["statement"].casefold().split()) for q in questions.values()).values()) == 1
    for q in questions.values():
        assert q["category"] in categories and q["conceptId"] in concepts
        assert q["status"] == "editorial-draft" and q["liveEligible"] is False
        assert q["axisAssignment"] is None
        assert q["statement"].endswith(".") and not re.search(r"\[(?:\?|=|-2)", q["statement"]), q["id"]
        assert set(q["positions"]) == set(PARTIES)
        assert len(q["proposalIds"]) == len(set(q["proposalIds"]))
        for pid in q["proposalIds"]:
            assert q["id"] in proposals[pid]["questionIds"]
        for party, pos in q["positions"].items():
            val = pos["proposedValue"]
            assert val in (None, -2, 2)
            assert pos["comparisonRule"] == (None if val is None else "A" if val == 2 else "B")
            assert pos["reviewStatus"] == "editorial-draft" and pos["basis"]
            assert pos["status"] == ("proposed-coding" if val is not None else "undetermined" if pos["evidence"] else "not-determined-in-corpus")
            assert bool(pos["evidence"]) or val is None
            assert {e["proposalId"] for e in pos["evidence"]} == {pid for pid in q["proposalIds"] if proposals[pid]["party"] == party}
            for ev in pos["evidence"]:
                p = proposals[ev["proposalId"]]
                assert p["party"] == party
                for k, value in p["source"].items():
                    assert ev[k] == value, (q["id"], k)
        assert q["id"] in concepts[q["conceptId"]]["questionIds"]
    for c in concepts.values():
        assert c["category"] in categories and c["questionIds"]
        assert all(questions[qid]["conceptId"] == c["id"] for qid in c["questionIds"])
    assert set(data["migration"]["preservedPpProposalIds"]) == {p["id"] for p in proposals.values() if p["party"] == "pp"}
    assert set(data["migration"]["preservedPpQuestionIds"]) == {q["id"] for q in questions.values() if q["id"].startswith("q-pp23-")}
    preserved = {
        "proposals": [{k: p[k] for k in ["id", "number", "category", "concept", "summary", "source", "editorialNotes"]} for p in data["proposals"] if p["party"] == "pp"],
        "questions": [{"id": q["id"], "statement": q["statement"], "pp": {k: v for k, v in q["positions"]["pp"].items() if k != "comparisonRule"}} for q in data["questions"] if q["id"].startswith("q-pp23-")],
    }
    assert hashlib.sha256(json.dumps(preserved, ensure_ascii=False, sort_keys=True).encode()).hexdigest() == data["migration"]["preservedPpContentSha256"], "El contenido heredado del PP requiere una migración explícita"
    # Exercise exclusion, neutrality, opposition, importance and no common evidence.
    for p in [-2, 2]:
        for a in range(-2, 3):
            assert similarity([a], [p], [1]) == 100 * (1 - abs(a - p) / 4)
    assert similarity([1, -1], [2, 2], [1, 3]) == 37.5
    assert similarity([1, -1], [2, 2], [1, 1]) == 50
    assert similarity([2, None], [2, -2], [1, 3]) == 100
    assert similarity([0, 2], [2, None], [1, 3]) == 50
    assert similarity([None], [2], [3]) is None
    assert similarity([2], [None], [3]) is None
    assert questions["q-pp23-042-a"]["positions"]["psoe"]["proposedValue"] is None
    assert questions["q-pp23-035-a"]["positions"]["psoe"]["proposedValue"] == 2
    assert questions["q-pp23-222-a"]["positions"]["pp"]["proposedValue"] == -2
    assert questions["q-pp23-222-a"]["positions"]["psoe"]["proposedValue"] == 2
    assert questions["q-pp23-222-a"]["positions"]["vox"]["proposedValue"] == -2
    assert data["surveyDesign"]["fullBankIsNotASession"] is True
    assert data["surveyDesign"]["implemented"] is False
    # An institutional single-article programme cannot acquire sectoral opinions.
    for q in questions.values():
        if q["category"] not in ("instituciones", "buen-gobierno"):
            assert q["positions"]["registro-4086"]["proposedValue"] is None
            assert not q["positions"]["registro-4086"]["evidence"]
        # A regional programme cannot silently become national evidence.
        salf = q["positions"]["registro-7458"]
        if salf["evidence"]:
            assert q["territorialScope"] == {"kind": "autonomous", "territory": "Castilla y León", "sourceElection": "2026-03-15"}
            assert all(sources[e["documentId"]]["kind"] == "territorial" for e in salf["evidence"])


def statistics(data):
    result = {"reviewedAt": data["reviewedAt"], "sourceElection": data["scope"]["sourceElection"], "sourceContext": data["scope"]["sourceContext"], "sourceDocumentIds": [s["id"] for s in data["sources"]], "surveyDesign": data["surveyDesign"], "liveEligible": False, "questions": len(data["questions"]), "concepts": len(data["concepts"]), "categories": len(data["categories"]), "proposalGroups": len(data["proposals"]), "sourceUnits": len(data["sourceUnits"]), "parties": {}, "limits": data["quality"]["limits"]}
    for party in PARTIES:
        pos = [q["positions"][party] for q in data["questions"]]
        result["parties"][party] = {"primarySourceUnits": data["quality"]["sourceCoverage"][party], "proposalGroups": sum(p["party"] == party for p in data["proposals"]), "supports": sum(p["proposedValue"] == 2 for p in pos), "opposes": sum(p["proposedValue"] == -2 for p in pos), "ambiguousEvidence": sum(p["status"] == "undetermined" for p in pos), "unlinkedDecision": sum(p["status"] == "not-determined-in-corpus" for p in pos)}
    result["questionsWithMultiplePartiesLinked"] = sum(sum(bool(p["evidence"]) for p in q["positions"].values()) >= 2 for q in data["questions"])
    result["questionsWithThreePartiesLinked"] = sum(sum(bool(p["evidence"]) for p in q["positions"].values()) >= 3 for q in data["questions"])
    result["questionsWithAllPartiesLinked"] = sum(all(p["evidence"] for p in q["positions"].values()) for q in data["questions"])
    result["byCategory"] = [{**c, "questions": sum(q["category"] == c["id"] for q in data["questions"]), "concepts": sum(k["category"] == c["id"] for k in data["concepts"])} for c in data["categories"]]
    return result


def reference(source):
    party = next(p for p in sorted(PARTIES, key=len, reverse=True) if source["documentId"].startswith(p + "-"))
    text = PARTIES[party]
    if "measure" in source:
        text += f" · medida {source['measure']}"
    text += (" · páginas PDF " + ", ".join(map(str, source["pdfPages"]))) if source["pdfPages"] else (" · líneas de la transcripción local " + ", ".join(map(str, source["textLines"])))
    if "printedPages" in source:
        text += " · impresas " + ", ".join(map(str, source["printedPages"]))
    return text


def render(data, stats):
    out = []
    def line(s=""): out.append(s)
    line(data["title"])
    line("Versión editorial " + data["version"] + " · revisión " + data["reviewedAt"])
    line("Borrador de investigación. No incorporado al cuestionario público.")
    line()
    line("ALCANCE Y LECTURA")
    line("Este documento reúne decisiones políticas por conceptos, aunque los programas las titulen de forma distinta. Cada pregunta conserva evidencia y posición de " + ", ".join(PARTIES.values()) + ". Una coincidencia temática no demuestra acuerdo sobre todos sus instrumentos, umbrales o condiciones.")
    line(data["scope"]["claim"])
    line("Frente Obrero y PCTE declaran expresamente que sus documentos no son programas electorales. El contrato de Iustitia Europa no identifica una edición electoral concreta. La fecha de descarga no demuestra fecha de publicación. El contrato de SALF es autonómico: sus posiciones no se trasladan al ámbito nacional. Estos documentos no acreditan candidaturas o leyes vigentes.")
    line("No hay un número prefijado de preguntas por tema. El catálogo es deliberadamente amplio para su revisión: no se propone que cada persona responda todo ni que cada formulación solapada sume un voto adicional.")
    line("Las categorías serán los apartados del cuestionario. En una fase posterior se agruparán formulaciones equivalentes y se diseñará una selección aleatoria equilibrada por categorías y conceptos. La longitud, los cupos y el algoritmo no están implementados. La selección deberá evitar repeticiones de una decisión y mantener cobertura comparable entre partidos.")
    line(f"Inventario: {stats['questions']} preguntas únicas en {stats['concepts']} conceptos y {stats['categories']} categorías; {stats['proposalGroups']} agrupaciones documentales.")
    for party, label in PARTIES.items():
        s = stats["parties"][party]
        line(f"{label}: {s['primarySourceUnits']} unidades primarias; {s['supports']} respaldos propuestos, {s['opposes']} oposiciones y {s['ambiguousEvidence']} atribuciones ambiguas. {s['unlinkedDecision']} decisiones del conjunto sin vínculo documental suficiente para este partido.")
    line("PP y Vox numeran medidas: 365 y 381 respectivamente. El PSOE no usa esa numeración: S0001–S1191 son anclas editoriales de viñetas, NO 1191 medidas oficiales. Hay además pasajes por página para propuestas que usan otras viñetas o párrafos. Pueden solaparse; no sumarlos como promesas independientes.")
    line("ERC, Junts, EH Bildu, PNV y BNG usan aquí anclas por página física (132, 151, 16, 52 y 68 páginas). No son recuentos de medidas ni promesas oficiales. ERC distingue horizontes estratégicos de propuestas a las Cortes; se han priorizado sus apartados operativos. EH Bildu es un compromiso de extensión menor. Las páginas introductorias quedan clasificadas como contexto.")
    line("PACMA y Frente Obrero se inventarían por sus 76 y 64 páginas físicas, respectivamente. Escaños en Blanco se inventaría mediante un único artículo en la línea 6 de su transcripción HTML local. No se inventan páginas PDF para ese texto ni posiciones sectoriales que no contiene. Su renuncia a cobrar subvenciones propias no implica prohibir la financiación de los demás partidos.")
    line("PCTE, Iustitia Europa y SALF se inventarían por sus 24, 28 y 22 páginas físicas. SALF corresponde exclusivamente a Castilla y León, 15 de marzo de 2026. No se localizó un programa nacional en la revisión del 18 de octubre: se mantiene pendiente, sin presentar el documento regional como sustituto. Los referendos de Iustitia Europa no acreditan por sí solos apoyo a abandonar UE u OTAN; las terapias naturales se describen como propuesta política, sin validar su eficacia clínica.")
    line("Cobertura significa que cada unidad del inventario tiene una clasificación y referencias. No garantiza que todas las subcláusulas estén desdobladas ni que este borrador sea ya un cuestionario validado.")
    line("Los originales del PSOE, Vox y Junts se conservan como copias de archivo de prensa, identificadas por huella y procedencia; no se presentan como descargas actuales de sus servidores oficiales.")
    line()
    line("ESCALA, IMPORTANCIA Y CÁLCULO")
    line("Respuesta: muy en desacuerdo −2; en desacuerdo −1; neutral 0; de acuerdo +1; muy de acuerdo +2. No lo sé y prefiero omitir no tienen valor numérico ni participan en la suma.")
    line("Importancia: normal 1 (por defecto), alta 2, esencial 3. Multiplica el peso de la pregunta, no la posición del partido ni el signo de la respuesta.")
    line("Posiciones editoriales: RESPALDA +2, SE OPONE −2, SIN DETERMINAR sin valor. Los extremos representan respaldo u oposición a la decisión exacta, no radicalidad ni entusiasmo. No se inventan valores intermedios por el tono de un texto.")
    line("Cada pregunta muestra la comparación y las páginas de evidencia. El apartado final INVENTARIO Y NOTAS DE PROPUESTAS contiene el resumen propio y las reservas de cada identificador citado. Así no se repite el mismo resumen en todas las preguntas que proceden de una medida.")
    line("Sin determinar puede significar evidencia ambigua, una revisión anunciada sin resultado, diferencias de alcance o ausencia de vínculo suficiente. Nunca significa neutralidad, oposición ni prueba de que el partido carezca de postura.")
    line("Coincidencia por pregunta = 100 × (1 − |respuesta − posición| / 4).")
    line("Coincidencia con un partido = 100 × [1 − Σ(peso × |respuesta − posición| / 4) / Σ(peso)]. Solo se incluyen respuestas numéricas con posición documental aprobada. Si no hay denominador, no se publica porcentaje.")
    line("                  Respuesta:     −2     −1      0     +1     +2")
    line("Regla A, partido +2:              0%    25%    50%    75%   100%")
    line("Regla B, partido −2:            100%    75%    50%    25%     0%")
    line("Ejemplo: ante una misma afirmación, marcar +2 da 100% de coincidencia con quien la respalda y 0% con quien se opone. Si otro partido no tiene evidencia suficiente, no recibe ni 0% ni 50%: queda fuera de esa comparación.")
    line("Ejemplo de importancia: dos coincidencias de 75% y 25% producen 50% con pesos 1 y 1. Con pesos 1 y 3 producen (75×1 + 25×3)/4 = 37,5%. El efecto de cada respuesta queda así trazable.")
    line("Comparación justa: mostrar cobertura por partido y calcular sobre un conjunto común de preguntas acreditadas para los partidos comparados, o presentar resultados de cobertura diferente sin un ranking equiparable. La falta de evidencia no puede favorecer una clasificación artificial.")
    line("Antes de producción, seleccionar una pregunta por decisión o fijar un presupuesto de peso por familia de solapamiento. Las repeticiones en capítulos y las medidas que citan una misma pregunta no aumentan su peso. Los grupos actuales son avisos de revisión, no una corrección ya aplicada.")
    line("La vista previa Coordenadas políticas utiliza una selección explícita de decisiones en ejes.json, con signos y pesos iguales por indicador. Es independiente de la fórmula de afinidad y del cuestionario vigente. axisAssignment del banco permanece vacío. Las ausencias no son centro ideológico; se muestran cobertura e intervalos de datos faltantes, no incertidumbre estadística.")
    line()
    line("FUENTES CONSERVADAS")
    for s in data["sources"]:
        line(s["title"])
        line("  Archivo del repositorio: " + s["file"])
        line("  Referencia del partido: " + s["source"])
        line("  Descarga archivada: " + s["downloadedFrom"])
        line("  SHA-256: " + s["sha256"])
        line("  Alcance: " + s["kind"] + (" · " + s["territory"] if s.get("territory") else "") + (" · " + s["electionDate"] if s.get("electionDate") else ""))
        line("  Nota: " + s["note"])
    line("Las páginas PDF son posiciones físicas, empezando por 1. El desfase de la numeración impresa del PSOE varía; por eso se usa la página PDF y no una resta fija. En el PP se conserva además la paginación impresa del análisis original. Las líneas TXT son posiciones físicas del archivo conservado, con sus cabeceras y líneas vacías, no números de artículo oficiales.")
    line()
    line("ÍNDICE DE CONCEPTOS")
    catnames = {c["id"]: c["title"] for c in data["categories"]}
    for c in data["concepts"]:
        line(f"  {c['id']} · {catnames[c['category']]} / {c['title']} · {len(c['questionIds'])} preguntas")
    questions = {q["id"]: q for q in data["questions"]}
    proposals = {p["id"]: p for p in data["proposals"]}
    for c in data["concepts"]:
        line(); line("=" * 78)
        line(catnames[c["category"]].upper() + " / " + c["title"].upper())
        line("Concepto " + c["id"])
        if c.get("aliases"): line("Términos reunidos: " + "; ".join(c["aliases"]) + ".")
        for qid in c["questionIds"]:
            q = questions[qid]
            line(); line(qid + " · " + q["statement"])
            for party, label in PARTIES.items():
                pos = q["positions"][party]
                value = pos["proposedValue"]
                code = "RESPALDA (+2; regla A)" if value == 2 else "SE OPONE (−2; regla B)" if value == -2 else "SIN DETERMINAR (sin puntuación)"
                line("  " + label + ": " + code)
                for ev in pos["evidence"]:
                    p = proposals[ev["proposalId"]]
                    line("    " + p["id"] + " · " + reference(ev))
                if value is None and pos["evidence"]:
                    line("    Criterio: " + pos["basis"])
    line(); line("=" * 78); line("INVENTARIO Y NOTAS DE PROPUESTAS")
    line("Este índice conserva cada agrupación, su localización y sus reservas. Las propuestas sin pregunta son contexto o balance; no se han convertido automáticamente en una posición puntuable.")
    for p in data["proposals"]:
        line(); line(p["id"] + " · " + PARTIES[p["party"]] + " · " + p["concept"])
        line("  " + p["summary"])
        line("  " + reference(p["source"]))
        line("  Unidades: " + ", ".join(p["sourceUnitIds"]))
        line("  Preguntas: " + (", ".join(p["questionIds"]) or "Ninguna: contexto o balance"))
        if p["editorialNotes"]: line("  Reserva editorial: " + p["editorialNotes"])
    line(); line("CONCEPTOS RESERVADOS DEL ANÁLISIS PREVIO")
    for p in data["pendingConcepts"]:
        line(p["concept"] + ": " + p["reason"])
    line("Se conservan para trazabilidad. Los nuevos conceptos relacionados no trasladan al PP una posición que su fuente no determine.")
    line(); line("REVISIÓN ANTES DEL CUESTIONARIO")
    for item in data["quality"]["requiredBeforeLive"]: line("- " + item)
    line("- Contrastar atribuciones entre programas y actualizar por convocatoria; no publicar estos antecedentes como programas actuales.")
    line("- Revisar neutralidad, formulaciones inversas, contexto explicativo, negaciones, edades, cifras y condiciones.")
    line("- Auditar solapamientos y equilibrio de selección, fijar ejes y mostrar al usuario evidencia, cobertura y contribución ponderada de cada respuesta.")
    return "\n".join(out) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = read(FOLDER / "analisis.json")
    validate(data)
    stats = statistics(data)
    grouping = read(FOLDER / "agrupacion.json")
    grouping_summary = compile_review(data, grouping)
    stats["groupingReview"] = grouping_summary["counts"]
    selection_report = render_plan(data, grouping, grouping_summary, PARTIES, reference)
    axes = read(FOLDER / "ejes.json")
    questions = {q["id"]: q for q in data["questions"]}
    selected = set()
    assert axes["sourceElection"] == data["scope"]["sourceElection"]
    assert axes["status"] == "editorial-preview" and axes["notAnAffinityRanking"]
    assert len({c["id"] for c in axes["charts"]}) == len(axes["charts"])
    for chart in axes["charts"]:
        for axis in [chart["x"], chart["y"]]:
            seen = set()
            for indicator in axis["indicators"]:
                assert indicator["direction"] in [-1, 1]
                for qid in indicator["questionIds"]:
                    assert qid in questions and qid not in seen, (chart["id"], qid)
                    assert not questions[qid].get("territorialScope"), "No mezclar decisiones autonómicas con los ejes generales"
                    selected.add(qid)
                    seen.add(qid)
    preview = {
        "version": data["version"], "sourceElection": data["scope"]["sourceElection"], "sourceContext": data["scope"]["sourceContext"],
        "reviewedAt": data["reviewedAt"], "parties": [{"id": k, "name": v} for k, v in PARTIES.items()],
        "counts": {k: stats[k] for k in ["questions", "concepts", "categories", "proposalGroups", "sourceUnits"]},
        "sources": [{k: s.get(k) for k in ["id", "organization", "title", "file", "source", "sourceKind", "sha256", "pages", "textLines", "format", "kind", "electionDate", "territory", "electionScope"]} for s in data["sources"]],
        "questions": [{"id": q["id"], "statement": q["statement"], "category": q["category"], "positions": {party: {"value": pos["proposedValue"], "basis": pos["basis"], "evidence": pos["evidence"]} for party, pos in q["positions"].items()}} for q in data["questions"] if q["id"] in selected],
        "categories": stats["byCategory"],
    }
    category_report = ["Resumen de categorías · antecedentes electorales y documentos generales y permanentes", f"{stats['questions']} formulaciones de borrador · {stats['concepts']} conceptos · {stats['categories']} categorías", "", "Categoría | Formulaciones | Conceptos"]
    category_report += [f"{c['title']} | {c['questions']} | {c['concepts']}" for c in stats["byCategory"]]
    category_report += ["", "El recuento es de formulaciones, no de decisiones independientes ni de preguntas que una persona deba responder seguidas.", "Las categorías serán los apartados del cuestionario. Se prevé reducir formulaciones y seleccionar preguntas de forma aleatoria equilibrada por temas y conceptos, evitando repeticiones. Aún no se ha implementado el algoritmo ni fijado la longitud.", "Antes del test definitivo se revisarán solapamientos, neutralidad, contexto y cobertura comparable.", "", f"{len(PARTIES)} documentos de origen · {stats['proposalGroups']} grupos de propuestas · {stats['sourceUnits']} unidades documentales de referencia.", "Las unidades mezclan medidas oficiales numeradas, viñetas, páginas PDF y un artículo de texto. No son una métrica comparable de promesas entre partidos.", "Importancia del futuro test: normal 1, alta 2, esencial 3. No lo sé y omitir se excluyen.", f"La vista Coordenadas políticas contiene {len(axes['charts'])} agrupaciones gráficas de una selección publicada de indicadores. No sustituye las {stats['categories']} categorías de este inventario."]
    outputs = {
        FOLDER / "Resumen Preguntas.txt": render(data, stats) + "\n" + selection_report,
        FOLDER / "cobertura.json": json.dumps(stats, ensure_ascii=False, indent=2) + "\n",
        FOLDER / "Resumen Categorías.txt": "\n".join(category_report) + "\n",
        FOLDER / "coordenadas.json": json.dumps(preview, ensure_ascii=False, indent=2) + "\n",
        FOLDER / "Plan de selección.txt": selection_report,
        FOLDER / "agrupacion-cobertura.json": json.dumps(grouping_summary, ensure_ascii=False, indent=2) + "\n",
    }
    for path, content in outputs.items():
        if args.check:
            assert path.read_text(encoding="utf-8") == content, "Regenerar " + str(path)
        else:
            path.write_text(content, encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("Validación correcta" if args.check else "Documento y cobertura generados")


if __name__ == "__main__":
    main()
