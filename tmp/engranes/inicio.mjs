import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'base_inicio_import.xlsx'));
const s=wb.worksheets.getItem('INICIAR P1');
if(process.argv[2]==='antes'){
 const p=await wb.render({sheetName:s.name,range:'B18:I34',scale:1.4,format:'png'});await fs.writeFile(dir+'inicio_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={F22:0,H22:0};
 const formulas={E3:'=D3*0.98',F3:'=E3*0.98',E11:'=F20/E20',F11:'=H20/G20',D13:'=6.1/0.1129848290276167',E13:'=D13*E11*0.98',F13:'=E13*F11*0.98',E20:'=20/6',F20:'=60/6',G20:'=20/6',H20:'=60/6',E25:'=2*$D$12/E20',F25:'=E25',G25:'=2*$E$12/G20',H25:'=G25',E27:'=2*$D$13/E20',F27:'=E27',G27:'=2*$E$13/G20',H27:'=G27',D33:'=D13',E33:'=D13',F33:'=E13',G33:'=E13',H33:'=F13',I33:'=H33'};
 for(const c of 'EFGH'){
  formulas[c+'26']=`=${c}25*TAN(RADIANS(${c}21))`;
  formulas[c+'28']=`=${c}27*TAN(RADIANS(${c}21))`;
 }
 for(const [cell,value] of Object.entries(values))s.getRange(cell).values=[[value]];
 for(const [cell,formula] of Object.entries(formulas))s.getRange(cell).formulas=[[formula]];
 wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:"'INICIAR P1'!D12:F13",tableMaxRows:2,tableMaxCols:3,maxChars:1500})).ndjson);
 console.log((await wb.inspect({kind:'table',range:"'INICIAR P1'!B25:I34",tableMaxRows:10,tableMaxCols:8,maxChars:2500})).ndjson);
 for(const [name,range] of [['inicio_potencia','B2:I13'],['inicio_fuerzas','B18:I34']]){
  const p=await wb.render({sheetName:s.name,range,scale:1.4,format:'png'});await fs.writeFile(dir+name+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(wb)).save(dir+'inicio_export.xlsx');
 await fs.writeFile(dir+'inicio_cambios.json',JSON.stringify({values,formulas}));
}
