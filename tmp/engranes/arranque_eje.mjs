import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_arr_eje.xlsx'));
const s=w.worksheets.getItem('Eje 1');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'A80:J100',scale:1.4,format:'png'});await fs.writeFile(dir+'arr_eje_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={A89:'Comprobación de arranque',A90:'Sección',E90:'B',G90:'D',J90:'G',A91:'Relación de torques',B91:'Tarr/Tnom',A92:'Momento de arranque',B92:'lb-in',A93:'Torque de arranque',B93:'lb-in',A94:'Esfuerzo de flexión de arranque',B94:'psi',A95:'Esfuerzo cortante de arranque',B95:'psi',A96:'Von Mises de arranque',B96:'psi',A97:'Seguridad contra fluencia',B97:'ny arr.',A98:'Factor de diseño requerido',B98:'nd',A99:'Comprobación',A100:'Kt y Kts: filas 63 y 66. Diámetros: fila 80. Resistencia Sy: fila 16.'};
 const formulas={};
 s.getRange('A89:J89').copyFrom(s.getRange('A85:J85'),'all');s.getRange('A89:J89').clear({applyTo:'contents'});
 s.getRange('A90:J90').copyFrom(s.getRange('A5:J5'),'all');s.getRange('A90:J90').clear({applyTo:'contents'});
 for(let r=91;r<=99;r++){
  s.getRange(`A${r}:J${r}`).copyFrom(s.getRange('A86:J86'),'all');s.getRange(`A${r}:J${r}`).clear({applyTo:'contents'});
 }
 for(const c of ['E','G','J']){
  formulas[c+'91']=c==='E'?"='INICIAR P1'!$D$13/'INICIAR P1'!$D$12":'=$E$91';
  formulas[c+'92']=`=MAX(ABS(${c}7),ABS(${c}8))*${c}91`;
  formulas[c+'93']=`=IF(MAX(ABS(${c}10),ABS(${c}11))>0,'INICIAR P1'!$D$13,0)`;
  formulas[c+'94']=`=32*${c}63*${c}92/(PI()*${c}80^3)`;
  formulas[c+'95']=`=16*${c}66*${c}93/(PI()*${c}80^3)`;
  formulas[c+'96']=`=SQRT(${c}94^2+3*${c}95^2)`;
  formulas[c+'97']=`=${c}16/${c}96`;
  formulas[c+'98']=`=${c}17`;
  formulas[c+'99']=`=IF(${c}97>=${c}98,"CUMPLE","NO CUMPLE")`;
 }
 for(const [a,v] of Object.entries(values))s.getRange(a).values=[[v]];
 for(const [a,f] of Object.entries(formulas))s.getRange(a).formulas=[[f]];
 for(const c of ['E','G','J'])s.getRange(`${c}91:${c}98`).setNumberFormat('0.00');
 w.recalculate();
 console.log((await w.inspect({kind:'table',range:"'Eje 1'!A91:J99",tableMaxRows:9,tableMaxCols:10,maxChars:2500})).ndjson);
 const p=await w.render({sheetName:s.name,range:'A85:J100',scale:1.4,format:'png'});await fs.writeFile(dir+'arr_eje_despues.png',new Uint8Array(await p.arrayBuffer()));
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_arr_eje.xlsx');
 await fs.writeFile(dir+'cambios_arr_eje.json',JSON.stringify({values,formulas}));
}
