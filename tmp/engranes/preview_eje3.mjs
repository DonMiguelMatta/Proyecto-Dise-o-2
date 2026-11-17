import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'preview_eje3.xlsx'));
const s=w.worksheets.getItem('Eje 3');
const p=await w.render({sheetName:s.name,range:'A89:J99',scale:1.1,format:'png'});await fs.writeFile(dir+'eje3_final.png',new Uint8Array(await p.arrayBuffer()));
