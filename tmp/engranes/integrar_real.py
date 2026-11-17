from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
import re,json,math,hashlib
from openpyxl import load_workbook
tmp=Path('tmp/engranes');base=tmp/'base_real.xlsx';source=tmp/'export_real.xlsx';out=tmp/'CALCULADORA_EJES_actualizada.xlsx'
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};uri=N['m'];tag=lambda x:'{'+uri+'}'+x
changes=json.loads((tmp/'cambios_real.json').read_text(encoding='utf-8'));allowed=set(changes['values'])|set(changes['formulas'])
with ZipFile(base) as z:files={x.filename:z.read(x.filename) for x in z.infolist()};infos=z.infolist()
with ZipFile(source) as z:generated={x.filename:z.read(x.filename) for x in z.infolist()}
def sp(parts):
 rels={r.get('Id'):r.get('Target') for r in E.fromstring(parts['xl/_rels/workbook.xml.rels'])}
 s=next(x for x in E.fromstring(parts['xl/workbook.xml']).find('m:sheets',N) if x.get('name')=='INICIAR P1')
 p=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
 return p.lstrip('/') if p.startswith('/') else 'xl/'+p
path=sp(files);sheet=E.fromstring(files[path]);new=E.fromstring(generated[sp(generated)])
data=sheet.find('m:sheetData',N);newcells={c.get('r'):c for c in new.findall('.//m:sheetData/m:row/m:c',N)}
oldcells={c.get('r'):c for c in sheet.findall('.//m:sheetData/m:row/m:c',N)}
def colnum(addr):
 n=0
 for c in re.match('[A-Z]+',addr).group():n=n*26+ord(c)-64
 return n
for addr in allowed:
 rownum=int(re.search(r'\d+',addr).group());row=next((r for r in data if int(r.get('r'))==rownum),None)
 if row is None:row=E.SubElement(data,tag('row'),r=str(rownum))
 old=oldcells.get(addr);attrs=dict(old.attrib) if old is not None else {'r':addr};attrs.pop('t',None)
 if rownum in [13,31,32]:
  refrow={13:12,31:25,32:26}[rownum];ref=oldcells.get(re.sub(r'\d+',str(refrow),addr))
  if ref is not None and ref.get('s') is not None:attrs['s']=ref.get('s')
 c=E.Element(tag('c'),attrs)
 if addr in changes['values']:
  v=changes['values'][addr]
  if isinstance(v,str):c.set('t','inlineStr');ins=E.SubElement(c,tag('is'));E.SubElement(ins,tag('t')).text=v
  else:E.SubElement(c,tag('v')).text=str(v)
 else:
  E.SubElement(c,tag('f')).text=changes['formulas'][addr][1:]
  v=newcells[addr].find('m:v',N);assert v is not None and newcells[addr].get('t')!='e',addr;c.append(deepcopy(v))
 if old is not None:row.remove(old)
 row.append(c)
for c in sheet.findall('.//m:sheetData/m:row/m:c',N):
 if c.find('m:f',N) is None or c.get('r') in allowed:continue
 generatedcell=newcells[c.get('r')];v=generatedcell.find('m:v',N)
 assert v is not None and generatedcell.get('t')!='e',c.get('r')
 oldv=c.find('m:v',N)
 if oldv is not None:c.remove(oldv)
 c.append(deepcopy(v))
for row in data:row[:]=sorted(row,key=lambda c:colnum(c.get('r')))
data[:]=sorted(data,key=lambda r:int(r.get('r')))
for prefix in sheet.get('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable','').split():assert prefix in sheet.nsmap,prefix
serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
updates={path:serialize(sheet)}
wb=E.fromstring(files['xl/workbook.xml']);calc=wb.find('m:calcPr',N)
if calc is None:calc=E.SubElement(wb,tag('calcPr'))
calc.set('fullCalcOnLoad','1');calc.set('forceFullCalc','1');updates['xl/workbook.xml']=serialize(wb)
if 'xl/calcChain.xml' in files:
 rels=E.fromstring(files['xl/_rels/workbook.xml.rels'])
 for r in list(rels):
  if r.get('Type','').endswith('/calcChain'):rels.remove(r)
 updates['xl/_rels/workbook.xml.rels']=serialize(rels)
 types=E.fromstring(files['[Content_Types].xml'])
 for r in list(types):
  if r.get('PartName')=='/xl/calcChain.xml':types.remove(r)
 updates['[Content_Types].xml']=serialize(types)
with ZipFile(out,'w') as z:
 for info in infos:
  if info.filename!='xl/calcChain.xml':z.writestr(info,updates.get(info.filename,files[info.filename]))
with ZipFile(out) as z:
 assert z.testzip() is None
 for name,data in files.items():
  if name not in updates and name!='xl/calcChain.xml':assert z.read(name)==data,name
old=load_workbook(base,data_only=False);final=load_workbook(out,data_only=False);v=load_workbook(out,data_only=True)
assert old.sheetnames==final.sheetnames
for s in old:
 assert len(s._images)==len(final[s.title]._images)
 assert s.freeze_panes==final[s.title].freeze_panes
 for row in s:
  for c in row:
   if s.title!='INICIAR P1' or c.coordinate not in allowed:assert c.value==final[s.title][c.coordinate].value,(s.title,c.coordinate)
s=v['INICIAR P1']
for r in [12,13]:
 for c in ['D','E','F']:assert isinstance(s[f'{c}{r}'].value,(float,int))
for r in [25,26,31,32]:
 for c in ['E','F','G','H']:assert isinstance(s[f'{c}{r}'].value,(float,int))
assert math.isclose(s['E25'].value,10.504166666666665,rel_tol=1e-12)
assert math.isclose(s['E31'].value,32.393729596257494,rel_tol=1e-12)
assert math.isclose(s['E32'].value,11.790353349905851,rel_tol=1e-12)
for row in s:
 for c in row:assert c.data_type!='e',(c.coordinate,c.value)
(tmp/'real_sha256.txt').write_text(hashlib.sha256(base.read_bytes()).hexdigest())
print(json.dumps({'prepared':str(out.resolve()),'nominal_torques':[s[f'{c}12'].value for c in ['D','E','F']],'start_torques':[s[f'{c}13'].value for c in ['D','E','F']],'Wt_nom':s['E25'].value,'Wr_nom':s['E26'].value,'Wt_start':s['E31'].value,'Wr_start':s['E32'].value,'other_sheets_preserved':len(old.sheetnames)-1}))
