"""Transcripción de cuadros institucionales, sin convertir erratas en datos precisos."""
import importlib.util,pathlib,re,json,sys
s=importlib.util.spec_from_file_location('r',pathlib.Path(__file__).with_name('consultar-rioja.py'));r=importlib.util.module_from_spec(s);s.loader.exec_module(r);c=r.c
import pymupdf

def cabinets():
 result=[]
 for original in json.loads((c.CACHE/'gabinetes.json').read_text('utf8')):
  doc=pymupdf.open(c.CACHE/f"gabinetes/{original['key']}.pdf");members=[]
  for page in doc:
   text=page.get_text();tables=page.find_tables().tables;assert len(tables)==1,original
   table=tables[0].extract();last_role=last_name=None
   for row in table[1:]:
    cells=[cell for cell in row if cell is not None]
    if len(cells)!=4 or not c.iso(cells[2]):continue
    # Las tablas antiguas tienen una fila por nombramiento; sus saltos de línea
    # son ajustes tipográficos, no cargos distintos. En 2019 hay celdas fusionadas.
    count=len(re.findall(r'\d{2}/\d{2}/\d{4}',cells[2]))
    columns=[[c.clean(cell)]for cell in cells]if count==1 else[cell.split('\n')for cell in cells]
    assert all(len(col)==count for col in columns),(original,row)
    for role,name,start,end in zip(*columns):
     role=c.clean(role or last_role);name=c.clean(name or last_name);last_role=role;last_name=name
     members.append(dict(role=role,name=name,start=c.iso(start),end=c.iso(end)))
   dates=re.findall(r'\d{2}/\d{2}/\d{4}',table[0][0])[:2]
   assert len(dates)==2,(original,dates)
  result.append({**original,'start':c.iso(dates[0]),'end':c.iso(dates[1]),'members':members})
 c.write(c.CACHE/'gabinetes-preparados.json',result)
 print('GABINETES',len(result),'CARGOS',sum(len(g['members'])for g in result))

if __name__=='__main__':cabinets()
