from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from copy import deepcopy,copy
import json,re,math,hashlib,shutil
from openpyxl import load_workbook
root=Path.cwd();tmp=root/'tmp/engranes'
base=tmp/'base_inicio.xlsx';export=tmp/'inicio_export.xlsx';out=tmp/'iniciar_integrado.xlsx'
dest=root/'Calculos/CALCULADORA EJES.xlsx'
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
uri=ns['m'];tag=lambda n:'{'+uri+'}'+n
changes=json.loads((tmp/'inicio_cambios.json').read_text(encoding='utf-8'))
allowed=set(changes['values'])|set(changes['formulas'])
original=load_workbook(base,data_only=False)
def sheetpath(z,name):
 rels={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
 s=next(e for e in ET.fromstring(z.read('xl/workbook.xml')).find('m:sheets',ns) if e.attrib['name']==name)
 p=rels[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
 return p.lstrip('/') if p.startswith('/') else 'xl/'+p
with ZipFile(base) as a,ZipFile(export) as b:
 original_data={name:a.read(name) for name in a.namelist()}
 path=sheetpath(a,'INICIAR P1');otherpath=sheetpath(b,'INICIAR P1')
 newsheet=ET.fromstring(b.read(otherpath))
 newcells={c.attrib['r']:c for c in newsheet.findall('.//m:sheetData/m:row/m:c',ns)}
 oldsheet=ET.fromstring(a.read(path))
 data=oldsheet.find('m:sheetData',ns)
 for addr in allowed:
  r=int(re.search(r'\d+',addr).group())
  row=next((x for x in data if int(x.attrib['r'])==r),None)
  if row is None:row=ET.SubElement(data,tag('row'),{'r':str(r)})
  old=next((c for c in row if c.attrib.get('r')==addr),None)
  attrs=dict(old.attrib) if old is not None else {'r':addr}
  if r==34:
   ref=next((c for c in oldsheet.findall('.//m:c',ns) if c.attrib['r']==re.sub(r'\d+','31',addr)),None)
   if ref is not None and 's' in ref.attrib:attrs['s']=ref.attrib['s']
  attrs.pop('t',None)
  new=ET.Element(tag('c'),attrs)
  if addr in changes['values']:
   value=changes['values'][addr]
   if isinstance(value,str):
    new.attrib['t']='inlineStr';ins=ET.SubElement(new,tag('is'));ET.SubElement(ins,tag('t')).text=value
   else:ET.SubElement(new,tag('v')).text=str(value)
  else:
   ET.SubElement(new,tag('f')).text=changes['formulas'][addr][1:]
   val=newcells[addr].find('m:v',ns)
   assert val is not None and newcells[addr].attrib.get('t')!='e',addr
   new.append(deepcopy(val))
  if old is not None:row.remove(old)
  row.append(new)
 # Refresh cached values only on this worksheet; retain all unchanged formulas.
 for c in oldsheet.findall('.//m:sheetData/m:row/m:c',ns):
  if c.find('m:f',ns) is None or c.attrib['r'] in allowed:continue
  cached=newcells.get(c.attrib['r'])
  if cached is None:continue
  v=cached.find('m:v',ns)
  assert v is not None and cached.attrib.get('t')!='e',c.attrib['r']
  prior=c.find('m:v',ns)
  if prior is not None:c.remove(prior)
  c.append(deepcopy(v))
 # Keep cells and rows in canonical coordinate order.
 def colnum(address):
  n=0
  for x in re.match(r'[A-Z]+',address).group():n=n*26+ord(x)-64
  return n
 for row in data:row[:]=sorted(row,key=lambda c:colnum(c.attrib['r']))
 data[:]=sorted(data,key=lambda r:int(r.attrib['r']))
 updates={path:ET.tostring(oldsheet,encoding='utf-8',xml_declaration=True)}
 wb=a.read('xl/workbook.xml').decode()
 updates['xl/workbook.xml']=re.sub(r'<calcPr\b[^>]*/>','<calcPr calcId="0" fullCalcOnLoad="1" forceFullCalc="1"/>',wb).encode()
 if 'xl/calcChain.xml' in a.namelist():
  rel=a.read('xl/_rels/workbook.xml.rels').decode()
  updates['xl/_rels/workbook.xml.rels']=re.sub(r'<Relationship\b[^>]*\bType="[^"]*/calcChain"[^>]*/>','',rel).encode()
  types=a.read('[Content_Types].xml').decode()
  updates['[Content_Types].xml']=re.sub(r'<Override\b[^>]*\bPartName="/xl/calcChain.xml"[^>]*/>','',types).encode()
 with ZipFile(out,'w') as z:
  for info in a.infolist():
   if info.filename!='xl/calcChain.xml':z.writestr(info,updates.get(info.filename,original_data[info.filename]))
 with ZipFile(out) as z:
  for name in a.namelist():
   if name not in updates and name!='xl/calcChain.xml':assert z.read(name)==original_data[name],name
final=load_workbook(out,data_only=False);values=load_workbook(out,data_only=True)
assert final.sheetnames==original.sheetnames
for sheet in original:
 after=final[sheet.title]
 assert len(sheet._images)==len(after._images)
 assert sheet.freeze_panes==after.freeze_panes
 assert sheet.sheet_view.showGridLines==after.sheet_view.showGridLines
 assert list(sheet.merged_cells.ranges)==list(after.merged_cells.ranges)
 for row in sheet:
  for c in row:
   if sheet.title=='INICIAR P1' and c.coordinate in allowed:continue
   assert c.value==after[c.coordinate].value,(sheet.title,c.coordinate)
for row in values['INICIAR P1']:
 for c in row:assert c.data_type!='e',(c.coordinate,c.value)
s=values['INICIAR P1']
assert math.isclose(s['E25'].value,10.504166666666665,rel_tol=1e-12)
assert math.isclose(s['E27'].value,32.393729596257494,rel_tol=1e-12)
assert math.isclose(s['E28'].value,11.790353349905851,rel_tol=1e-12)
for l,r in [('E','F'),('G','H')]:
 for row in [25,26,27,28]:assert s[f'{l}{row}'].value==s[f'{r}{row}'].value
assert math.isclose(s['E13'].value,s['D13'].value*3*.98,rel_tol=1e-12)
assert math.isclose(s['F13'].value,s['D13'].value*9*.98**2,rel_tol=1e-12)
assert hashlib.sha256(base.read_bytes()).digest()==hashlib.sha256(dest.read_bytes()).digest(),'El archivo fue modificado durante la edición'
shutil.copyfile(out,dest)
print(json.dumps({'file':str(dest),'sheet':'INICIAR P1','changed_cells':len(allowed),'other_sheets_preserved':len(final.sheetnames)-1,'nominal_torques_lbin':[s.cell(12,c).value for c in [4,5,6]],'starting_torques_lbin':[s.cell(13,c).value for c in [4,5,6]]},ensure_ascii=False))
