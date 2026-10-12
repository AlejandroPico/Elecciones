"""Extrae únicamente nombres y cargos de decretos originales consultados."""
import importlib.util, io, json, re, sys
sys.path.insert(0,'test-results/libraries')
from pypdf import PdfReader
spec=importlib.util.spec_from_file_location('consulta','Gobiernos/herramientas/consultar-canarias-ceuta-melilla.py')
c=importlib.util.module_from_spec(spec);spec.loader.exec_module(c)
def clean(text):
    return re.sub(r'\s+',' ',re.sub(r'-\s*\n\s*','',text)).strip()
def main():
    out=[]
    for key,date in [('ceuta-1999','1999-08-28'),('ceuta-2007','2007-06-21'),('ceuta-2011','2011-06-16')]:
        source=json.loads((c.CACHE/(key+'-nombramientos.json')).read_text('utf8'))['source']
        pdf=PdfReader(io.BytesIO(c.fetch(source)))
        pages=[clean(p.extract_text() or '') for p in pdf.pages] if key=='ceuta-1999' else [clean(' '.join(p.extract_text() or '' for p in pdf.pages))]
        for text in pages:
            if key=='ceuta-1999':
                # Codificación antigua contrastada en el PDF renderizado.
                text=text.translate(str.maketrans({'Æ':'á','Ø':'é','œ':'ú','Œ':'í'}))
                pattern=r'Sea nombrad[oa] la?\s*Excmo?\.\s*(?:Sr|Sra)\.\s*D[^. ]*[. ]+(.+?), como (Consejer[oa] de .+?)(?= la cual| el cual)'
                # Variantes de tratamiento de las disposiciones originales.
                pattern=r'Sea nombrad[oa].{0,35}?D[.“ªña]*[. ]+(.+?), como (Consejer[oa] de .+?)(?= la cual| el cual)'
            else:
                text=text.split('Efectuar los siguientes nombramientos:')[1].split('Segundo.-')[0]
                pattern=r'(?:Excma|Excmo)\.\s*(?:Sr|Sra)\.\s*D(?:ña|\.ª|ª)?\.?\s*(.+?),?\s+como\s*(.+?)(?=\.\s|\s+Excma|\s+Excmo|$)'
            for name,role in re.findall(pattern,text):
                out.append({'region':'Ceuta','date':date,'name':clean(name).title().replace('M.ª','María'),'role':clean(role).capitalize(),'source':source})
    source='https://bomemelilla.es/bome/BOME-BX-2019-21/articulo/86'
    text=clean(c.soup(source).get_text(' ',strip=True));block=text.split('El Consejo de Gobierno de la Ciudad')[1].split('Segundo')[0]
    for role,name in re.findall(r'-\s*(Consejería[^:]+):\s*D(?:ña|ª)?\.?\s*(.+?)(?=\s+-|$)',block):
        name=re.split(r',\s*Vicepresident|\s*\(Portavoz',name)[0].strip().rstrip('.')
        out.append({'region':'Melilla','date':'2019-07-04','name':name,'role':role,'source':source})
    c.write(c.CACHE/'consejerias-ciudades.json',out)
    print([(r['date'],r['name'],r['role'])for r in out],flush=True)
if __name__=='__main__':main()
