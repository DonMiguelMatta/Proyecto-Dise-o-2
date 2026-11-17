import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_cunas.xlsx'));
const s=w.worksheets.getItem('Cuña');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'B2:M19',scale:1.5,format:'png'});
 await fs.writeFile(dir+'cunas_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={B5:'Long. máxima',B6:'Factor de diseño',C8:'AISI 1020 CD',B13:'Torque arranque',G15:'lbf',B16:'Long. cubo disp.',G16:'in',B17:'N.º cuñas',B20:'Long. mínima',G20:'in',B21:'Long. elegida',G21:'in',B22:'n corte arr.',B23:'n aplast. arr.',B24:'Comprobación',H6:null,H12:null,H22:'Shigley, cap. 7: tabla 7-6 y comprobación por corte/aplastamiento.',H23:'AISI 1020 CD: Sy = 57 ksi; Ssy = 0.577 Sy. Cuñas de extremos rectos.',H24:'Una cuña por engrane. No incluye acople del motor ni unión del mandril.'};
 const formulas={};
 const sizes=[.1875,.1875,.1875,.25],Ls=[.5,.5,.5,.75],hubs=[1.5,1.5,2,2];
 const ds=["='Eje 1'!G80","='Eje 2'!F80","='Eje 2'!H80","='Eje 3'!G80"];
 const ts=["='INICIAR P1'!D13","='INICIAR P1'!E13","='INICIAR P1'!E13","='INICIAR P1'!F13"];
 const loc=['Eje 1 / D','Eje 2 / C','Eje 2 / E','Eje 3 / D'];
 for(let k=0;k<4;k++){
  const c='CDEF'[k];
  values[c+'1']=loc[k];values[c+'3']=sizes[k];values[c+'4']=sizes[k];values[c+'6']=1.2;
  values[c+'9']=57000;values[c+'10']=68000;values[c+'16']=hubs[k];values[c+'17']=1;values[c+'21']=Ls[k];
  formulas[c+'5']=`=MIN(${c}16,1.5*${c}14)`;
  formulas[c+'11']=`=0.577*${c}9`;
  formulas[c+'13']=ts[k];formulas[c+'14']=ds[k];
  formulas[c+'15']=`=2*${c}13/${c}14`;
  formulas[c+'18']=`=${c}15*${c}6/(${c}3*${c}11*${c}17)`;
  formulas[c+'19']=`=2*${c}15*${c}6/(${c}4*${c}9*${c}17)`;
  formulas[c+'20']=`=MAX(${c}18,${c}19)`;
  formulas[c+'22']=`=${c}11*${c}3*${c}21*${c}17/${c}15`;
  formulas[c+'23']=`=${c}9*${c}4*${c}21*${c}17/(2*${c}15)`;
  formulas[c+'24']=`=IF(AND(${c}22>=${c}6,${c}23>=${c}6,${c}21<=${c}5),"CUMPLE","REVISAR")`;
 }
 values.B6='F. diseño';values.B13='T arranque';values.B16='L cubo disp.';
 for(const [a,v] of Object.entries(values))s.getRange(a).values=[[v]];
 for(const [a,v] of Object.entries(formulas))s.getRange(a).formulas=[[v]];
 s.getRange('C20:F21').setNumberFormat('0.000');s.getRange('C22:F23').setNumberFormat('0.00');
 w.recalculate();
 console.log((await w.inspect({kind:'table',range:"'Cuña'!B13:G24",tableMaxRows:12,tableMaxCols:6,maxChars:3500})).ndjson);
 const p=await w.render({sheetName:s.name,range:'B1:G24',scale:1.6,format:'png'});
 await fs.writeFile(dir+'cunas_despues.png',new Uint8Array(await p.arrayBuffer()));
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_cunas.xlsx');
 await fs.writeFile(dir+'cambios_cunas.json',JSON.stringify({values,formulas}));
}
