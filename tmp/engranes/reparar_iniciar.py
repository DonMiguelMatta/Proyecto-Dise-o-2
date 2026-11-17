from pathlib import Path,PurePosixPath
from zipfile import ZipFile
from lxml import etree as E
from copy import deepcopy
import posixpath,re,math,hashlib,shutil,json
from openpyxl import load_workbook
tmp=Path('tmp/engranes');base=tmp/'antes_reparacion.xlsx';src=tmp/'inicio_export.xlsx';out=tmp/'reparacion_iniciar.xlsx';target=Path('Calculos/CALCULADORA EJES.xlsx')
M='http://schemas.openxmlformats.org/spreadsheetml/2006/main';R='http://schemas.openxmlformats.org/package/2006/relationships';CT='http://schemas.openxmlformats.org/package/2006/content-types';N={'m':M}
tag=lambda n:'{'+M+'}'+n
parse=lambda x:E.fromstring(x)
serialize=lambda x:E.tostring(x,encoding='UTF-8',xml_declaration=True,standalone=True)
def sheetpath(files):
 rels={r.get('Id'):r.get('Target') for r in parse(files['xl/_rels/workbook.xml.rels'])}
 for s in parse(files['xl/workbook.xml']).find('m:sheets',N):
  if s.get('name')=='INICIAR P1':
   p=rels[s.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id')]
   return p.lstrip('/') if p.startswith('/') else posixpath.normpath('xl/'+p)
with ZipFile(base) as z:old={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
with ZipFile(src) as z:new={i.filename:z.read(i.filename) for i in z.infolist()}
path=sheetpath(old);sourcepath=sheetpath(new);sheet=parse(new[sourcepath]);styles=parse(old['xl/styles.xml']);ss=parse(new['xl/styles.xml'])
strings=parse(new['xl/sharedStrings.xml'])
for c in sheet.findall('.//m:sheetData/m:row/m:c',N):
 if c.get('t')=='s':
  si=strings[int(c.find('m:v',N).text)]
  c.remove(c.find('m:v',N));c.set('t','inlineStr');isnode=E.SubElement(c,tag('is'))
  for child in si:isnode.append(deepcopy(child))
maps={}
def mapstyle(coll,idx):
 key=(coll,int(idx))
 if key in maps:return maps[key]
 dest=styles.find('m:'+coll,N)
 if dest is None:
  dest=E.Element(tag(coll),count='0')
  if coll=='numFmts':styles.insert(0,dest)
  elif coll=='dxfs':
   table=styles.find('m:tableStyles',N);styles.insert(styles.index(table) if table is not None else len(styles),dest)
  else:raise ValueError(coll)
 item=deepcopy(ss.find('m:'+coll,N)[int(idx)])
 if coll=='cellXfs':
  for attr,typ in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:item.set(attr,str(mapstyle(typ,item.get(attr,'0'))))
  item.set('xfId','0')
  num=int(item.get('numFmtId','0'))
  if num>=164:
   srcfmt=next(x for x in ss.find('m:numFmts',N) if int(x.get('numFmtId'))==num)
   fmts=styles.find('m:numFmts',N)
   if fmts is None:fmts=E.Element(tag('numFmts'),count='0');styles.insert(0,fmts)
   fmt=next((x for x in fmts if x.get('formatCode')==srcfmt.get('formatCode')),None)
   if fmt is None:
    fmt=deepcopy(srcfmt);fmt.set('numFmtId',str(max([163]+[int(x.get('numFmtId')) for x in fmts])+1));fmts.append(fmt);fmts.set('count',str(len(fmts)))
   item.set('numFmtId',fmt.get('numFmtId'))
 # Reuse identical style records where possible.
 for i,olditem in enumerate(dest):
  if E.tostring(olditem,method='c14n')==E.tostring(item,method='c14n'):maps[key]=i;return i
 index=len(dest);dest.append(item);dest.set('count',str(len(dest)));maps[key]=index;return index
for c in sheet.findall('.//m:c',N):
 if c.get('s') is not None:c.set('s',str(mapstyle('cellXfs',c.get('s'))))
for col in sheet.findall('.//m:col',N):
 if col.get('style') is not None:col.set('style',str(mapstyle('cellXfs',col.get('style'))))
for row in sheet.findall('.//m:row',N):
 if row.get('s') is not None:row.set('s',str(mapstyle('cellXfs',row.get('s'))))
for rule in sheet.findall('.//m:cfRule',N):
 if rule.get('dxfId') is not None:rule.set('dxfId',str(mapstyle('dxfs',rule.get('dxfId'))))
# Give Excel valid namespace declarations throughout; lxml preserves prefix mappings.
view=sheet.find('m:sheetViews/m:sheetView',N)
if view is not None:
 view.set('showGridLines','1');view.set('topLeftCell','A1')
 for pane in view.findall('m:pane',N):view.remove(pane)
updates={path:serialize(sheet),'xl/styles.xml':serialize(styles)}
partmap={sourcepath:path}
newtypes=parse(new['[Content_Types].xml']);oldtypes=parse(old['[Content_Types].xml'])
def relpath(part):return posixpath.dirname(part)+'/_rels/'+posixpath.basename(part)+'.rels'
def register_type(source,dest):
 over=next((x for x in newtypes if x.get('PartName')=='/'+source),None)
 if over is not None:
  x=deepcopy(over);x.set('PartName','/'+dest);oldtypes.append(x)
 ext=posixpath.splitext(dest)[1][1:]
 if not any(x.get('Extension')==ext for x in oldtypes):
  default=next((x for x in newtypes if x.get('Extension')==ext),None)
  if default is not None:oldtypes.append(deepcopy(default))
def copy_part(source):
 if source in partmap:return partmap[source]
 directory=posixpath.dirname(source);name='iniciar_restaurado_'+posixpath.basename(source);dest=directory+'/'+name
 while dest in old or dest in updates:name='r_'+name;dest=directory+'/'+name
 partmap[source]=dest;updates[dest]=new[source];register_type(source,dest);copy_rels(source,dest)
 return dest
def copy_rels(source,dest):
 rp=relpath(source)
 if rp not in new:return
 relationships=parse(new[rp])
 for rel in relationships:
  if rel.get('TargetMode')=='External':continue
  part=rel.get('Target');resolved=part.lstrip('/') if part.startswith('/') else posixpath.normpath(posixpath.dirname(source)+'/'+part)
  copied=copy_part(resolved);rel.set('Target',posixpath.relpath(copied,posixpath.dirname(dest)))
 updates[relpath(dest)]=serialize(relationships)
copy_rels(sourcepath,path)
wb=parse(old['xl/workbook.xml']);cp=wb.find('m:calcPr',N)
if cp is None:cp=E.SubElement(wb,tag('calcPr'))
cp.set('fullCalcOnLoad','1');cp.set('forceFullCalc','1');updates['xl/workbook.xml']=serialize(wb)
updates['[Content_Types].xml']=serialize(oldtypes)
with ZipFile(out,'w') as z:
 for info in infos:z.writestr(info,updates.get(info.filename,old[info.filename]))
 for name,data in updates.items():
  if name not in old:z.writestr(name,data)
 # Original sheet parts and resources remain untouched except INICIAR P1.
with ZipFile(out) as z:
 assert z.testzip() is None
 for name,data in old.items():
  if name not in updates:assert z.read(name)==data,name
 for name in z.namelist():
  if name.endswith('.xml'):
   root=parse(z.read(name))
   ign=root.get('{http://schemas.openxmlformats.org/markup-compatibility/2006}Ignorable')
   if ign:
    for prefix in ign.split():assert prefix in root.nsmap,(name,prefix)
final=load_workbook(out,data_only=False);v=load_workbook(out,data_only=True)
assert final.sheetnames==load_workbook(base).sheetnames
s=v['INICIAR P1'];assert s.max_row>=33 and len(final[s.title]._images)==6
assert final[s.title].freeze_panes is None
for row in [12,13]:
 for c in ['D','E','F']:assert isinstance(s[f'{c}{row}'].value,(int,float))
for row in [25,26,27,28,32,33]:
 for c in ['E','F','G','H']:assert isinstance(s[f'{c}{row}'].value,(int,float))
assert math.isclose(s['E27'].value,32.393729596257494,rel_tol=1e-12)
assert math.isclose(s['E28'].value,11.790353349905851,rel_tol=1e-12)
for row in s:
 for c in row:assert c.data_type!='e',(c.coordinate,c.value)
assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(base.read_bytes()).digest(),'El archivo cambió durante la reparación'
shutil.copyfile(out,target)
print(json.dumps({'restored_sheet':s.title,'rows':s.max_row,'images':len(final[s.title]._images),'nominal_torque':[s[f'{c}12'].value for c in ['D','E','F']],'starting_torque':[s[f'{c}13'].value for c in ['D','E','F']],'first_stage_Wt_nominal':s['E25'].value,'first_stage_Wr_nominal':s['E26'].value,'first_stage_Wt_start':s['E27'].value,'first_stage_Wr_start':s['E28'].value}))
