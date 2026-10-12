"""Lee los cuadros del ICI cuyo ToUnicode omite ligaduras y desplaza caracteres.

Contrasta contornos exactos de las fuentes incrustadas con la tipografía original.
No corrige nombres por parecido ni modifica los PDF. Conserva la transcripción
para revisión visual. Requiere pypdf, fonttools y las fuentes Calibri/Arial.
"""
import collections, functools, io, pathlib, re, sys
sys.path.insert(0, 'test-results/libraries')
from fontTools.ttLib import TTFont
from fontTools.pens.recordingPen import DecomposingRecordingPen
from pypdf import PdfReader
from pypdf.generic import DecodedStreamObject, NameObject

def shape(glyphs, name):
    pen=DecomposingRecordingPen(glyphs);glyphs[name].draw(pen);return repr(pen.value)

@functools.lru_cache()
def original_shapes(family):
    filename={'Calibri':'calibri.ttf','Calibri-Bold':'calibrib.ttf','Calibri-Italic':'calibrii.ttf','ArialMT':'arial.ttf','Arial-BoldMT':'arialbd.ttf'}[family]
    font=TTFont(pathlib.Path('C:/Windows/Fonts')/filename); glyphs=font.getGlyphSet()
    meanings={name:chr(code) for code,name in sorted(font.getBestCmap().items(),reverse=True) if 32<=code<=383}
    for _ in range(3):
        if 'GSUB' not in font:break
        for lookup in font['GSUB'].table.LookupList.Lookup:
            for table in lookup.SubTable:
                while hasattr(table,'ExtSubTable'):table=table.ExtSubTable
                for src,dst in getattr(table,'mapping',{}).items():
                    if src in meanings and isinstance(dst,str):meanings.setdefault(dst,meanings[src])
                for src,dsts in getattr(table,'alternates',{}).items():
                    if src in meanings:
                        for dst in dsts:meanings.setdefault(dst,meanings[src])
                for src,ligatures in getattr(table,'ligatures',{}).items():
                    for lig in ligatures:
                        parts=[src,*lig.Component]
                        if all(p in meanings for p in parts):meanings.setdefault(lig.LigGlyph,''.join(meanings[p] for p in parts))
    result=collections.defaultdict(set)
    for name,text in meanings.items():result[shape(glyphs,name)].add(text)
    return result

def reader(file):
    pdf=PdfReader(file);done=set()
    for page in pdf.pages:
        for ref in page['/Resources']['/Font'].values():
            font=ref.get_object()
            if id(font) in done or '/FontDescriptor' not in font:continue
            done.add(id(font));descriptor=font['/FontDescriptor']
            if '/FontFile2' not in descriptor:continue
            family=str(font['/BaseFont']).split('+')[-1].lstrip('/')
            if family not in ['Calibri','Calibri-Bold','Calibri-Italic','ArialMT','Arial-BoldMT']:continue
            subset=TTFont(io.BytesIO(descriptor['/FontFile2'].get_data()));glyphs=subset.getGlyphSet()
            cmap=subset['cmap'].tables[0].cmap;lookup=original_shapes(family)
            old={int(a,16):bytes.fromhex(b.decode()).decode('utf-16-be') for a,b in re.findall(rb'<([0-9A-Fa-f]{2})>\s+<([0-9A-Fa-f]{4,})>',font['/ToUnicode'].get_data())}
            pairs=[]
            for code,name in cmap.items():
                options=lookup.get(shape(glyphs,name),set())
                if not options:
                    if code in old and old[code] in ['–','—','•','º','ª','\n']:text=old[code]
                    else:raise ValueError(f'Glifo sin contraste: {family} {code} {old.get(code)}')
                else:text=old.get(code) if old.get(code) in options else sorted(options,key=lambda s:(s!=' ',len(s),s))[0]
                pairs.append(f'<{code:02X}> <{text.encode("utf-16-be").hex().upper()}>')
            stream=DecodedStreamObject();stream.set_data(('/CIDInit /ProcSet findresource begin\n12 dict begin begincmap\n/CMapName /ICI-UCS def /CMapType 2 def\n1 begincodespacerange <00> <FF> endcodespacerange\n'+str(len(pairs))+' beginbfchar\n'+'\n'.join(pairs)+'\nendbfchar endcmap CMapName currentdict /CMap defineresource pop end end').encode())
            font[NameObject('/ToUnicode')]=stream
    return pdf

def rows(pdf, columns):
    result=[]
    for index,page in enumerate(pdf.pages):
        texts=[]; borders=[]; previous=None
        def operand(op,args,cm,tm):
            nonlocal previous
            if op==b'm':previous=list(map(float,args))
            if op==b'l':
                end=list(map(float,args))
                if previous and abs(previous[1]-end[1])<0.05 and abs(previous[0]-end[0])>100:
                    borders.append(end[1])
                previous=end
        page.extract_text(visitor_operand_before=operand, visitor_text=lambda t,cm,tm,font,size:texts.append((t.strip(),tm[4],tm[5])) if t.strip() else None)
        limits=[]
        for y in sorted(set(borders),reverse=True):
            if not limits or limits[-1]-y>1:limits.append(y)
        for top,bottom in zip(limits,limits[1:]):
            cells=[]
            for left,right in zip(columns,columns[1:]):
                words=sorted([(t,x,y) for t,x,y in texts if left<=x<right and bottom<y<top],key=lambda item:(-item[2],item[1]))
                cells.append(' '.join(t for t,x,y in words))
            if any(cells):result.append({'page':index+1,'cells':cells})
    return result

if __name__=='__main__':
    path=pathlib.Path(sys.argv[1]);pdf=reader(path)
    path.with_suffix('.txt').write_text('\n\nPAGE\n\n'.join(p.extract_text(extraction_mode='layout') for p in pdf.pages),'utf8')
    import json
    columns=[55,218,378,541] if path.stem.startswith('parl') else [55,157.6,355.8,541]
    path.with_suffix('.json').write_text(json.dumps(rows(pdf,columns),ensure_ascii=False,indent=2)+'\n','utf8')
