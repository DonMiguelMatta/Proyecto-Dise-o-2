from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
import re,json,math,hashlib
from openpyxl import load_workbook
tmp=Path('tmp/engranes');base=tmp/'base_eje2.xlsx';source=tmp/'export_eje2.xlsx';out=tmp/'eje2_listo.xlsx'
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};tag=lambda x:'{'+N['m']+'}'+x
changes=json.loads((tmp/'cambios_eje2.json').read_text(encoding='utf-8'));allowed=set(changes['values'])|set(changes['formulas'])
with ZipFile(base) as z:files={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
with ZipFile(source) as z:generated={i.filename:z.read(i.filename) for i in z.infolist()}
def sp(parts):
 rels={x.get('Id'):x.get('Target') for x in E.fromstring(parts['xl/_rels/workbook.xml.rels'])}
 s=next(x for x in E.fromstring(parts['xl/workbook.xml']).find('m:sheets',N) if x.get('name')=='Eje 2')
 p=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
 return p.lstrip('/') if p.startswith('/') else 'xl/'+p
path=sp(files);sheet=E.fromstring(files[path]);data=sheet.find('m:sheetData',N)
oldcells={c.get('r'):c for c in sheet.findall('.//m:sheetData/m:row/m:c',N)}
newcells={c.get('r'):c for c in E.fromstring(generated[sp(generated)]).findall('.//m:sheetData/m:row/m:c',N)}
def cache(c,auth):
 c.attrib.pop('t',None)
 if auth.get('t') in ['str','b','e']:c.set('t',auth.get('t'))
 for child in list(c):
  if child.tag in [tag('v'),tag('is')]:c.remove(child)
 v=auth.find('m:v',N)
 if v is not None:c.append(deepcopy(v))
for addr in allowed:
 r=int(re.search(r'\d+',addr).group());col=re.match('[A-Z]+',addr).group();row=next((x for x in data if int(x.get('r'))==r),None)
 if row is None:row=E.SubElement(data,tag('row'),r=str(r))
 old=oldcells.get(addr);attrs=dict(old.attrib) if old is not None else {'r':addr};attrs.pop('t',None)
 ref=None
 if len(col)==1 and col in 'DFHI' and 90<=r<=99:ref=oldcells.get('E'+str(r))
 elif len(col)==1 and col in 'DFHI' and r in [20,21,22,24,25,62,63,64,66,67]:ref=oldcells.get('E'+str(r))
 elif len(col)==1 and col>='R':
  if r==17:ref=oldcells.get('R17')
  elif isinstance(changes['values'].get(addr),str):ref=oldcells.get('R18')
  else:ref=oldcells.get('U18')
 if ref is not None and ref.get('s') is not None:attrs['s']=ref.get('s')
 c=E.Element(tag('c'),attrs)
 if addr in changes['values']:
  v=changes['values'][addr]
  if isinstance(v,str):c.set('t','inlineStr');ins=E.SubElement(c,tag('is'));E.SubElement(ins,tag('t')).text=v
  elif v is not None:E.SubElement(c,tag('v')).text=str(v)
 else:
  E.SubElement(c,tag('f')).text=changes['formulas'][addr][1:]
  cache(c,newcells[addr])
 if old is not None:row.remove(old)
 row.append(c)
for c in sheet.findall('.//m:sheetData/m:row/m:c',N):
 if c.find('m:f',N) is not None and c.get('r') not in allowed:cache(c,newcells[c.get('r')])
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
 for name,v in files.items():
  if name not in updates and name!='xl/calcChain.xml':assert z.read(name)==v,name
old=load_workbook(base,data_only=False);w=load_workbook(out,data_only=False);vals=load_workbook(out,data_only=True)
assert w.sheetnames==old.sheetnames
for s in old:
 dst=w[s.title]
 assert len(s._images)==len(dst._images)
 assert s.freeze_panes==dst.freeze_panes
 assert s.sheet_view.showGridLines==dst.sheet_view.showGridLines
 assert list(s.merged_cells.ranges)==list(dst.merged_cells.ranges)
 for row in s:
  for c in row:
   if s.title!='Eje 2' or c.coordinate not in allowed:assert c.value==dst[c.coordinate].value,(s.title,c.coordinate)
s=vals['Eje 2'];input=vals['INICIAR P1']
for row in s:
 for c in row:assert c.data_type!='e',(c.coordinate,c.value)
L=10.625-.875
F1=input['F25'].value;F2=input['G25'].value;R1=input['F26'].value;R2=-input['G26'].value
RA=(F1*(10.625-3.25)+F2*(10.625-8))/L
RAR=(R1*(10.625-3.25)+R2*(10.625-8))/L
assert math.isclose(s['S12'].value,RA,rel_tol=1e-12)
assert math.isclose(s['S14'].value,RAR,rel_tol=1e-12)
assert abs(s['S12'].value+s['S13'].value-F1-F2)<1e-10
assert abs(s['S14'].value+s['S15'].value-R1-R2)<1e-10
for k,c in enumerate('DEFGHIJ'):
 r=18+k;x=s[f'S{r}'].value
 mt=RA*(x-.875)-F1*max(0,x-3.25)-F2*max(0,x-8)
 mr=RAR*(x-.875)-R1*max(0,x-3.25)-R2*max(0,x-8)
 m=math.hypot(mt,mr)
 assert math.isclose(s[c+'7'].value,m,rel_tol=1e-12)
 assert math.isclose(s[c+'8'].value,-m,rel_tol=1e-12)
 assert s[c+'10'].value==(input['E12'].value if k in [2,3,4] else 0)
 assert s[c+'11'].value==s[c+'10'].value
 A=2*s[c+'27'].value*m;B=math.sqrt(3)*s[c+'28'].value*s[c+'10'].value
 required=(16*s[c+'17'].value/math.pi*(A/s[c+'48'].value+B/s[c+'15'].value))**(1/3)
 assert math.isclose(s[c+'53'].value,required,rel_tol=1e-12)
 assert s[c+'55'].value>=required-1e-12
 assert s[c+'58'].value is None and s[c+'80'].value is None
 assert s[c+'99'].value=='Elegir diámetro'
 assert s[c+'94'].value in [None,''] and s[c+'97'].value in [None,'']
assert math.isclose(s['H7'].value,68.67168506605614,rel_tol=1e-12)
assert math.isclose(s['H92'].value,211.77615203006977,rel_tol=1e-12)
(tmp/'eje2_sha256.txt').write_text(hashlib.sha256(base.read_bytes()).hexdigest())
print(json.dumps({'prepared':str(out.resolve()),'modified_sheet':'Eje 2','max_nominal_moment':s['H7'].value,'max_start_moment':s['H92'].value,'initial_required_d':[s[c+'53'].value for c in 'DEFGHIJ'],'manual_diameters':'pending','other_sheets_preserved':len(w.sheetnames)-1}))
