import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'import_eje3.xlsx'));
const s=w.worksheets.getItem('Eje 3');
if(process.argv[2]==='antes'){
 const p=await w.render({sheetName:s.name,range:'A5:J28',scale:1.3,format:'png'});await fs.writeFile(dir+'eje3_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const values={},formulas={};
 const v=(a,x)=>{values[a]=x;delete formulas[a];};
 const f=(a,x)=>{formulas[a]=x;delete values[a];};
 // Replace the inherited Eje 1 helper table, retaining its location and formatting.
 for(let r=17;r<=25;r++)for(let c=18;c<=26;c++)v(String.fromCharCode(64+c)+r,null);
 v('R2','Eje 3: geometría y cargas');
 [['R3','L total (in)'],['R4','Apoyo G (in)'],['R5','Rueda D (in)'],['R7','Apoyo B (in)'],['R8','L apoyos (in)']].forEach(([a,x])=>v(a,x));
 v('S3',9.283333333333333);v('S4',.625);v('S5',2.7);v('S7',4.658333333333333);f('S8','=S7-S4');
 v('S9','Nominal');v('U9','Arranque');
 v('R10','Wt (lbf)');v('R11','Wr (lbf)');
 for(const [a,formula] of Object.entries({S10:"='INICIAR P1'!H25",U10:"='INICIAR P1'!H31",S11:"='INICIAR P1'!H26",U11:"='INICIAR P1'!H32"}))f(a,formula);
 ['RG_t (lbf)','RB_t (lbf)','RG_r (lbf)','RB_r (lbf)'].forEach((x,k)=>v('R'+(12+k),x));
 for(const c of ['S','U']){
  f(c+'12',`=${c}10*($S$7-$S$5)/$S$8`);
  f(c+'13',`=${c}10-${c}12`);
  f(c+'14',`=${c}11*($S$7-$S$5)/$S$8`);
  f(c+'15',`=${c}11-${c}14`);
 }
  const heads=['Sección','x (in)','Elemento','Mxy nom.','Mxz nom.','Mres nom.','T nom.','Mres arr.','T arr.'];
 heads.forEach((x,k)=>v(String.fromCharCode(82+k)+'17',x));
 const positions=[1.25,1.45,1.7,2.7,3.7,4.033333333333333,5.283333333333333];
 for(let k=0;k<7;k++){
  const c=String.fromCharCode(68+k),r=18+k,section='GFEDCBA'[k],keyed=k===3;
  v('R'+r,section);v('S'+r,positions[k]);v('T'+r,keyed?'Cuñero':'Hombro');
  f('U'+r,`=IF(S${r}>=$S$7,0,$S$12*(S${r}-$S$4)-$S$10*MAX(0,S${r}-$S$5))`);
  f('V'+r,`=IF(S${r}>=$S$7,0,$S$14*(S${r}-$S$4)-$S$11*MAX(0,S${r}-$S$5))`);
  f('W'+r,`=SQRT(U${r}^2+V${r}^2)`);
  f('X'+r,k>=3?"='INICIAR P1'!$F$12":'=0');
  f('Y'+r,`=IF(S${r}>=$S$7,0,SQRT(($U$12*(S${r}-$S$4)-$U$10*MAX(0,S${r}-$S$5))^2+($U$14*(S${r}-$S$4)-$U$11*MAX(0,S${r}-$S$5))^2))`);
  f('Z'+r,k>=3?"='INICIAR P1'!$F$13":'=0');
  v(c+'5',section);f(c+'7',`=$W$${r}`);f(c+'8',`=-${c}7`);f(c+'10',`=$X$${r}`);f(c+'11',`=${c}10`);
  v(c+'20',keyed?'Cuñero fresado':'Hombro agudo');v(c+'21',keyed?2.2:2.7);v(c+'24',keyed?3:2.2);v(c+'22',1);v(c+'25',1);
  f(c+'27',`=1+${c}22*(${c}21-1)`);f(c+'28',`=1+${c}25*(${c}24-1)`);
  v(c+'62',keyed?'Cuñero fresado':'Hombro agudo');f(c+'63',`=${c}21`);v(c+'64',1);f(c+'66',`=${c}24`);v(c+'67',1);
  v(c+'58',null);v(c+'80',null);v(c+'31',1);
  const oldkb=s.getRange(c+'72').formulas[0][0];f(c+'72',`=IF(ISNUMBER(${c}58),${oldkb.slice(1)},"")`);
  f(c+'73',`=IF(ISNUMBER(${c}72),${c}121*${c}72*${c}128*${c}138*${c}153*${c}167,"")`);
  f(c+'59',k?`=IF(AND(ISNUMBER(${c}58),ISNUMBER(${String.fromCharCode(67+k)}58)),MAX(${c}58,${String.fromCharCode(67+k)}58)/MIN(${c}58,${String.fromCharCode(67+k)}58),"")`:'="—"');
  f(c+'60',`=IF(ISNUMBER(${c}58),(PI()*${c}58^3)/16*(${c}45/${c}48+${c}46/${c}15)^-1,"Pendiente")`);
  f(c+'78',`=IF(ISNUMBER(${c}73),((16*${c}17)/PI()*(${c}75/${c}73+${c}76/${c}15))^(1/3),"")`);
  f(c+'81',k?`=IF(AND(ISNUMBER(${c}80),ISNUMBER(${String.fromCharCode(67+k)}80)),MAX(${c}80,${String.fromCharCode(67+k)}80)/MIN(${c}80,${String.fromCharCode(67+k)}80),"")`:'="—"');
  f(c+'82',`=IF(AND(ISNUMBER(${c}80),ISNUMBER(${c}73)),(PI()*${c}80^3)/16*(${c}75/${c}73+${c}76/${c}15)^-1,"Pendiente")`);
  f(c+'86',`=IF(ISNUMBER(${c}80),SQRT((${c}63*32*${c}7/(PI()*${c}80^3))^2+3*(${c}66*16*${c}10/(PI()*${c}80^3))^2),"")`);
  f(c+'87',`=IF(ISNUMBER(${c}86),${c}16/${c}86,"")`);
  v(c+'90',section);f(c+'91',"='INICIAR P1'!$F$13/'INICIAR P1'!$F$12");f(c+'92',`=$Y$${r}`);f(c+'93',`=$Z$${r}`);
  f(c+'94',`=IF(ISNUMBER(${c}80),32*${c}63*${c}92/(PI()*${c}80^3),"")`);
  f(c+'95',`=IF(ISNUMBER(${c}80),16*${c}66*${c}93/(PI()*${c}80^3),"")`);
  f(c+'96',`=IF(ISNUMBER(${c}80),SQRT(${c}94^2+3*${c}95^2),"")`);
  f(c+'97',`=IF(ISNUMBER(${c}96),${c}16/${c}96,"")`);f(c+'98',`=${c}17`);
  f(c+'99',`=IF(ISNUMBER(${c}97),IF(${c}97>=${c}98,"CUMPLE","NO CUMPLE"),"Elegir diámetro")`);
 }
 const weights=[1.2,1.2**2,1.2**3,1.2**2,1.2,1,1/1.2];
 const bound='MAX('+weights.map((x,k)=>String.fromCharCode(68+k)+'53/'+x).join(',')+')';
 for(let k=0;k<7;k++)f(String.fromCharCode(68+k)+'55','='+bound+'*'+weights[k]);
 for(const [a,formula] of Object.entries({D56:'="—"',E56:'=E55/D55',F56:'=F55/E55',G56:'=F55/G55',H56:'=G55/H55',I56:'=H55/I55',J56:'=I55/J55'}))f(a,formula);
 v('R26','D: rueda de 60 dientes, ancho 2 in. Torque desde D hacia A.');
 v('R27','Kt/Kts preliminares Shigley; q=qs=1 hasta definir radios.');
 v('R28','Fila 55: estimación D/d=1.2; diámetros aún sin adoptar.');
 v('R29','Filas 58 y 80: elegir diámetros para activar comprobaciones.');
 v('R30','Solo cargas de engrane y torque. Empuje axial no incluido.');
 v('R31','Material de plantilla conservado. Primera iteración kb=1.');
 v('R32','Sección');v('R33','Longitud (in)');
 const lengths=[1.25,.2,.25,2,1/3,1.25,4];
 lengths.forEach((x,k)=>{v(String.fromCharCode(83+k)+'32','GFEDCBA'[k]);v(String.fromCharCode(83+k)+'33',x);});
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
 console.log((await w.inspect({kind:'table',range:"'Eje 3'!R18:Z24",tableMaxRows:7,tableMaxCols:9,maxChars:2500})).ndjson);
 console.log((await w.inspect({kind:'table',range:"'Eje 3'!D53:J55",tableMaxRows:3,tableMaxCols:7,maxChars:1600})).ndjson);
 console.log((await w.inspect({kind:'match',sheetId:s.name,range:'D5:J99',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!',options:{useRegex:true,maxResults:15},maxChars:1800})).ndjson);
 for(const [name,range] of [['eje3_cargas','A5:J28'],['eje3_geometria','R2:Z33'],['eje3_diametros','A51:J87'],['eje3_arranque','A89:J99']]){
  const p=await w.render({sheetName:s.name,range,scale:1.25,format:'png'});await fs.writeFile(dir+name+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(w)).save(dir+'export_eje3.xlsx');
 await fs.writeFile(dir+'cambios_eje3.json',JSON.stringify({values,formulas}));
}
