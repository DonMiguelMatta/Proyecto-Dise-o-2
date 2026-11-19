from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
import re,json,math,hashlib
from openpyxl import load_workbook
tmp=Path('tmp/engranes');base=tmp/'base_eje2_mismolado.xlsx';source=tmp/'export_eje2_mismolado.xlsx';out=tmp/'eje2_mismolado_listo.xlsx'
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};tag=lambda x:'{'+N['m']+'}'+x
changes=json.loads((tmp/'cambios_eje2_mismolado.json').read_text(encoding='utf-8'));allowed=set(changes['values'])|set(changes['formulas'])
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
s=vals['Eje 2'];inputs=vals['INICIAR P1'];before=load_workbook(base,data_only=True)['Eje 2']
left=s['S4'].value;right=s['S7'].value;L=right-left;x1=s['S5'].value;x2=s['S6'].value
F1=inputs['F25'].value;F2=-inputs['G25'].value;R1=inputs['F26'].value;R2=inputs['G26'].value
ra=(F1*(right-x1)+F2*(right-x2))/L;rb=F1+F2-ra
rar=(R1*(right-x1)+R2*(right-x2))/L;rbr=R1+R2-rar
for cell,value in [('S12',ra),('S13',rb),('S14',rar),('S15',rbr)]:assert math.isclose(s[cell].value,value,rel_tol=1e-12)
assert math.isclose(ra+rb,F1+F2,rel_tol=1e-12)
assert math.isclose(rb*L,F1*(x1-left)+F2*(x2-left),rel_tol=1e-12)
assert math.isclose(rar+rbr,R1+R2,rel_tol=1e-12)
assert math.isclose(rbr*L,R1*(x1-left)+R2*(x2-left),rel_tol=1e-12)
ratio=inputs['E13'].value/inputs['E12'].value
for k,c in enumerate('DEFGHIJ'):
 r=18+k;x=s['S'+str(r)].value
 mt=ra*(x-left)-F1*max(0,x-x1)-F2*max(0,x-x2)
 mr=rar*(x-left)-R1*max(0,x-x1)-R2*max(0,x-x2)
 m=math.hypot(mt,mr)
 assert math.isclose(s['U'+str(r)].value,mt,rel_tol=1e-12)
 assert math.isclose(s['V'+str(r)].value,mr,rel_tol=1e-12)
 assert math.isclose(s['W'+str(r)].value,m,rel_tol=1e-12)
 assert math.isclose(s['Y'+str(r)].value,m*ratio,rel_tol=1e-12)
 for row in [10,11,58,80,93]:assert s[c+str(row)].value==before[c+str(row)].value
 if k in [0,2,4]:
  assert math.isclose(s[c+'7'].value,m,rel_tol=1e-12)
  diam=s[c+'80'].value;se=s[c+'73'].value;sut=s[c+'15'].value;sy=s[c+'16'].value
  aa=math.sqrt(4*(s[c+'69'].value*m)**2+3*(s[c+'70'].value*s[c+'43'].value)**2)
  bb=math.sqrt(4*(s[c+'69'].value*s[c+'39'].value)**2+3*(s[c+'70'].value*s[c+'42'].value)**2)
  nf=math.pi*diam**3/(16*(aa/se+bb/sut))
  vm=math.hypot(32*s[c+'63'].value*m*ratio/(math.pi*diam**3),math.sqrt(3)*16*s[c+'66'].value*s[c+'93'].value/(math.pi*diam**3))
  assert math.isclose(s[c+'82'].value,nf,rel_tol=1e-12)
  assert math.isclose(s[c+'97'].value,sy/vm,rel_tol=1e-12)
for row in s:
 for c in row:
  if c.data_type=='e':assert before[c.coordinate].data_type=='e',(c.coordinate,c.value)
print(json.dumps({'output':str(out.resolve()),'sections':[{ 'section':s[c+'5'].value,'M_nom':s[c+'7'].value,'M_start':s[c+'92'].value,'d':s[c+'80'].value,'n_fatigue':s[c+'82'].value,'ny_start':s[c+'97'].value} for c in ['D','F','H']],'other_sheets_preserved':True}))
