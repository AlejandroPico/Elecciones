"""Generate the compact, traceable experimental questionnaire; never edit its output."""
import argparse
import json
from pathlib import Path

from agrupacion import compile_review, fingerprint
from importlib import import_module

ROOT = Path(__file__).resolve().parents[1]


def compile_bank(bank, review, config, axes):
    assert config["bankVersion"] == bank["version"]
    assert config["questionsPerCategory"] == 10
    assert config["status"] == "experimental-documentary-survey"
    categories = {c["id"] for c in bank["categories"]}
    grouped = [cid for g in config["groups"] for cid in g["categoryIds"]]
    assert len(grouped) == len(set(grouped)) and set(grouped) == categories
    grouping = compile_review(bank, review)
    keys = {qid: u["id"] for u in grouping["equivalentGroups"] for qid in u["questionIds"]}
    keys.update({qid: f["id"] for f in grouping["selectionFamilies"] for qid in f["expandedQuestionIds"]})
    parties = import_module("generar-resumen").PARTIES
    questions = []
    for q in bank["questions"]:
        assert q["scale"] == "agreement-five"
        positions = {}
        for party, p in q["positions"].items():
            # Preserve ambiguous evidence without assigning it a neutral value.
            if p["proposedValue"] is not None or p["evidence"]:
                positions[party] = {
                    "value": p["proposedValue"], "basis": p["basis"],
                    "evidence": [{k: v for k, v in e.items() if k in ["proposalId", "documentId", "pdfPages", "textLines", "measure"]} for e in p["evidence"]],
                }
        questions.append({
            "id": q["id"], "category": q["category"], "concept": q["concept"],
            "text": q["statement"], "selectionKey": keys.get(q["id"], q["id"]),
            "scope": q.get("territorialScope"), "positions": positions,
        })
    assert len({q["id"] for q in questions}) == len(questions)
    for cid in categories:
        assert len({q["selectionKey"] for q in questions if q["category"] == cid}) >= 10
    return {
        "version": config["version"], "bankVersion": bank["version"],
        "bankFingerprint": fingerprint(bank), "status": config["status"],
        "categories": bank["categories"], "groups": config["groups"],
        "parties": [{"id": p, "name": n} for p, n in parties.items()],
        "sources": [{k: s.get(k) for k in ["id", "title", "file", "source", "kind", "territory", "electionDate", "organization"]} for s in bank["sources"]],
        "questions": questions, "maps": axes["charts"],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    read = lambda name: json.loads((ROOT / name).read_text(encoding="utf-8"))
    result = compile_bank(read("analisis.json"), read("agrupacion.json"), read("sesiones.json"), read("ejes.json"))
    output = json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n"
    target = ROOT / "sesiones-banco.json"
    if args.check:
        assert target.read_text(encoding="utf-8") == output, "Regenerar sesiones-banco.json"
    else:
        target.write_text(output, encoding="utf-8", newline="\n")
    print(f"{len(result['questions'])} preguntas · {len(result['categories'])} categorías · {len(output.encode('utf-8')):,} bytes")


if __name__ == "__main__":
    main()
