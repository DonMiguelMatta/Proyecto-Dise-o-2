import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_real.xlsx'));
const s=w.worksheets.getItem('INICIAR P1');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'B18:I32',scale:1.5,format:'png'});await fs.writeFile(dir+'real_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={D3:.5,D6:1800,F6:200,F22:0,H22:0,B12:'Torque nominal',B13:'Torque arranque',C13:'lb-in',B25:'Wt nominal',B26:'Wr nominal',B31:'Wt arranque',B32:'Wr arranque',C31:'lbs',C32:'lbs'};
 const formulas={E3:'=D3*0.98',F3:'=E3*0.98',E20:'=20/6',F20:'=60/6',G20:'=20/6',H20:'=60/6',E11:'=F20/E20',F11:'=H20/G20',D13:'=6.1/0.1129848290276167',E13:'=D13*E11*0.98',F13:'=E13*F11*0.98',E25:'=2*$D$12/E20',F25:'=E25',G25:'=2*$E$12/G20',H25:'=G25',E31:'=2*$D$13/E20',F31:'=E31',G31:'=2*$E$13/G20',H31:'=G31'};
 for(const c of 'EFGH'){
  formulas[c+'26']=`=${c}25*TAN(RADIANS(${c}21))`;
  formulas[c+'32']=`=${c}31*TAN(RADIANS(${c}21))`;
 }
 s.getRange('B13:F13').copyFrom(s.getRange('B12:F12'),'all');
 s.getRange('B31:I32').copyFrom(s.getRange('B25:I26'),'all');
 for(const [a,v] of Object.entries(values))s.getRange(a).values=[[v]];
 for(const [a,v] of Object.entries(formulas))s.getRange(a).formulas=[[v]];
 w.recalculate();
 console.log((await w.inspect({kind:'table',range:"'INICIAR P1'!B25:I32",tableMaxRows:8,tableMaxCols:8,maxChars:2500})).ndjson);
 for(const [name,range] of [['real_torques','B2:F13'],['real_fuerzas','B18:I32']]){
  const p=await w.render({sheetName:s.name,range,scale:1.5,format:'png'});await fs.writeFile(dir+name+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_real.xlsx');
 await fs.writeFile(dir+'cambios_real.json',JSON.stringify({values,formulas}));
}
