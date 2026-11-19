import json,sys,logging
from pathlib import Path
from openpyxl import load_workbook
sys.stdout.reconfigure(encoding='utf-8');logging.disable(logging.CRITICAL)
paths={'ejes':Path('../Calculos/CALCULADORA EJES.xlsx'),'engranes':Path('Calculos/EXCEL ENGRANES.xlsx')}
out={}
for name,path in paths.items():
 w=load_workbook(path,data_only=True);wf=load_workbook(path,data_only=False)
 out[name]={'path':str(path.resolve()),'sheets':{}}
 print(name,list(w.sheetnames))
 for s in w:
  if name=='ejes' and s.title not in ['INICIAR P1','Eje 1','Eje 2','Eje 3','Cuña']:continue
  if name=='engranes' and s.max_row>300:continue
  rows=[]
  for row in s:
   vals={c.coordinate:{'v':c.value,'f':wf[s.title][c.coordinate].value} for c in row if c.value is not None and c.column<=24}
   if vals:rows.append(vals)
  out[name]['sheets'][s.title]=rows
Path('tmp/rodamientos/fuentes_memoria.json').write_text(json.dumps(out,ensure_ascii=False,indent=2,default=str),encoding='utf-8')
for n,b in out.items():
 for s,rows in b['sheets'].items():
  print('\n',n,s)
  for row in rows:
   print(' | '.join(k+'='+str(v['v']) for k,v in row.items()))
