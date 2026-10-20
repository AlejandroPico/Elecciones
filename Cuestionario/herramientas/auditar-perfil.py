"""Reproducible coverage audit. It never completes unknown party positions."""
import argparse
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

def compile_audit(bank, indices):
    questions = bank['questions']
    lookup = {q['id']: q for q in questions}
    mapped = {id for m in indices['charts'] for a in ['x','y'] for i in m[a]['indicators'] for id in i['questionIds']}
    assert mapped <= lookup.keys()
    for m in indices['charts']:
        assert m['x']['indicators'] and m['y']['indicators']
        for axis in [m['x'],m['y']]:
            seen = set()
            for i in axis['indicators']:
                assert i['direction'] in [-1,1]
                assert not seen.intersection(i['questionIds']), 'Do not count the same formulation twice in one axis'
                seen.update(i['questionIds'])
                assert all(not lookup[id]['scope'] for id in i['questionIds']), 'No territorial-to-national projection'
    known = [(q,p,v) for q in questions for p,v in q['positions'].items() if v['value'] is not None and v['evidence']]
    values = Counter(v['value'] for q,p,v in known)
    possible = len(questions)*len(bank['parties'])
    parties = []
    for p in bank['parties']:
        native = [(q,v) for q,pid,v in known if pid == p['id']]
        parties.append({**p,'known':len(native),'supports':sum(v['value']==2 for q,v in native),'opposes':sum(v['value']==-2 for q,v in native),'mapped':sum(q['id'] in mapped and not q['scope'] for q,v in native),'territorial':sum(bool(q['scope']) for q,v in native)})
    return {'date':'2026-10-20','bankVersion':bank['bankVersion'],'indexVersion':indices['version'],'questions':len(questions),'parties':len(parties),'possiblePositions':possible,'knownPositions':len(known),'matrixCoverage':100*len(known)/possible,'supportCodes':values[2],'oppositionCodes':values[-2],'multiPartyQuestions':sum(sum(v['value'] is not None and bool(v['evidence']) for v in q['positions'].values())>1 for q in questions),'mappedQuestions':len(mapped),'unmappedQuestions':len(questions)-len(mapped),'maps':len(indices['charts']),'partyCoverage':parties,'categoryCoverage':[{'id':c['id'],'title':c['title'],'questions':sum(q['category']==c['id'] for q in questions),'mapped':sum(q['category']==c['id'] and q['id'] in mapped for q in questions)} for c in bank['categories']]}

