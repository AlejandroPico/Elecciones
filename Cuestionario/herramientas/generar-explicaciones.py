"""Compile plain-language explanations without changing questions or revealing parties."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re
import unicodedata

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT / "explicaciones"


def normalize(text):
    return "".join(c for c in unicodedata.normalize("NFD", text.lower()) if not unicodedata.combining(c))


IRREGULAR = dict(item.split(":") for item in "ser:sea estar:esté haber:haya tener:tenga poder:pueda hacer:haga decir:diga ir:vaya dar:dé saber:sepa querer:quiera poner:ponga disponer:disponga proponer:proponga suponer:suponga imponer:imponga mantener:mantenga obtener:obtenga sostener:sostenga venir:venga intervenir:intervenga seguir:siga conseguir:consiga elegir:elija exigir:exija corregir:corrija dirigir:dirija proteger:proteja recoger:recoja reducir:reduzca producir:produzca introducir:introduzca conducir:conduzca establecer:establezca ofrecer:ofrezca reconocer:reconozca conocer:conozca favorecer:favorezca desaparecer:desaparezca permanecer:permanezca incluir:incluya excluir:excluya contribuir:contribuya sustituir:sustituya distribuir:distribuya atribuir:atribuya construir:construya disminuir:disminuya invertir:invierta convertir:convierta permitir:permita preferir:prefiera requerir:requiera adquirir:adquiera pedir:pida impedir:impida servir:sirva medir:mida repetir:repita ampliar:amplíe evaluar:evalúe continuar:continúe adecuar:adecúe financiar:financie reforzar:refuerce contar:cuente encontrar:encuentre recordar:recuerde renovar:renueve demostrar:demuestre fomentar:fomente crear:cree promover:promueva resolver:resuelva devolver:devuelva mover:mueva volver:vuelva facilitar:facilite prever:prevea limitar:limite aplicar:aplique garantizar:garantice pagar:pague negociar:negocie apoyar:apoye suprimir:suprima eliminar:elimine desarrollar:desarrolle flexibilizar:flexibilice priorizar:priorice perseguir:persiga afectar:afecte unificar:unifique modificar:modifique evaluar:evalúe autorizar:autorice cubrir:cubra cumplir:cumpla restituir:restituya restablecer:restablezca retirar:retire dejar:deje abandonar:abandone aprobar:apruebe comprobar:compruebe comprobarse:se_compruebe".split())


IRREGULAR.update({"revertir":"revierta","transferir":"transfiera","situar":"sitúe","restituir":"restituya","extender":"extienda","atender":"atienda","perder":"pierda","cerrar":"cierre","acordar":"acuerde","fortalecer":"fortalezca","endurecer":"endurezca","establecer":"establezca","seguir":"siga","evaluar":"evalúe","comenzar":"comience","empezar":"empiece"})

IRREGULAR.update({"salir":"salga","prohibir":"prohíba","reunir":"reúna","retribuir":"retribuya","disolver":"disuelva","referir":"refiera","diferir":"difiera","merecer":"merezca","ejercer":"ejerza","comparecer":"comparezca","proveer":"provea","satisfacer":"satisfaga","reconstruir":"reconstruya","sustituir":"sustituya","contradecir":"contradiga"})


def lower_initial(subject):
    if subject.split()[0] in {"El", "La", "Los", "Las", "Un", "Una", "Todos", "Todas", "Cada", "Cualquier", "Ninguna", "Ningún", "Ambas", "No", "En", "Dentro", "Ante", "Esa", "Ese", "Esos", "Esas", "Dicha", "Dicho", "Dichos", "Dichas"}:
        return subject[0].lower() + subject[1:]
    return subject


def subjunctive(verb, plural):
    reflexive = verb.endswith("se")
    base = verb[:-2] if reflexive else verb
    if base in IRREGULAR:
        result = IRREGULAR[base]
    elif base.endswith("car"):
        result = base[:-3] + "que"
    elif base.endswith("gar"):
        result = base[:-3] + "gue"
    elif base.endswith("zar"):
        result = base[:-3] + "ce"
    elif base.endswith("ar"):
        result = base[:-2] + "e"
    elif base.endswith(("er", "ir")):
        result = base[:-2] + "a"
    else:
        return None
    if plural:
        result += "n"
    return ("se " if reflexive else "") + result.replace("_", " ")


def plain_statement(statement):
    # Preserve exact objects, negations, numbers, scope and conditions; only expand syntax.
    match = re.match(r"^Deberían? (.*)$", statement)
    if match:
        action = match[1]
        verb, sep, tail = action.partition(" ")
        if verb.endswith("se") and verb[:-2].endswith(("ar", "er", "ir")):
            action = verb[:-2] + sep + tail
        return "Se propone " + action
    match = re.match(r"^No deberían? (.*)$", statement)
    if match:
        action = match[1]
        verb, sep, tail = action.partition(" ")
        if verb.endswith("se") and verb[:-2].endswith(("ar", "er", "ir")):
            action = verb[:-2] + sep + tail
        return "Se propone no " + action
    match = re.match(r"^(.+?) debería(n)? (\w+)(.*)$", statement)
    if match:
        subject, plural, verb, tail = match.groups()
        action = subjunctive(verb, bool(plural))
        if action:
            return "Se propone que " + lower_initial(subject) + " " + action + tail
    return "La decisión que se plantea es esta: " + lower_initial(statement)


def compile_explanations(bank, topics, rules, glossary, overrides):
    counts = Counter()
    proposals = {p["id"]:p for p in bank["proposals"]}
    outputs = {c["id"]: {} for c in bank["categories"]}
    compiled = [(r, [re.compile(p) for p in r["patterns"]]) for r in rules]
    fallbacks = []
    for q in bank["questions"]:
        text = normalize(q["statement"])
        matches = []
        for rule, patterns in compiled:
            if rule["categoryIds"] and q["category"] not in rule["categoryIds"]:
                continue
            hits = [p.pattern for p in patterns if p.search(text)]
            if hits:
                matches.append((rule["priority"] + max(len(p) for p in hits), rule))
        profile = max(matches, key=lambda pair: pair[0])[1] if matches else topics[q["category"]]
        key = profile.get("id", "tema-" + q["category"])
        counts[key] += 1
        if not matches:
            fallbacks.append(q["id"])
        terms = [g for g in glossary if re.search(r"(?<!\w)" + re.escape(normalize(g["term"])) + r"(?!\w)", text)]
        paragraphs = [plain_statement(q["statement"]), profile["background"], profile["example"], profile["distinction"]]
        percentages = re.findall(r"(\d+(?:[.,]\d+)?)\s*(?:%|por ciento)", q["statement"], re.I)
        if percentages:
            values = []
            for percentage in dict.fromkeys(percentages):
                amount = float(percentage.replace(",", ".")) * 10
                formatted = f"{amount:g}".replace(".", ",")
                values.append(f"el {percentage} % de una base ilustrativa de 1.000 unidades equivale a {formatted} unidades")
            paragraphs.append("Para entender la proporción: " + "; ".join(values) + ". Es una cuenta ilustrativa, no una nueva cifra del programa. El resultado real depende de la base nombrada en la pregunta; un porcentaje de aumento tampoco debe confundirse con puntos porcentuales.")
        if q.get("territorialScope"):
            scope = q["territorialScope"]
            paragraphs.append(f"El ámbito de esta propuesta es {scope['territory']}, en el documento autonómico de {scope['sourceElection']}. La medida se interpreta para ese territorio; no se extiende por ello a todas las comunidades ni al conjunto nacional.")
        # Only the originating proposal: other parties' opposing evidence must
        # not silently become the explanation of this exact question.
        origin = proposals[q["proposalIds"][0]]
        summary = origin["summary"].strip()
        if re.search(r"\b(?:PP|PSOE|Vox|Podemos|Sumar|PACMA|ERC|Junts|Bildu|PNV|BNG|PCTE)\b", summary):
            origin_context = None
        else:
            summary = re.sub(r"^(?:Propone|Plantea|Reitera|Defiende|Solicita)\s+", "", summary)
            origin_context = {"proposalId":origin["id"],"text":"El pasaje de origen reúne esta actuación: " + summary[0].lower()+summary[1:]}
        result = {"questionHash": hashlib.sha256(q["statement"].encode()).hexdigest(), "profile":key, "paragraphs":paragraphs,"terms":terms,"originContext":origin_context}
        if q["id"] in overrides:
            override = dict(overrides[q["id"]])
            lead = override.pop("lead", None)
            if lead:
                result["paragraphs"][0] = lead + " " + result["paragraphs"][0]
            result.update(override)
            result["profile"] = "revision-individual"
        assert len(result["paragraphs"]) >= 4
        assert len(result["paragraphs"][0]) > 15
        assert all(len(p) > 70 for p in result["paragraphs"][1:])
        assert set(re.findall(r"\d+(?:[.,]\d+)*", q["statement"])).issubset(set(re.findall(r"\d+(?:[.,]\d+)*", result["paragraphs"][0]))), q["id"]
        outputs[q["category"]][q["id"]] = result
    report = {"date":"2026-10-19","bankVersion":bank["version"],"questions":len(bank["questions"]),"categories":len(outputs),"specificProfiles":len(rules),"topicProfiles":len(topics),"glossaryTerms":len(glossary),"individualOverrides":len(overrides),"profileUse":dict(sorted(counts.items())),"topicProfileQuestionIds":fallbacks,"limits":["Explicaciones educativas de propuestas, no un catálogo de legislación vigente.","Ejemplos ilustrativos; sus cifras no crean nuevos compromisos programáticos.","Los perfiles y definiciones se combinan con el enunciado individual, conservando números, negaciones y condiciones.","Las explicaciones no puntúan ni contienen posiciones o nombres de partidos.","La revisión editorial puede ampliarse mediante excepciones por ID sin tocar el cálculo."]}
    return outputs, report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    read = lambda path: json.loads(path.read_text(encoding="utf-8"))
    bank = read(ROOT / "analisis.json")
    output, report = compile_explanations(bank, read(FOLDER/"temas.json"),read(FOLDER/"reglas.json"),read(FOLDER/"glosario.json"),read(FOLDER/"excepciones.json"))
    targets = {FOLDER/"generadas"/(category+".json"):json.dumps({"version":"1.0.0","bankVersion":bank["version"],"questions":questions},ensure_ascii=False,separators=(",",":"))+"\n" for category,questions in output.items()}
    targets[FOLDER/"revision.json"] = json.dumps(report,ensure_ascii=False,indent=2)+"\n"
    for path,content in targets.items():
        if args.check:
            assert path.read_text(encoding="utf-8")==content, "Regenerar " + str(path)
        else:
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(content,encoding="utf-8",newline="\n")
    print(f"{report['questions']} explicaciones, {report['categories']} categorías; {sum(len(s.encode()) for s in targets.values()):,} bytes. {len(report['topicProfileQuestionIds'])} usan el perfil temático con sus términos específicos.")


if __name__ == "__main__":
    main()
