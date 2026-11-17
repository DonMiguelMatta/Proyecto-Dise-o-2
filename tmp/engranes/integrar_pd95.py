from pathlib import Path
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
from openpyxl import load_workbook
import json,re,math
tmp=Path('tmp/engranes');base=tmp/'base_pd95.xlsx';out=tmp/'ejes_pd95_listo.xlsx'
ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
tag=lambda x:'{'+ns['m']+'}'+x
with ZipFile(base) as z:files={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
with ZipFile(tmp/'export_pd95.xlsx') as z:generated={i.filename:z.read(i.filename) for i in z.infolist()}
changes=json.loads((tmp/'cambios_pd95.json').read_text(encoding='utf-8'))
def paths(parts):
 rels={x.get('Id'):x.get('Target') for x in E.fromstring(parts['xl/_rels/workbook.xml.rels'])}
 result={}
 for s in E.fromstring(parts['xl/workbook.xml']).find('m:sheets',ns):
  p=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
  result[s.get('name')]=p.lstrip('/') if p.startswith('/') else 'xl/'+p
 return result
srcpaths=paths(files);genpaths=paths(generated);updates={}
serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
def cache(c,auth):
 c.attrib.pop('t',None)
 if auth.get('t') in ['str','b','e']:c.set('t',auth.get('t'))
 for x in list(c):
  if x.tag in [tag('v'),tag('is')]:c.remove(x)
 v=auth.find('m:v',ns)
 if v is not None:c.append(deepcopy(v))
def colnum(addr):
 n=0
 for c in re.match('[A-Z]+',addr).group():n=n*26+ord(c)-64
 return n
for name in ['INICIAR P1','Eje 1','Eje 2','Eje 3']:
 sheet=E.fromstring(files[srcpaths[name]]);data=sheet.find('m:sheetData',ns)
 old={c.get('r'):c for c in data.findall('m:row/m:c',ns)}
 new={c.get('r'):c for c in E.fromstring(generated[genpaths[name]]).findall('m:sheetData/m:row/m:c',ns)}
 edits=changes.get(name,{'values':{},'formulas':{}})
 for addr in set(edits['values'])|set(edits['formulas']):
  r=int(re.search(r'\d+',addr).group());row=next((x for x in data if int(x.get('r'))==r),None)
  if row is None:row=E.SubElement(data,tag('row'),r=str(r))
  prior=old.get(addr);attrs=dict(prior.attrib) if prior is not None else {'r':addr};attrs.pop('t',None)
  if name=='INICIAR P1' and addr in ['B16','C16','E16']:attrs['s']=old[{'B16':'B20','C16':'C20','E16':'E21'}[addr]].get('s','0')
  c=E.Element(tag('c'),attrs)
  if addr in edits['values']:
   v=edits['values'][addr]
   if isinstance(v,str):c.set('t','inlineStr');ins=E.SubElement(c,tag('is'));E.SubElement(ins,tag('t')).text=v
   elif v is not None:E.SubElement(c,tag('v')).text=str(v)
  else:E.SubElement(c,tag('f')).text=edits['formulas'][addr][1:];cache(c,new[addr])
  if prior is not None:row.remove(prior)
  row.append(c)
 for c in data.findall('m:row/m:c',ns):
  if c.find('m:f',ns) is not None:cache(c,new[c.get('r')])
 for row in data:row[:]=sorted(row,key=lambda c:colnum(c.get('r')))
 data[:]=sorted(data,key=lambda r:int(r.get('r')))
 for prefix in sheet.get('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable','').split():assert prefix in sheet.nsmap
 updates[srcpaths[name]]=serialize(sheet)
wb=E.fromstring(files['xl/workbook.xml']);cp=wb.find('m:calcPr',ns)
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
 for i in infos:
  if i.filename!='xl/calcChain.xml':z.writestr(i,updates.get(i.filename,files[i.filename]))
with ZipFile(out) as z:
 assert z.testzip() is None
 for name,content in files.items():
  if name not in updates and name!='xl/calcChain.xml':assert z.read(name)==content,name
old=load_workbook(base,data_only=False);dst=load_workbook(out,data_only=False)
ov=load_workbook(base,data_only=True);nv=load_workbook(out,data_only=True)
assert old.sheetnames==dst.sheetnames
for s in old:
 t=dst[s.title];allowed=set(changes.get(s.title,{}).get('values',{}))|set(changes.get(s.title,{}).get('formulas',{}))
 assert len(s._images)==len(t._images)
 assert s.freeze_panes==t.freeze_panes and s.sheet_view.showGridLines==t.sheet_view.showGridLines
 assert list(s.merged_cells.ranges)==list(t.merged_cells.ranges)
 for row in s:
  for c in row:
   if c.coordinate not in allowed:assert c.value==t[c.coordinate].value,(s.title,c.coordinate)
   assert c.number_format==t[c.coordinate].number_format or (s.title=='INICIAR P1' and c.coordinate in ['B16','C16','E16'])
 for row in nv[s.title]:
  for c in row:
   if c.data_type=='e':assert ov[s.title][c.coordinate].data_type=='e',(s.title,c.coordinate,'new error',c.value)
ratio=9.5/6
for row in [25,26,31,32]:
 for c in 'EFGH':assert math.isclose(nv['INICIAR P1'][c+str(row)].value,ov['INICIAR P1'][c+str(row)].value*ratio,rel_tol=1e-12)
for c in 'DEF':
 for r in [12,13]:assert nv['INICIAR P1'][c+str(r)].value==ov['INICIAR P1'][c+str(r)].value
for name in ['Eje 1','Eje 2','Eje 3']:
 for c in 'DEFGHIJ':
  for r in [7,8,92]:
   x=ov[name][c+str(r)].value;y=nv[name][c+str(r)].value
   if isinstance(x,(int,float)):assert math.isclose(y,x*ratio,rel_tol=1e-12,abs_tol=1e-12),(name,c,r,x,y)
  for r in [10,11,58,80,93]:assert ov[name][c+str(r)].value==nv[name][c+str(r)].value,(name,c,r)
 for c in 'DEFGHIJ':
  if nv[name][c+'63'].value and nv[name][c+'80'].value and isinstance(nv[name][c+'97'].value,(int,float)):
   s=nv[name];diam=s[c+'80'].value
   stress=math.hypot(32*s[c+'63'].value*s[c+'92'].value/(math.pi*diam**3),math.sqrt(3)*16*(s[c+'66'].value or 0)*s[c+'93'].value/(math.pi*diam**3))
   assert math.isclose(s[c+'97'].value,s[c+'16'].value/stress,rel_tol=1e-12)
print(json.dumps({'output':str(out.resolve()),'forces_nominal':[nv['INICIAR P1'][c+'25'].value for c in ['E','G']],'ny_arranque_Eje3_B':nv['Eje 3']['I97'].value,'diameters_and_manual_iterations_preserved':True,'no_new_formula_errors':True}))
