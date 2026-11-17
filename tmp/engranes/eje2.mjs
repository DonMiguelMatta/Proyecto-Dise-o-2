import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_eje2.xlsx'));
const s=w.worksheets.getItem('Eje 2');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'A5:J28',scale:1.3,format:'png'});await fs.writeFile(dir+'eje2_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={},formulas={};
 const v=(a,x)=>{values[a]=x;delete formulas[a];};
 const f=(a,x)=>{formulas[a]=x;delete values[a];};
 // Replace the inherited Eje 1 helper table, retaining its location and formatting.
 for(let r=17;r<=25;r++)for(let c=18;c<=26;c++)v(String.fromCharCode(64+c)+r,null);
 v('R2','Eje 2: geometría y cargas');
 [['R3','L total (in)'],['R4','Apoyo A (in)'],['R5','Rueda C (in)'],['R6','Piñón E (in)'],['R7','Apoyo G (in)'],['R8','L apoyos (in)']].forEach(([a,x])=>v(a,x));
 v('S3',11.5);v('S4',.875);v('S5',3.25);v('S6',8);v('S7',10.625);f('S8','=S7-S4');
 v('S9','C nom.');v('T9','E nom.');v('U9','C arr.');v('V9','E arr.');
 v('R10','Wt (lbf)');v('R11','Wr (lbf)');
 for(const [a,formula] of Object.entries({S10:"='INICIAR P1'!F25",T10:"='INICIAR P1'!G25",U10:"='INICIAR P1'!F31",V10:"='INICIAR P1'!G31",S11:"='INICIAR P1'!F26",T11:"=-'INICIAR P1'!G26",U11:"='INICIAR P1'!F32",V11:"=-'INICIAR P1'!G32"}))f(a,formula);
 ['RA_t (lbf)','RB_t (lbf)','RA_r (lbf)','RB_r (lbf)'].forEach((x,k)=>v('R'+(12+k),x));
 for(const [c,d] of [['S','T'],['U','V']]){
  f(c+'12',`=(${c}10*($S$7-$S$5)+${d}10*($S$7-$S$6))/$S$8`);
  f(c+'13',`=${c}10+${d}10-${c}12`);
  f(c+'14',`=(${c}11*($S$7-$S$5)+${d}11*($S$7-$S$6))/$S$8`);
  f(c+'15',`=${c}11+${d}11-${c}14`);
 }
 const heads=['Sección','x (in)','Elemento','Mxy nom.','Mxz nom.','Mres nom.','T nom.','Mres arr.','T arr.'];
 heads.forEach((x,k)=>v(String.fromCharCode(82+k)+'17',x));
 const positions=[1.75,2.25,3.25,7,8,9.25,9.75];
 for(let k=0;k<7;k++){
  const c=String.fromCharCode(68+k),r=18+k,section='ABCDEFG'[k],keyed=k===2||k===4;
  v('R'+r,section);v('S'+r,positions[k]);v('T'+r,keyed?'Cuñero':'Hombro');
  f('U'+r,`=$S$12*(S${r}-$S$4)-$S$10*MAX(0,S${r}-$S$5)-$T$10*MAX(0,S${r}-$S$6)`);
  f('V'+r,`=$S$14*(S${r}-$S$4)-$S$11*MAX(0,S${r}-$S$5)-$T$11*MAX(0,S${r}-$S$6)`);
  f('W'+r,`=SQRT(U${r}^2+V${r}^2)`);
  f('X'+r,k>=2&&k<=4?"='INICIAR P1'!$E$12":'=0');
  f('Y'+r,`=SQRT(($U$12*(S${r}-$S$4)-$U$10*MAX(0,S${r}-$S$5)-$V$10*MAX(0,S${r}-$S$6))^2+($U$14*(S${r}-$S$4)-$U$11*MAX(0,S${r}-$S$5)-$V$11*MAX(0,S${r}-$S$6))^2)`);
  f('Z'+r,k>=2&&k<=4?"='INICIAR P1'!$E$13":'=0');
  v(c+'5',section);f(c+'7',`=$W$${r}`);f(c+'8',`=-${c}7`);f(c+'10',`=$X$${r}`);f(c+'11',`=${c}10`);
  v(c+'20',keyed?'Cuñero fresado':'Hombro agudo');v(c+'21',keyed?2.2:2.7);v(c+'24',keyed?3:2.2);v(c+'22',1);v(c+'25',1);
  f(c+'27',`=1+${c}22*(${c}21-1)`);f(c+'28',`=1+${c}25*(${c}24-1)`);
  v(c+'62',keyed?'Cuñero fresado':'Hombro agudo');f(c+'63',`=${c}21`);v(c+'64',1);f(c+'66',`=${c}24`);v(c+'67',1);
  v(c+'58',null);v(c+'80',null);
  const oldkb=s.getRange(c+'72').formulas[0][0];f(c+'72',`=IF(ISNUMBER(${c}58),${oldkb.slice(1)},"")`);
  f(c+'73',`=IF(ISNUMBER(${c}72),${c}121*${c}72*${c}128*${c}138*${c}153*${c}167,"")`);
  f(c+'59',k?`=IF(AND(ISNUMBER(${c}58),ISNUMBER(${String.fromCharCode(67+k)}58)),MAX(${c}58,${String.fromCharCode(67+k)}58)/MIN(${c}58,${String.fromCharCode(67+k)}58),"")`:'="—"');
  f(c+'60',`=IF(ISNUMBER(${c}58),(PI()*${c}58^3)/16*(${c}45/${c}48+${c}46/${c}15)^-1,"Pendiente")`);
  f(c+'78',`=IF(ISNUMBER(${c}73),((16*${c}17)/PI()*(${c}75/${c}73+${c}76/${c}15))^(1/3),"")`);
  f(c+'81',k?`=IF(AND(ISNUMBER(${c}80),ISNUMBER(${String.fromCharCode(67+k)}80)),MAX(${c}80,${String.fromCharCode(67+k)}80)/MIN(${c}80,${String.fromCharCode(67+k)}80),"")`:'="—"');
  f(c+'82',`=IF(AND(ISNUMBER(${c}80),ISNUMBER(${c}73)),(PI()*${c}80^3)/16*(${c}75/${c}73+${c}76/${c}15)^-1,"Pendiente")`);
  f(c+'86',`=IF(ISNUMBER(${c}80),SQRT((${c}63*32*${c}7/(PI()*${c}80^3))^2+3*(${c}66*16*${c}10/(PI()*${c}80^3))^2),"")`);
  f(c+'87',`=IF(ISNUMBER(${c}86),${c}16/${c}86,"")`);
  v(c+'90',section);f(c+'91',"='INICIAR P1'!$E$13/'INICIAR P1'!$E$12");f(c+'92',`=$Y$${r}`);f(c+'93',`=$Z$${r}`);
  f(c+'94',`=IF(ISNUMBER(${c}80),32*${c}63*${c}92/(PI()*${c}80^3),"")`);
  f(c+'95',`=IF(ISNUMBER(${c}80),16*${c}66*${c}93/(PI()*${c}80^3),"")`);
  f(c+'96',`=IF(ISNUMBER(${c}80),SQRT(${c}94^2+3*${c}95^2),"")`);
  f(c+'97',`=IF(ISNUMBER(${c}96),${c}16/${c}96,"")`);f(c+'98',`=${c}17`);
  f(c+'99',`=IF(ISNUMBER(${c}97),IF(${c}97>=${c}98,"CUMPLE","NO CUMPLE"),"Elegir diámetro")`);
 }
 f('G55','=MAX(G53,F53*1.2,H53*1.2,E53*1.2^2,I53*1.2^2,D53*1.2^3,J53*1.2^3)');
 for(const [a,formula] of Object.entries({F55:'=G55/1.2',E55:'=F55/1.2',D55:'=E55/1.2',H55:'=G55/1.2',I55:'=H55/1.2',J55:'=I55/1.2',D56:'="—"',E56:'=E55/D55',F56:'=F55/E55',G56:'=G55/F55',H56:'=G55/H55',I56:'=H55/I55',J56:'=I55/J55'}))f(a,formula);
 v('R26','C y E: sección del lado que transmite torque.');
 v('R27','Kt/Kts preliminares de Shigley; q=qs=1 conservador hasta definir radios.');
 v('R28','Fila 55: estimación automática con D/d=1.2; no son diámetros adoptados.');
 v('R29','Filas 58 y 80: seleccionar diámetros manuales para activar comprobaciones.');
 v('R30','Cargas de engranamiento; radiales opuestas. Apoyos y engranes según bosquejo.');
 v('R31','Propiedades del material y primera iteración kb=1 conservadas de la plantilla.');
 for(const [a,x] of Object.entries(values))s.getRange(a).values=[[x]];
 for(const [a,x] of Object.entries(formulas))s.getRange(a).formulas=[[x]];
 s.getRange('R17:Z24').setNumberFormat('0.000');
 s.getRange('S10:V15').setNumberFormat('0.000');
 for(const c of ['D','E','F','G','H','I','J']){
  s.getRange(c+'58').values=[[.5]];s.getRange(c+'80').values=[[.75]];
 }
 if(typeof s.getRange('H78').values[0][0]!=='number' || !(s.getRange('H97').values[0][0]>0))throw Error('No se activaron las comprobaciones al introducir diámetros de prueba');
 for(const c of ['D','E','F','G','H','I','J']){
  s.getRange(c+'58').values=[[null]];s.getRange(c+'80').values=[[null]];
 }
 w.recalculate();
 console.log((await w.inspect({kind:'table',range:"'Eje 2'!R18:Z24",tableMaxRows:7,tableMaxCols:9,maxChars:2500})).ndjson);
 console.log((await w.inspect({kind:'table',range:"'Eje 2'!D53:J55",tableMaxRows:3,tableMaxCols:7,maxChars:1600})).ndjson);
 console.log((await w.inspect({kind:'match',sheetId:s.name,range:'D5:J99',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:15},maxChars:1800})).ndjson);
 for(const [name,range] of [['eje2_cargas','A5:J28'],['eje2_geometria','R2:Z31'],['eje2_diametros','A51:J87'],['eje2_arranque','A89:J99']]){
  const p=await w.render({sheetName:s.name,range,scale:1.25,format:'png'});await fs.writeFile(dir+name+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_eje2.xlsx');
 await fs.writeFile(dir+'cambios_eje2.json',JSON.stringify({values,formulas}));
}
