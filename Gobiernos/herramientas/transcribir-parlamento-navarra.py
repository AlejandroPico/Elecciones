"""Extracción verificable de relaciones nominales oficiales. Los candidatos se revisan antes de integrarlos."""
import importlib.util,pathlib,re,json,sys,collections
s=importlib.util.spec_from_file_location('n',pathlib.Path(__file__).with_name('consultar-norte.py'));n=importlib.util.module_from_spec(s);s.loader.exec_module(n);c=n.c
import pymupdf
PARTY=r'(?:PSN[/-]PSOE|SPN/PSOE|PSOE/PSN|PSOUPSN|Nafarroa[ -]Bai(?: 2011)?|Na[.-]Bai|NaBai|NAVARRA SUMA|Navarra Suma|NA\+|EH Bildu|EH BILDU|EH-Bildu|Geroa Bai|GEROA BAI|GBAI|Contigo[ -]Zurekin|CONTIGO[ -]ZUREKIN|Izquierda[ -]Ezkerra|IZQUIERDA[ -]EZKERRA|I-E|IUN[/-]NEB|IUN-NEB|IU[/-]EB|IU \(IE \(n\)\)|Podemos[/-]Ahal Dugu|PODEMOS[/-]AHAL DUGU|Podemos|PODEMOS|UPN(?: \(NA\+\))?|Ciudadanos \(NA\+\)|PP \(NA\+\)|UDF|PSOE|CDS|CDN|PPN|P\.\s?P\.|PP|I\.\s?U\.|IU|AP|HB|EA|EE|VOX|Vox|BILDU|Bildu)'

def ordered(name):
 name=c.clean(name).strip(' .').replace('OTAN0','OTANO');name=re.sub(r'^\d+[.)]\s*','',name)
 name=re.sub(r'^(?:D\.ª|Dª\.?|Dña\.?|D\.)\s*','',name)
 name=re.sub(r'\bM\s*[.ªº”"’]+','María',name);name=re.sub(r'\bF(?:CO|co)\.?\s*','Francisco ',name)
 if ','in name:
  surname,first=name.split(',',1)
  if surname.isupper():surname=' '.join(w.capitalize()if w.lower()not in['de','del','y']else w.lower()for w in surname.split())
  name=c.clean(first+' '+surname)
 return name

def lines(page,side=None):
 box=page.rect if side is None else pymupdf.Rect(side*page.rect.width/2,0,(side+1)*page.rect.width/2,page.rect.height)
 rows=[]
 for w in sorted(page.get_text('words',clip=box),key=lambda w:(w[3],w[0])):
  row=next((r for r in rows if abs(r[0]-w[3])<4.5),None)
  if row is None:row=[w[3],[]];rows.append(row)
  row[1].append(w)
 return [(y,' '.join(w[4]for w in sorted(ws,key=lambda w:w[0])))for y,ws in sorted(rows)]

def extract(data):
 doc=pymupdf.open(stream=c.fetch(data['source']),filetype='pdf');year=int(re.search(r'B(\d{4})',data['source'])[1]);rows=[]
 for pi,page in enumerate(doc):
  if pi==0:continue
  for side in ([None]if year in[1987,1991]else[0,1]):
   for y,line in lines(page,side):
    if y<45 or y>page.rect.height-30:continue
    m=re.search(r'^(.+?)\s+('+PARTY+r'|PSN|EH|EA\s*/\s*EAJ-PNV|Aralar|ARALAR|tu)\s*$',line,re.I)
    if not m:continue
    name=m[1]
    if year in[1987,1991]:
     name=re.split(r'\s+\d',name,maxsplit=1)[0]
     name=name.replace('García Adanero. Carlos','García Adanero, Carlos')
    else:name=re.sub(r'\s+\d+$','',name)
    if year in[1987,1991,1995]and ','not in name:continue
    if any(s in name.lower()for s in['grupo','parlament','nombre','portavoz','coalición','a.p.f.']):continue
    name=ordered(name)
    if not(5<len(name)<100)or re.search(r'\d',name):continue
    rows.append({'name':name,'formation':m[2],'source':data['source'],'page':pi+1})
 # Una relación electoral no convierte a sus candidatos en militantes.
 seen={}
 for row in rows:seen.setdefault(row['name'],row)
 return list(seen.values())

def main():
 out=[];indices=json.loads((c.CACHE/'navarra-boletines-indice.json').read_text('utf8'))
 for f in sorted((c.CACHE/'boletines').glob('*.json')):
  data=json.loads(f.read_text('utf8'));leg=data['legislature']
  if leg==0:continue
  year=int(f.name[:4]);rows=extract(data)
  if not rows:
   index=next(i for i in indices if i['year']==year)
   for file in index['files']:
    if re.search(rf'B{year}{leg}0+2\.pdf$',file['source']):
     rows=extract(file)
     if rows:data={**data,**file}
  out.append({'legislature':leg,'year':year,'source':data['source'],'publishedAt':data['publishedAt'],'members':rows})
  print(year,len(rows),flush=True)
 c.write(c.CACHE/'navarra-candidatos-transcripcion.json',out)
if __name__=='__main__':main()
