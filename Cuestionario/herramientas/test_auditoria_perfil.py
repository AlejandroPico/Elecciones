import importlib
import json
from pathlib import Path
import unittest
from copy import deepcopy

editor=importlib.import_module('auditar-perfil')
ROOT=Path(__file__).resolve().parents[1]

class ProfileAudit(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank=json.loads((ROOT/'sesiones-banco.json').read_text(encoding='utf-8'))
        cls.indices=json.loads((ROOT/'indices-perfil.json').read_text(encoding='utf-8'))

    def test_audit_exposes_the_actual_sparse_matrix_and_unmapped_questions(self):
        actual=editor.compile_audit(self.bank,self.indices)
        recorded=json.loads((ROOT/'auditoria-perfil.json').read_text(encoding='utf-8'))
        self.assertEqual(actual,recorded)
        self.assertEqual(actual['knownPositions'],sum(p['known'] for p in actual['partyCoverage']))
        self.assertEqual(actual['possiblePositions'],actual['questions']*actual['parties'])
        self.assertGreater(actual['unmappedQuestions'],actual['mappedQuestions'])
        self.assertEqual(actual['supportCodes']+actual['oppositionCodes'],actual['knownPositions'])
        self.assertEqual(sum(c['mapped'] for c in actual['categoryCoverage']),actual['mappedQuestions'])

    def test_repeated_question_in_one_axis_cannot_inflate_the_index(self):
        changed=deepcopy(self.indices)
        changed['charts'][0]['x']['indicators'].append(changed['charts'][0]['x']['indicators'][0])
        with self.assertRaises(AssertionError):editor.compile_audit(self.bank,changed)

    def test_territorial_program_cannot_become_a_national_coordinate(self):
        changed=deepcopy(self.indices)
        regional=next(q for q in self.bank['questions'] if q['scope'])
        changed['charts'][0]['x']['indicators'].append({'label':'invalid projection','questionIds':[regional['id']],'direction':1})
        with self.assertRaises(AssertionError):editor.compile_audit(self.bank,changed)

if __name__=='__main__':unittest.main()
