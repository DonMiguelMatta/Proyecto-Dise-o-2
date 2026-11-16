from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from openpyxl import load_workbook
from openpyxl.formula.tokenizer import Tokenizer
from openpyxl.utils.cell import range_boundaries
from collections import deque
import re, math, shutil, json

root=Path.cwd()
src=root/'Calculos/EXCEL ENGRANES.xlsx'
tmp=root/'tmp/engranes'
generated=tmp/'recalculado.xlsx'
original=load_workbook(src,data_only=False)
edited=load_workbook(generated,data_only=False)
changed={(s,c.coordinate) for s in original.sheetnames for row in original[s] for c in row
         if c.value != edited[s][c.coordinate].value}
expected={('Etapa1','E17'),('Etapa1','F17'),('Etapa1','E37'),('Etapa 2','E10'),('Etapa 2','E12'),('Etapa 2','F12'),('Etapa 2','E37')}
assert changed==expected,(changed,expected)
dependents={}
for sheet in edited:
    for row in sheet:
        for c in row:
            if c.data_type!='f': continue
            target=(sheet.title,c.coordinate)
            for token in Tokenizer(c.value).items:
                if token.type!='OPERAND' or token.subtype!='RANGE': continue
                text=token.value
                if '!' in text:
                    name,area=text.rsplit('!',1)
                    name=name.strip("'").replace("''", "'")
                else: name,area=sheet.title,text
                try: x1,y1,x2,y2=range_boundaries(area)
                except ValueError: continue
                if None in (x1,y1,x2,y2): continue
                for cells in edited[name].iter_rows(min_col=x1,max_col=x2,min_row=y1,max_row=y2):
                    for precedent in cells: dependents.setdefault((name,precedent.coordinate),set()).add(target)
affected=set(changed)
queue=deque(changed)
while queue:
    for target in dependents.get(queue.popleft(),set()):
        if target not in affected: affected.add(target); queue.append(target)

ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sheet_paths(z):
    rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
    targets={r.attrib['Id']:r.attrib['Target'] for r in rels}
    result={}
    for s in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',ns):
        target=targets[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        result[s.attrib['name']]=target.lstrip('/') if target.startswith('/') else 'xl/'+target
    return result

backup=tmp/'original.xlsx'
if not backup.exists(): shutil.copy2(src,backup)
staged=tmp/'verificado.xlsx'
with ZipFile(backup) as old, ZipFile(generated) as new:
    old_paths=sheet_paths(old); new_paths=sheet_paths(new)
    replacements={}
    for name,file in old_paths.items():
        raw=old.read(file).decode('utf-8')
        cells={c.attrib['r']:c for c in ET.fromstring(new.read(new_paths[name])).findall('.//m:sheetData/m:row/m:c',ns)}
        def patch(match):
            cell=match.group(0)
            addr=re.search(r'\br="([A-Z]+[0-9]+)"',cell).group(1)
            key=(name,addr)
            if key not in affected: return cell
            element=cells[addr]
            val=element.find('m:v',ns)
            assert val is not None,(key,'missing cached value')
            assert element.attrib.get('t')!='e',(key,val.text)
            if key in changed:
                formula=edited[name][addr].value[1:]
                if re.search(r'<f\b[^>]*>.*?</f>',cell):
                    cell=re.sub(r'<f\b[^>]*>.*?</f>', '<f>'+formula+'</f>',cell)
                else:
                    cell=re.sub(r'(<c\b[^>]*>)',r'\1<f>'+formula+'</f>',cell,count=1)
            if re.search(r'<v(?:\s[^>]*)?>.*?</v>',cell):
                cell=re.sub(r'<v(?:\s[^>]*)?>.*?</v>','<v>'+val.text+'</v>',cell)
            else: cell=cell.replace('</c>','<v>'+val.text+'</v></c>')
            return cell
        updated=re.sub(r'<c\b[^>]*/>|<c\b[^>]*>.*?</c>',patch,raw,flags=re.S)
        if updated!=raw: replacements[file]=updated.encode('utf-8')
    raw=old.read('xl/workbook.xml').decode('utf-8')
    raw=re.sub(r'<calcPr\b[^>]*/>', '<calcPr calcId="0" fullCalcOnLoad="1" forceFullCalc="1"/>',raw)
    replacements['xl/workbook.xml']=raw.encode('utf-8')
    # Remove the obsolete calculation order so Excel rebuilds it from the edited references.
    if 'xl/calcChain.xml' in old.namelist():
        rel=old.read('xl/_rels/workbook.xml.rels').decode('utf-8')
        replacements['xl/_rels/workbook.xml.rels']=re.sub(r'<Relationship\b[^>]*\bType="[^"]*/calcChain"[^>]*/>','',rel).encode()
        types=old.read('[Content_Types].xml').decode('utf-8')
        replacements['[Content_Types].xml']=re.sub(r'<Override\b[^>]*\bPartName="/xl/calcChain.xml"[^>]*/>','',types).encode()
    with ZipFile(staged,'w') as output:
        for info in old.infolist():
            if info.filename=='xl/calcChain.xml': continue
            output.writestr(info,replacements.get(info.filename,old.read(info.filename)))

final_formulas=load_workbook(staged,data_only=False)
final=load_workbook(staged,data_only=True)
assert final.sheetnames==original.sheetnames
for sheet in original:
    after=final_formulas[sheet.title]
    assert list(sheet.merged_cells.ranges)==list(after.merged_cells.ranges)
    assert len(sheet._images)==len(after._images)
    for row in sheet:
        for c in row:
            other=after[c.coordinate]
            assert c._style==other._style,(sheet.title,c.coordinate,'style')
            if (sheet.title,c.coordinate) not in changed: assert c.value==other.value,(sheet.title,c.coordinate,'unexpected edit')
for name in ['Etapa1','Etapa 2']:
    s=final[name]
    assert math.isclose(s['E37'].value,3)
    I=math.cos(math.radians(20))*math.sin(math.radians(20))*3/(2*4)
    assert math.isclose(s['E20'].value,I,rel_tol=1e-12)
    for col in ['E','F']:
        contact=s[f'{col}22'].value*math.sqrt(s[f'{col}13'].value*s[f'{col}25'].value*s['E23'].value*s[f'{col}27'].value*s['E28'].value/(s['E9'].value*s[f'{col}7'].value)*s[f'{col}26'].value/I)
        assert math.isclose(s[f'{col}41'].value,contact,rel_tol=1e-12)
assert math.isclose(final['Etapa1']['E17'].value,10.504226244065093*math.tan(math.radians(20)),rel_tol=1e-12)
assert final['Etapa 2']['E10'].value==600
assert final['Etapa 2']['F10'].value==200
assert final['Etapa 2']['E12'].value==0.49
with ZipFile(backup) as a, ZipFile(staged) as b:
    for name in a.namelist():
        if name not in replacements and name!='xl/calcChain.xml': assert a.read(name)==b.read(name),name
shutil.copyfile(staged,src)
print(json.dumps({'formula_changes':sorted(changed),'recalculated_cells':len(affected),'radial_lbf':final['Etapa1']['E17'].value,'output_rpm':final['Etapa 2']['F10'].value,'preserved_images':sum(len(s._images) for s in final_formulas),'file':str(src)},ensure_ascii=False))
