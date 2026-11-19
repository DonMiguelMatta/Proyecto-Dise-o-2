import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_eje2_mismolado.xlsx'));
const s=w.worksheets.getItem('Eje 2');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'R9:Z24',scale:1.25,format:'png'});
 await fs.writeFile(dir+'eje2_mismolado_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={R30:'Engranes al mismo lado: Wt opuestas; Wr en el mismo sentido.'};
 const formulas={T10:"=-'INICIAR P1'!G25",V10:"=-'INICIAR P1'!G31",T11:"='INICIAR P1'!G26",V11:"='INICIAR P1'!G32"};
 for(const [a,v] of Object.entries(values))s.getRange(a).values=[[v]];
 for(const [a,v] of Object.entries(formulas))s.getRange(a).formulas=[[v]];
 w.recalculate();
 console.log((await w.inspect({kind:'table',range:"'Eje 2'!R18:Z24",tableMaxRows:7,tableMaxCols:9,maxChars:2500})).ndjson);
 console.log((await w.inspect({kind:'table',range:"'Eje 2'!D97:J99",tableMaxRows:3,tableMaxCols:7,maxChars:1000})).ndjson);
 for(const [range,file] of [['R9:Z24','eje2_mismolado_cargas'],['A78:J87','eje2_mismolado_fatiga'],['A89:J99','eje2_mismolado_arranque']]){
  const p=await w.render({sheetName:s.name,range,scale:1.25,format:'png'});
  await fs.writeFile(dir+file+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_eje2_mismolado.xlsx');
 await fs.writeFile(dir+'cambios_eje2_mismolado.json',JSON.stringify({values,formulas}));
}
