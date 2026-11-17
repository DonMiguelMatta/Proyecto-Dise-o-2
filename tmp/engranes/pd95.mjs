import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_pd95.xlsx'));
const s=w.worksheets.getItem('INICIAR P1');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'B18:I32',scale:1.3,format:'png'});
 await fs.writeFile(dir+'pd95_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const changes={'INICIAR P1':{values:{B16:'Paso diametral',C16:'1/in',E16:9.5},formulas:{E20:'=20/$E$16',F20:'=60/$E$16',G20:'=20/$E$16',H20:'=60/$E$16'}},'Eje 1':{values:{},formulas:{}}};
 const f=changes['Eje 1'].formulas;
 for(const c of ['E','G','J']){
  const old=w.worksheets.getItem('Eje 1').getRange(c+'7').values[0][0];
  f[c+'7']=`=${old}*'INICIAR P1'!$E$16/6`;
  f[c+'8']=`=-${c}7`;
 }
 for(const r of [18,19,20])for(const c of ['U','V']){
  const old=w.worksheets.getItem('Eje 1').getRange(c+r).values[0][0];
  f[c+r]=`=${old}*'INICIAR P1'!$E$16/6`;
 }
 for(const [name,data] of Object.entries(changes)){
  const sheet=w.worksheets.getItem(name);
  for(const [a,v] of Object.entries(data.values))sheet.getRange(a).values=[[v]];
  for(const [a,v] of Object.entries(data.formulas))sheet.getRange(a).formulas=[[v]];
 }
 s.getRange('E16').setNumberFormat('0.0');
 w.recalculate();
 for(const name of ['INICIAR P1','Eje 1','Eje 2','Eje 3']){
  console.log((await w.inspect({kind:'table',range:`'${name}'!${name==='INICIAR P1'?'E25:H32':'D97:J99'}`,tableMaxRows:8,tableMaxCols:7,maxChars:2200})).ndjson);
 }
 for(const [name,range,file] of [['INICIAR P1','B12:I32','pd95_cargas'],['Eje 3','A89:J99','pd95_eje3']]){
  const p=await w.render({sheetName:name,range,scale:1.2,format:'png'});
  await fs.writeFile(dir+file+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_pd95.xlsx');
 await fs.writeFile(dir+'cambios_pd95.json',JSON.stringify(changes));
}
