from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
import re,json,math,hashlib
from openpyxl import load_workbook
tmp=Path('tmp/engranes');base=tmp/'base_arr_eje.xlsx';source=tmp/'export_arr_eje.xlsx';out=tmp/'eje1_arranque_verificado.xlsx'
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};tag=lambda x:'{'+N['m']+'}'+x
changes=json.loads((tmp/'cambios_arr_eje.json').read_text(encoding='utf-8'));addresses=set(changes['values'])|set(changes['formulas'])
with ZipFile(base) as z:files={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
with ZipFile(source) as z:authored={i.filename:z.read(i.filename) for i in z.infolist()}
def sp(parts):
 rels={r.get('Id'):r.get('Target') for r in E.fromstring(parts['xl/_rels/workbook.xml.rels'])}
 s=next(s for s in E.fromstring(parts['xl/workbook.xml']).find('m:sheets',N) if s.get('name')=='Eje 1')
 p=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
 return p.lstrip('/') if p.startswith('/') else 'xl/'+p
path=sp(files);sheet=E.fromstring(files[path]);data=sheet.find('m:sheetData',N)
oldcells={c.get('r'):c for c in sheet.findall('.//m:sheetData/m:row/m:c',N)}
newcells={c.get('r'):c for c in E.fromstring(authored[sp(authored)]).findall('.//m:sheetData/m:row/m:c',N)}
for addr in addresses:
 r=int(re.search(r'\d+',addr).group());row=next((x for x in data if int(x.get('r'))==r),None)
 if row is None:row=E.SubElement(data,tag('row'),r=str(r))
 old=oldcells.get(addr)
 assert old is None or (old.find('m:f',N) is None and old.find('m:v',N) is None and old.find('m:is',N) is None),('Celda ocupada',addr)
 attrs=dict(old.attrib) if old is not None else {'r':addr};attrs.pop('t',None)
 refrow=85 if r==89 else 5 if r==90 else 87 if r==97 else 86
 refaddr=re.sub(r'\d+',str(refrow),addr)
 if addr[0] in ['E','G','J'] and 91<=r<=98:refaddr=addr[0]+'87'
 ref=oldcells.get(refaddr)
 if ref is not None and ref.get('s') is not None:attrs['s']=ref.get('s')
 c=E.Element(tag('c'),attrs)
 if addr in changes['values']:
  val=changes['values'][addr]
  if isinstance(val,str):
   c.set('t','inlineStr');isnode=E.SubElement(c,tag('is'));E.SubElement(isnode,tag('t')).text=val
  else:E.SubElement(c,tag('v')).text=str(val)
 else:
  E.SubElement(c,tag('f')).text=changes['formulas'][addr][1:]
  v=newcells[addr].find('m:v',N)
  assert v is not None and newcells[addr].get('t')!='e',addr
  if newcells[addr].get('t') in ['str','b']:c.set('t',newcells[addr].get('t'))
  c.append(deepcopy(v))
 if old is not None:row.remove(old)
 row.append(c)
def colnum(addr):
 n=0
 for c in re.match('[A-Z]+',addr).group():n=n*26+ord(c)-64
 return n
for row in data:row[:]=sorted(row,key=lambda c:colnum(c.get('r')))
data[:]=sorted(data,key=lambda r:int(r.get('r')))
for prefix in sheet.get('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable','').split():assert prefix in sheet.nsmap
serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
updates={path:serialize(sheet)}
wb=E.fromstring(files['xl/workbook.xml']);cp=wb.find('m:calcPr',N)
if cp is None:cp=E.SubElement(wb,tag('calcPr'))
cp.set('fullCalcOnLoad','1');cp.set('forceFullCalc','1');updates['xl/workbook.xml']=serialize(wb)
if 'xl/calcChain.xml' in files:
 rels=E.fromstring(files['xl/_rels/workbook.xml.rels'])
 for x in list(rels):
  if x.get('Type','').endswith('/calcChain'):rels.remove(x)
 updates['xl/_rels/workbook.xml.rels']=serialize(rels)
 ct=E.fromstring(files['[Content_Types].xml'])
 for x in list(ct):
  if x.get('PartName')=='/xl/calcChain.xml':ct.remove(x)
 updates['[Content_Types].xml']=serialize(ct)
with ZipFile(out,'w') as z:
 for info in infos:
  if info.filename!='xl/calcChain.xml':z.writestr(info,updates.get(info.filename,files[info.filename]))
with ZipFile(out) as z:
 assert z.testzip() is None
 for p,b in files.items():
  if p not in updates and p!='xl/calcChain.xml':assert z.read(p)==b,p
old=load_workbook(base,data_only=False);w=load_workbook(out,data_only=False);vals=load_workbook(out,data_only=True)
assert w.sheetnames==old.sheetnames
for s in old:
 dst=w[s.title]
 assert len(s._images)==len(dst._images)
 assert s.freeze_panes==dst.freeze_panes
 assert s.sheet_view.showGridLines==dst.sheet_view.showGridLines
 for row in s:
  for c in row:
   if s.title!='Eje 1' or c.coordinate not in addresses:assert c.value==dst[c.coordinate].value,(s.title,c.coordinate)
s=vals['Eje 1']
for col in ['E','G','J']:
 ratio=vals['INICIAR P1']['D13'].value/vals['INICIAR P1']['D12'].value
 M=max(abs(s[col+'7'].value),abs(s[col+'8'].value))*ratio
 T=vals['INICIAR P1']['D13'].value if max(abs(s[col+'10'].value),abs(s[col+'11'].value))>0 else 0
 d=s[col+'80'].value;kt=s[col+'63'].value;kts=s[col+'66'].value
 vm=math.hypot(32*kt*M,math.sqrt(3)*16*kts*T)/(math.pi*d**3)
 assert math.isclose(s[col+'96'].value,vm,rel_tol=1e-12)
 assert math.isclose(s[col+'97'].value,s[col+'16'].value/vm,rel_tol=1e-12)
 assert s[col+'99'].value=='CUMPLE'
 for r in range(91,100):assert s[f'{col}{r}'].data_type!='e'
(tmp/'arr_eje_sha256.txt').write_text(hashlib.sha256(base.read_bytes()).hexdigest())
print(json.dumps({'prepared':str(out.resolve()),'added_range':'Eje 1!A89:J100','ny_start':[s[c+'97'].value for c in ['E','G','J']],'all_existing_cells_preserved':True}))
