from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from copy import deepcopy,copy
import re,math,hashlib,shutil,json,sys
from openpyxl import load_workbook
root=Path.cwd();temp=root/'tmp/engranes'
base=temp/'base_arranque.xlsx'; authored=temp/'arranque_export.xlsx'; staged=temp/'arranque_integrado.xlsx'
target=root/'Calculos/EXCEL ENGRANES.xlsx'
sheet_title='Arranque'
if len(sys.argv)>1 and sys.argv[1]=='ejes':
    base=temp/'base_ejes.xlsx';authored=temp/'ejes_export.xlsx';staged=temp/'ejes_integrado.xlsx'
    target=root/'Calculos/CALCULADORA EJES.xlsx';sheet_title='Entrada nominal y arranque'
ns='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
N={'m':ns};tag=lambda name:'{'+ns+'}'+name

with ZipFile(base) as z,ZipFile(authored) as a:
    original={info.filename:z.read(info.filename) for info in z.infolist()}
    workbook=ET.fromstring(a.read('xl/workbook.xml'))
    rels=ET.fromstring(a.read('xl/_rels/workbook.xml.rels'))
    relation={r.attrib['Id']:r.attrib['Target'] for r in rels}
    node=next(s for s in workbook.find('m:sheets',N) if s.attrib['name']==sheet_title)
    sheetpath=relation[node.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
    sheetpath=sheetpath.lstrip('/') if sheetpath.startswith('/') else 'xl/'+sheetpath
    sheet=ET.fromstring(a.read(sheetpath))
    strings=ET.fromstring(a.read('xl/sharedStrings.xml')) if 'xl/sharedStrings.xml' in a.namelist() else []
    for cell in sheet.findall('.//m:c',N):
        if cell.attrib.get('t')=='s':
            si=strings[int(cell.find('m:v',N).text)]
            cell.remove(cell.find('m:v',N));cell.attrib['t']='inlineStr'
            ins=ET.SubElement(cell,tag('is'))
            for item in si: ins.append(deepcopy(item))
    oldstyles=ET.fromstring(z.read('xl/styles.xml')); newstyles=ET.fromstring(a.read('xl/styles.xml'))
    additions={}; maps={}
    def map_item(collection,idx):
        key=(collection,int(idx))
        if key in maps:return maps[key]
        olditems=oldstyles.find('m:'+collection,N)
        newitems=newstyles.find('m:'+collection,N)
        item=deepcopy(newitems[int(idx)])
        if collection=='cellXfs':
            for attr,coll in [('fontId','fonts'),('fillId','fills'),('borderId','borders')]:
                if attr in item.attrib:item.attrib[attr]=str(map_item(coll,item.attrib[attr]))
            item.attrib['xfId']='0'
            num=int(item.attrib.get('numFmtId','0'))
            if num>=164:
                code=next(e.attrib['formatCode'] for e in newstyles.find('m:numFmts',N) if int(e.attrib['numFmtId'])==num)
                oldfmts=oldstyles.find('m:numFmts',N)
                existing=next((e.attrib['numFmtId'] for e in oldfmts if e.attrib['formatCode']==code),None) if oldfmts is not None else None
                if existing is None:
                    allfmts=list(oldfmts) if oldfmts is not None else []
                    allfmts+=additions.get('numFmts',[])
                    existing=str(max([163]+[int(e.attrib['numFmtId']) for e in allfmts])+1)
                    fmt=ET.Element(tag('numFmt'),{'numFmtId':existing,'formatCode':code})
                    additions.setdefault('numFmts',[]).append(fmt)
                item.attrib['numFmtId']=existing
        count=len(olditems) if olditems is not None else 0
        newidx=count+len(additions.get(collection,[]))
        additions.setdefault(collection,[]).append(item);maps[key]=newidx
        return newidx
    for cell in sheet.findall('.//m:c',N):
        if 's' in cell.attrib:cell.attrib['s']=str(map_item('cellXfs',cell.attrib['s']))
    for rule in sheet.findall('.//m:cfRule',N):
        if 'dxfId' in rule.attrib:rule.attrib['dxfId']=str(map_item('dxfs',rule.attrib['dxfId']))
    styles=z.read('xl/styles.xml').decode()
    for coll,items in additions.items():
        old=oldstyles.find('m:'+coll,N);count=(len(old) if old is not None else 0)+len(items)
        extra=''.join(ET.tostring(x,encoding='unicode') for x in items)
        pattern=rf'<{coll}\b[^>]*(?:/>|>.*?</{coll}>)'
        match=re.search(pattern,styles,flags=re.S)
        if match:
            chunk=match.group(0)
            chunk=re.sub(r'\bcount="\d+"',f'count="{count}"',chunk,count=1)
            if chunk.endswith('/>'):chunk=chunk[:-2]+'>'+extra+f'</{coll}>'
            else:chunk=chunk.replace(f'</{coll}>',extra+f'</{coll}>')
            styles=styles[:match.start()]+chunk+styles[match.end():]
        else:
            if coll=='numFmts':
                styles=styles.replace('<fonts',f'<numFmts count="{count}">{extra}</numFmts><fonts',1)
            elif coll=='dxfs':
                chunk=f'<dxfs count="{count}">{extra}</dxfs>'
                if '<tableStyles' in styles:styles=styles.replace('<tableStyles',chunk+'<tableStyles',1)
                else:styles=styles.replace('</styleSheet>',chunk+'</styleSheet>')
            else:raise AssertionError(coll)
    wbtext=z.read('xl/workbook.xml').decode()
    wbroot=ET.fromstring(wbtext)
    nextid=max(int(s.attrib['sheetId']) for s in wbroot.find('m:sheets',N))+1
    rtext=z.read('xl/_rels/workbook.xml.rels').decode()
    rid='rId'+str(max([0]+[int(x) for x in re.findall(r'Id="rId(\d+)"',rtext)])+1)
    path=f'xl/worksheets/sheet{nextid}.xml'
    wbtext=wbtext.replace('</sheets>',f'<sheet name="{sheet_title}" sheetId="{nextid}" r:id="{rid}"/></sheets>')
    wbtext=re.sub(r'<calcPr\b[^>]*/>','<calcPr calcId="0" fullCalcOnLoad="1" forceFullCalc="1"/>',wbtext)
    rtext=rtext.replace('</Relationships>',f'<Relationship Id="{rid}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{nextid}.xml"/></Relationships>')
    rtext=re.sub(r'<Relationship\b[^>]*\bType="[^"]*/calcChain"[^>]*/>','',rtext)
    ctext=z.read('[Content_Types].xml').decode()
    ctext=re.sub(r'<Override\b[^>]*\bPartName="/xl/calcChain.xml"[^>]*/>','',ctext)
    ctext=ctext.replace('</Types>',f'<Override PartName="/{path}" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/></Types>')
    changes={'xl/workbook.xml':wbtext.encode(),'xl/_rels/workbook.xml.rels':rtext.encode(),'[Content_Types].xml':ctext.encode(),'xl/styles.xml':styles.encode(),path:ET.tostring(sheet,encoding='utf-8',xml_declaration=True)}
    with ZipFile(staged,'w') as out:
        for info in z.infolist():
            if info.filename!='xl/calcChain.xml':out.writestr(info,changes.get(info.filename,original[info.filename]))
        out.writestr(path,changes[path])

old=load_workbook(base,data_only=False); final=load_workbook(staged,data_only=False); values=load_workbook(staged,data_only=True)
assert final.sheetnames==old.sheetnames+[sheet_title]
for s in old:
    after=final[s.title]
    assert len(s._images)==len(after._images)
    for row in s:
        for c in row:
            assert c.value==after[c.coordinate].value,(s.title,c.coordinate,'value')
            other=after[c.coordinate]
            for prop in ['font','fill','border','alignment','protection','number_format']:
                assert copy(getattr(c,prop))==copy(getattr(other,prop)),(s.title,c.coordinate,prop)
with ZipFile(staged) as z:
    for name,data in original.items():
        if name not in changes and name!='xl/calcChain.xml':assert z.read(name)==data,name
s=values[sheet_title]
for row in s:
    for c in row:assert c.data_type!='e',(c.coordinate,c.value)
if sheet_title=='Arranque':
    for k,col in enumerate('CDEF'):
        torque=6.1 if k<2 else 6.1*3*.98
        force=2*torque/(20/6*.0254)
        assert math.isclose(s[f'{col}31'].value,force,rel_tol=1e-12)
        ks=s[f'{col}35'].value;kv=s[f'{col}34'].value;face=1.5 if k<2 else 2
        sigma=force/4.4482216152605*kv*ks*6/face*1.18/(.34 if k%2==0 else .43)
        assert math.isclose(s[f'{col}43'].value,sigma,rel_tol=1e-12)
        assert s[f'{col}49'].value=='CUMPLE'
    assert math.isclose(sum(s[f'F{r}'].value for r in range(53,57)),.017268466703703703,rel_tol=1e-12)
else:
    assert final[sheet_title].freeze_panes is None
    assert final[sheet_title].sheet_view.showGridLines is not False
    assert all(not row.hidden for row in final[sheet_title].row_dimensions.values())
    assert all(not col.hidden for col in final[sheet_title].column_dimensions.values())
    assert math.isclose(s['E35'].value,25.13633427370066,rel_tol=1e-12)
    for c in ['D','E']:
        torque=s[f'{c}22'].value/.1129848290276167
        wt=2*torque/(20/6);wr=wt*math.tan(math.radians(20))
        assert math.isclose(s[f'{c}24'].value,wt,rel_tol=1e-12)
        assert math.isclose(s[f'{c}25'].value,wr,rel_tol=1e-12)
        moment=math.hypot(wt,wr)*1.75*1.25/3
        assert math.isclose(s[f'{c}35'].value,moment,rel_tol=1e-12)
        for r in range(36,40):assert abs(s[f'{c}{r}'].value)<1e-10
assert hashlib.sha256(target.read_bytes()).digest()==hashlib.sha256(base.read_bytes()).digest(),'El archivo original cambió durante la edición'
shutil.copyfile(staged,target)
print(json.dumps({'output':str(target),'sheet':sheet_title,'preserved_images':sum(len(x._images) for x in old),'result_D35':s['D35'].value,'result_E35':s['E35'].value},ensure_ascii=False))
