import hashlib
import importlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
editor = importlib.import_module("generar-explicaciones")


class Explanations(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads((ROOT/"analisis.json").read_text(encoding="utf-8"))
        cls.actual = {}
        for file in (ROOT/"explicaciones/generadas").glob("*.json"):
            cls.actual.update(json.loads(file.read_text(encoding="utf-8"))["questions"])

    def test_every_question_has_complete_context_without_changing_scope(self):
        self.assertEqual(set(self.actual), {q["id"] for q in self.bank["questions"]})
        self.assertEqual(len(self.actual), 5861)
        for q in self.bank["questions"]:
            content = self.actual[q["id"]]
            self.assertEqual(content["questionHash"], hashlib.sha256(q["statement"].encode()).hexdigest())
            self.assertGreaterEqual(len(content["paragraphs"]),4)
            self.assertGreater(sum(map(len,content["paragraphs"][1:4])),400)
            self.assertTrue(set(re.findall(r"\d+(?:[.,]\d+)*",q["statement"])).issubset(set(re.findall(r"\d+(?:[.,]\d+)*",content["paragraphs"][0]))))
            for token in ["no","sin","salvo"]:
                self.assertGreaterEqual(len(re.findall(r"\b"+token+r"\b",content["paragraphs"][0],re.I)),len(re.findall(r"\b"+token+r"\b",q["statement"],re.I)),q["id"])
            text=" ".join(content["paragraphs"])
            self.assertNotIn("Valora la propuesta concreta",text)
            self.assertNotIn("Las atribuciones a partidos",text)
            if q.get("territorialScope"):
                self.assertIn(q["territorialScope"]["territory"],text)
            if content.get("originContext"):
                self.assertEqual(content["originContext"]["proposalId"],q["proposalIds"][0])

    def test_dangling_references_have_specific_antecedents(self):
        examples={"q-pp23-348-b":"dos por ciento cultural","q-registro-6779-r26-g0056-02":"Fondo de Inversiones de Teruel","q-coalicion-d21-2026-r26-g0019-02":"presentar presupuestos","q-pp23-215-b":"organismos estatales independientes"}
        for qid,term in examples.items():
            self.assertIn(term,self.actual[qid]["paragraphs"][0])
            self.assertEqual(self.actual[qid]["profile"],"revision-individual")

    def test_examples_follow_the_instrument_not_only_the_category(self):
        cases={
            "Los trámites para crear empresas deberían simplificarse.":("tramites","oficinas"),
            "Deberían ofrecerse planes de acompañamiento a empresas que se internacionalizan.":("internacionalizacion","distribuidores"),
        }
        for statement,(profile,example_term) in cases.items():
            question=next(q for q in self.bank["questions"] if q["statement"]==statement)
            content=self.actual[question["id"]]
            self.assertEqual(content["profile"],profile)
            self.assertIn(example_term,content["paragraphs"][2])

    def test_tax_simplification_is_not_confused_with_paperwork(self):
        self.assertNotEqual(self.actual["q-pp23-042-c"]["profile"],"tramites")

    def test_monetary_policy_and_refunds_are_not_crossed_with_unrelated_domains(self):
        question=next(q for q in self.bank["questions"] if q["statement"]=="El Banco Central Europeo debería revertir las subidas de tipos de interés iniciadas en julio de 2022.")
        self.assertEqual(self.actual[question["id"]]["profile"],"tipos-interes")
        self.assertIn("hipoteca",self.actual[question["id"]]["paragraphs"][2])
        for q in self.bank["questions"]:
            if q["category"] in {"fiscalidad","consumo"}:
                self.assertNotEqual(self.actual[q["id"]]["profile"],"repatriacion")

    def test_plain_language_keeps_negations_and_conjugates_relevant_verbs(self):
        self.assertEqual(editor.plain_statement("Las competencias deberían transferirse a otra institución."),"Se propone que las competencias se transfieran a otra institución.")
        self.assertEqual(editor.plain_statement("El euro digital no debería implantarse."),"Se propone que el euro digital no se implante.")
        self.assertEqual(editor.plain_statement("Debería mantenerse una jornada de 32 horas sin reducción salarial."),"Se propone mantener una jornada de 32 horas sin reducción salarial.")

    def test_terms_and_examples_do_not_conflate_different_policy_tools(self):
        glossary={g["term"]:g["meaning"] for g in json.loads((ROOT/"explicaciones/glosario.json").read_text(encoding="utf-8"))}
        self.assertIn("no es impunidad",glossary["aforamiento"])
        self.assertIn("no significa simplemente atención personalizada",glossary["educación diferenciada"])
        self.assertIn("no convierte por sí solo",next(r["background"] for r in json.loads((ROOT/"explicaciones/reglas.json").read_text(encoding="utf-8")) if r["id"]=="terapias"))


if __name__=="__main__":
    unittest.main()