def render_report(r):
    lines=['REVISIÓN DEL MODELO DE PERFIL · 20 DE OCTUBRE DE 2026','',
      'Diagnóstico: el gráfico personal anterior escogía solo dos preguntas y convertía cada respuesta en valor × 50. Eso producía exactamente −100, −50, 0, +50 o +100 y excluía al partido sin evidencia en cualquiera de esas dos decisiones.',
      'No era una síntesis del tema ni del programa. La otra vista utilizaba otros indicadores y el gráfico de coincidencia representaba magnitudes distintas. Mezclar las tres presentaciones creaba una falsa impresión de precisión.',
      '',f"BASE REAL: {r['questions']} formulaciones, {r['parties']} organizaciones y {r['possiblePositions']} cruces posibles. Solo {r['knownPositions']} posiciones tienen evidencia ({r['matrixCoverage']:.2f} %). {r['supportCodes']} son respaldos y {r['oppositionCodes']} oposiciones. Solo {r['multiPartyQuestions']} formulaciones tienen posición documentada de al menos dos partidos.",
      'El respaldo +2 se ha usado para codificar que una propuesta consta en el documento. No acredita intensidad, radicalidad ni una escala ideológica calibrada. El número de preguntas extraídas tampoco mide representatividad electoral ni calidad del programa.',
      f"ASIGNACIÓN: {r['mappedQuestions']} preguntas están vinculadas a {r['maps']} mapas de indicadores; {r['unmappedQuestions']} todavía no. Las 40 categorías de preguntas no equivalen a 40 mapas ideológicos ya construidos.",
      '', 'CORRECCIÓN APLICADA:',
      '1. Se retira el cruce de dos preguntas. Perfil y coordenadas documentales usan el mismo catálogo fijo de índices. La posición documental no depende del sorteo o de las opiniones del usuario.',
      '2. La posición del usuario es la media ponderada de indicadores: 100 × suma(valor_del_indicador × peso) / suma(pesos), con valor normalizado en −1..1 y pesos 1, 2 o 3. No se cuantiza a múltiplos de 50. Las variantes de un indicador no multiplican su influencia.',
      '3. La media documental usa una vez cada indicador conocido. Una discrepancia de variantes se excluye; los documentos territoriales no se proyectan a índices nacionales. Ni una familia temática ni la etiqueta ideológica transfieren una postura a otro partido.',
      '4. Control del Gobierno incorpora indicadores de transparencia y fiscalización, y de límites e incompatibilidades. No se afirma que compartir esos compromisos vuelva equivalentes a sus partidos. Si coinciden, comparten punto; no se inventa dispersión.',
      '5. El porcentaje de coincidencia es PARCIAL: 100 × (1 − suma(peso × |respuesta − posición| / 4) / suma(pesos comparables)). No usa como denominador las respuestas que no pueden compararse.',
      '6. Cobertura = decisiones comparables / decisiones respondidas. Dos de treinta son un 6,67 % de cobertura; una coincidencia del 92 % solo describe esas dos, no el conjunto.',
      '7. Para todas las respuestas se muestran límites de identificación: acuerdo ponderado conocido / peso total hasta (acuerdo conocido + peso desconocido) / peso total. No son un intervalo de confianza, ni se sustituyen datos ausentes por cero ni por una puntuación central inventada.',
      '8. La barra distingue los cinco valores de respuesta: rojo intenso, rojo suave, gris, verde suave y verde intenso; la importancia mantiene el grosor.',
      '', 'LO QUE SIGUE SIN ESTAR RESUELTO:',
      'Falta construir una matriz común de decisiones comparables para todos los programas y ampliar las asignaciones a ejes. Descargar y resumir un programa no completa esa matriz. Este cambio corrige la presentación y el cálculo de índices parciales; no convierte el corpus en un test ideológico completo o validado.',
      'Los programas históricos, permanentes, generales y autonómicos conservan fechas y ámbitos. La ausencia de codificación no prueba que una organización carezca de posición. Los códigos propuestos y las equivalencias editoriales requieren contraste de pasajes, condiciones y alcances antes de ampliar la comparación.',
      '', 'COBERTURA NATIVA POR ORGANIZACIÓN:','Organización | posiciones con evidencia | respaldos | oposiciones | asignadas a índices | territoriales']
    lines += [f"{p['name']} | {p['known']} | {p['supports']} | {p['opposes']} | {p['mapped']} | {p['territorial']}" for p in r['partyCoverage']]
    lines += ['', 'ASIGNACIÓN POR CATEGORÍA:', 'Categoría | formulaciones | con eje asignado']
    lines += [f"{c['title']} | {c['questions']} | {c['mapped']}" for c in r['categoryCoverage']]
    return '\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--check',action='store_true');args=parser.parse_args()
    read=lambda name:json.loads((ROOT/name).read_text(encoding='utf-8'))
    report=compile_audit(read('sesiones-banco.json'),read('indices-perfil.json'))
    outputs={'auditoria-perfil.json':json.dumps(report,ensure_ascii=False,indent=2)+'\n','Revisión del modelo.txt':render_report(report)}
    for name,content in outputs.items():
        path=ROOT/name
        if args.check:assert path.read_text(encoding='utf-8')==content,'Regenerar '+name
        else:path.write_text(content,encoding='utf-8',newline='\n')
    print(f"{report['knownPositions']}/{report['possiblePositions']} posiciones; {report['mappedQuestions']}/{report['questions']} preguntas asignadas a índices")

if __name__=='__main__':main()
