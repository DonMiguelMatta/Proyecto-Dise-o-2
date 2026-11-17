from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
import re,json,math,hashlib
from openpyxl import load_workbook
tmp=Path('tmp/engranes');base=tmp/'base_cunas.xlsx';source=tmp/'export_cunas.xlsx';out=tmp/'cunas_listo.xlsx'
N={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};tag=lambda x:'{'+N['m']+'}'+x
changes=json.loads((tmp/'cambios_cunas.json').read_text(encoding='utf-8'));allowed=set(changes['values'])|set(changes['formulas'])
with ZipFile(base) as z:files={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
with ZipFile(source) as z:generated={i.filename:z.read(i.filename) for i in z.infolist()}
def sp(parts):
 rels={x.get('Id'):x.get('Target') for x in E.fromstring(parts['xl/_rels/workbook.xml.rels'])}
 s=next(x for x in E.fromstring(parts['xl/workbook.xml']).find('m:sheets',N) if x.get('name')=='Cuña')
 p=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
 return p.lstrip('/') if p.startswith('/') else 'xl/'+p
path=sp(files);sheet=E.fromstring(files[path]);data=sheet.find('m:sheetData',N)
oldcells={c.get('r'):c for c in sheet.findall('.//m:sheetData/m:row/m:c',N)}
newcells={c.get('r'):c for c in E.fromstring(generated[sp(generated)]).findall('.//m:sheetData/m:row/m:c',N)}
styles=E.fromstring(files['xl/styles.xml']);xfs=styles.find('m:cellXfs',N)
format3=next(x.get('numFmtId') for x in styles.find('m:numFmts',N) if '#,##0.000_' in x.get('formatCode',''));style3=deepcopy(xfs[int(oldcells['C18'].get('s','0'))])
style3.set('numFmtId',format3);style3.set('applyNumberFormat','1');index3=len(xfs);xfs.append(style3);xfs.set('count',str(len(xfs)))
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
 if addr[0] in 'CDEF' and r==1:ref=oldcells.get(addr[0]+'2')
 elif addr[0] in 'CDEF' and r in [16,20,21,22,23,24]:ref=oldcells.get(addr[0]+'18')
 elif addr[0]=='B' and r in [16,20,21,22,23,24]:ref=oldcells.get('B18')
 elif addr[0]=='G' and r in [16,20,21]:ref=oldcells.get('G18')
 if ref is not None and ref.get('s') is not None:attrs['s']=ref.get('s')
 if col in 'CDEF' and r in [14,20,21]:attrs['s']=str(index3)
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
updates={path:serialize(sheet),'xl/styles.xml':serialize(styles)}
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
   if s.title!='Cuña' or c.coordinate not in allowed:assert c.value==dst[c.coordinate].value,(s.title,c.coordinate)
s=vals['Cuña'];inputs=vals['INICIAR P1']
for row in s:
 for c in row:assert c.data_type!='e',(c.coordinate,c.value)
expected_d=[vals['Eje 1']['G80'].value,vals['Eje 2']['F80'].value,vals['Eje 2']['H80'].value,vals['Eje 3']['G80'].value]
expected_t=[inputs['D13'].value,inputs['E13'].value,inputs['E13'].value,inputs['F13'].value]
for k,c in enumerate('CDEF'):
 d=s[c+'14'].value;T=s[c+'13'].value;b=s[c+'3'].value;h=s[c+'4'].value;sy=s[c+'9'].value;n=s[c+'6'].value;L=s[c+'21'].value
 assert d==expected_d[k] and T==expected_t[k]
 force=2*T/d;lc=force*n/(b*.577*sy);la=2*force*n/(h*sy)
 assert math.isclose(s[c+'18'].value,lc,rel_tol=1e-12)
 assert math.isclose(s[c+'19'].value,la,rel_tol=1e-12)
 assert L>=max(lc,la) and L<=s[c+'5'].value
 assert math.isclose(s[c+'22'].value,.577*sy*b*L/force,rel_tol=1e-12)
 assert math.isclose(s[c+'23'].value,sy*h*L/(2*force),rel_tol=1e-12)
 assert s[c+'17'].value==1 and s[c+'24'].value=='CUMPLE'
print(json.dumps({'prepared':str(out.resolve()),'sizes':[[s[c+'3'].value,s[c+'4'].value,s[c+'21'].value] for c in 'CDEF'],'min_corte':min(s[c+'22'].value for c in 'CDEF'),'min_aplastamiento':min(s[c+'23'].value for c in 'CDEF'),'other_sheets_preserved':True}))
