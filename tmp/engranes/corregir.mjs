import fs from 'node:fs/promises';
import path from 'node:path';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const runtimeRequire=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(runtimeRequire.resolve('@oai/artifact-tool')).href);
const base=process.cwd();
const out=path.join(base,'tmp','engranes');
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(path.join(base,'Calculos','EXCEL ENGRANES.xlsx')));
const mode=process.argv[2]||'inspect';
if(mode==='inspect') {
  console.log((await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000})).ndjson);
  const p=await wb.render({sheetName:'Etapa1',range:'C5:G17',scale:1.5,format:'png'});
  await fs.writeFile(path.join(out,'antes.png'),new Uint8Array(await p.arrayBuffer()));
} else {
  const changes={Etapa1:{E17:'=E13*TAN(RADIANS(E15))',F17:'=F13*TAN(RADIANS(F15))',E37:'=F8/E8'},'Etapa 2':{E10:'=Etapa1!F10',E12:'=Etapa1!E12*0.98',F12:'=E12',E37:'=F8/E8'}};
  for(const [name,cells] of Object.entries(changes)) {
    const sheet=wb.worksheets.getItem(name);
    for(const [cell,formula] of Object.entries(cells)) sheet.getRange(cell).formulas=[[formula]];
  }
  wb.recalculate();
  for(const name of ['Etapa1','Etapa 2']) {
    console.log((await wb.inspect({kind:'table',range:`'${name}'!C35:G43`,include:'values,formulas',tableMaxRows:9,tableMaxCols:5,maxChars:5000})).ndjson);
    const p=await wb.render({sheetName:name,range:'C5:G17',scale:1.5,format:'png'});
    await fs.writeFile(path.join(out,name==='Etapa1'?'despues1.png':'despues2.png'),new Uint8Array(await p.arrayBuffer()));
  }
  console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:50},maxChars:3000})).ndjson);
  const exported=await SpreadsheetFile.exportXlsx(wb);
  await exported.save(path.join(out,'recalculado.xlsx'));
  await fs.writeFile(path.join(out,'cambios.json'),JSON.stringify(changes,null,2));
}
