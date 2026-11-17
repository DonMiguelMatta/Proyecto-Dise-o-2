import fs from 'node:fs/promises';
import {createRequire} from 'node:module';
import {pathToFileURL} from 'node:url';
const req=createRequire('C:/Users/migue/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/package.json');
const {FileBlob,SpreadsheetFile}=await import(pathToFileURL(req.resolve('@oai/artifact-tool')).href);
const dir='tmp/engranes/';
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(dir+'base_ejes_import.xlsx'));
if(process.argv[2]==='antes'){
 const p=await wb.render({sheetName:'INICIAR P1',range:'B2:F13',scale:1.5,format:'png'});
 await fs.writeFile(dir+'ejes_antes.png',new Uint8Array(await p.arrayBuffer()));
}else{
 const s=wb.worksheets.add('Entrada nominal y arranque');
 s.showGridLines=true;
 const v=(a,b)=>s.getRange(a).values=[[b]];
 const f=(a,b)=>s.getRange(a).formulas=[[b]];
 s.getRange('B2:F65').format.font={name:'Arial',size:10};
 s.getRange('B:B').format.columnWidth=46;
 s.getRange('C:C').format.columnWidth=14;
 s.getRange('D:E').format.columnWidth=20;
 s.getRange('F:F').format.columnWidth=96;
 s.getRange('B2:F65').format.rowHeight=21;
 s.getRange('D5:E65').setNumberFormat('0.000');
 v('B2','Eje de entrada: nominal y arranque');s.getRange('B2:F2').format.font={name:'Arial',size:14,bold:true};
 function band(range,label){v(range.split(':')[0],label);s.getRange(range).format={fill:'#FFFF00',font:{name:'Arial',size:10,bold:true,color:'#000000'}};}
 band('B4:E4','Datos comunes');
 const data={5:['Potencia del motor','hp',null],6:['Velocidad adoptada del motor','rpm',null],7:['Torque de arranque del motor','N·m',6.10],8:['Dientes del piñón','—',20],9:['Paso diametral','1/in',6],10:['Diámetro primitivo del piñón','in',null],11:['Ángulo de presión','°',20],12:['Longitud total del eje','in',5.5],13:['Centro del rodamiento A','in',2],14:['Centro del piñón','in',3.75],15:['Centro del rodamiento B','in',5],16:['Separación entre apoyos L','in',null],17:['Distancia A-piñón a','in',null],18:['Distancia piñón-B b','in',null]};
 for(const [row,[label,unit,value]] of Object.entries(data)){v('B'+row,label);v('C'+row,unit);if(value!==null)v('D'+row,value);}
 f('D5',"='INICIAR P1'!D3");f('D6',"='INICIAR P1'!D6");f('D10','=D8/D9');f('D16','=D15-D13');f('D17','=D14-D13');f('D18','=D15-D14');
 s.getRange('D7:D9').format.fill='#E2F0D9';s.getRange('D11:D15').format.fill='#E2F0D9';
 for(const r of [5,6,10,16,17,18])s.getRange('D'+r).format.fill='#DDEBF7';
 v('F5','Potencia y rpm vinculadas a INICIAR P1.');
 v('F7','Toshiba B1/24EMF2AOZ: torque de rotor bloqueado 6.10 N·m.');
 v('F8','https://www.mecampbell.com/media/pdf/TOSB1_24EMF2AOZ.pdf');
 v('F12','Cotas del bosquejo: origen en el extremo izquierdo; apoyos en sus centros.');
 v('F13','Apoyos simples; piñón entre A y B.');
 v('F14','Fuerzas aplicadas en el plano medio del piñón.');
 band('B20:E20','Cargas y resultados para MD Solids');
 v('D21','Nominal');v('E21','Arranque');s.getRange('D21:E21').format={fill:'#FFFF00',font:{bold:true,name:'Arial',size:10},horizontalAlignment:'center'};
 const labels={22:['Torque de entrada','N·m'],23:['Torque de entrada','lbf·in'],24:['Fuerza tangencial Wt','lbf'],25:['Fuerza radial Wr','lbf'],26:['Fuerza axial del engranamiento Wa','lbf'],27:['Reacción A, plano tangencial','lbf'],28:['Reacción B, plano tangencial','lbf'],29:['Reacción A, plano radial','lbf'],30:['Reacción B, plano radial','lbf'],31:['Reacción resultante A','lbf'],32:['Reacción resultante B','lbf'],33:['Momento tangencial en el piñón','lbf·in'],34:['Momento radial en el piñón','lbf·in'],35:['Momento flector resultante máximo','lbf·in'],36:['Comprobación de fuerzas tangenciales','lbf'],37:['Comprobación de fuerzas radiales','lbf'],38:['Comprobación de momentos tangenciales','lbf·in'],39:['Comprobación de momentos radiales','lbf·in']};
 for(const [r,[label,unit]] of Object.entries(labels)){v('B'+r,label);v('C'+r,unit);}
 for(const c of ['D','E']){
  f(c+'22',c==='D'?'=$D$5*745.699872/(2*PI()*$D$6/60)':'=$D$7');
  f(c+'23',`=${c}22/0.1129848290276167`);
  f(c+'24',`=2*${c}23/$D$10`);f(c+'25',`=${c}24*TAN(RADIANS($D$11))`);f(c+'26','=0');
  f(c+'27',`=${c}24*$D$18/$D$16`);f(c+'28',`=${c}24*$D$17/$D$16`);
  f(c+'29',`=${c}25*$D$18/$D$16`);f(c+'30',`=${c}25*$D$17/$D$16`);
  f(c+'31',`=SQRT(${c}27^2+${c}29^2)`);f(c+'32',`=SQRT(${c}28^2+${c}30^2)`);
  f(c+'33',`=${c}27*$D$17`);f(c+'34',`=${c}29*$D$17`);f(c+'35',`=SQRT(${c}33^2+${c}34^2)`);
  f(c+'36',`=${c}27+${c}28-${c}24`);f(c+'37',`=${c}29+${c}30-${c}25`);
  f(c+'38',`=${c}28*$D$16-${c}24*$D$17`);f(c+'39',`=${c}30*$D$16-${c}25*$D$17`);
 }
 s.getRange('D22:E39').format.fill='#DDEBF7';s.getRange('D35:E35').format.font={name:'Arial',size:10,bold:true};
 v('F23','Torsión aplicada por el acoplamiento; se retira en el piñón.');
 v('F24','Wt = 2T/dp; cargas hacia abajo en cada análisis plano independiente.');
 v('F25','Wr = Wt·tan(20°); plano perpendicular al tangencial.');
 v('F26','Engrane recto: Wa = 0. No incluye pesos ni cargas externas al engranamiento.');
 v('F33','Mt = RAt·a; Mr = RAr·a.');
 v('F35','M = √(Mt² + Mr²); máximo en x = 3.75 in para este modelo.');
 v('F36','Las cuatro comprobaciones de equilibrio deben ser cero.');
 band('B42:E42','Diagramas: valores por tramo');
 s.getRange('B43:E43').values=[['Coordenada x (in)','Diagrama','Nominal','Arranque']];s.getRange('B43:E43').format.fill='#FFFF00';
 const segments=[['0 ≤ x < 2','Vt',44],['2 < x < 3.75','Vt',45],['3.75 < x < 5','Vt',46],['5 < x ≤ 5.5','Vt',47],['0 ≤ x < 2','Vr',48],['2 < x < 3.75','Vr',49],['3.75 < x < 5','Vr',50],['5 < x ≤ 5.5','Vr',51],['0 ≤ x < 3.75','T',52],['3.75 < x ≤ 5.5','T',53]];
 for(const [x,kind,r] of segments){v('B'+r,x);v('C'+r,kind);for(const c of ['D','E']){
  const exp=r===45?`=${c}27`:r===46?`=-${c}28`:r===49?`=${c}29`:r===50?`=-${c}30`:r===52?`=${c}23`:'=0';f(c+r,exp);
 }}
 v('F44','Vt y Vr en lbf; T en lbf·in. Saltos en los puntos de carga y apoyo.');
 band('B56:E56','Ecuaciones de momento para reconstruir los diagramas');
 v('B57','0 ≤ x ≤ 2');v('D57','Mt = 0; Mr = 0');
 v('B58','2 ≤ x ≤ 3.75');v('D58','Mt = RAt·(x−2)');v('F58','Mr = RAr·(x−2). Coordenada x en pulgadas.');
 v('B59','3.75 ≤ x ≤ 5');v('D59','Mt = RBt·(5−x)');v('F59','Mr = RBr·(5−x).');
 v('B60','5 ≤ x ≤ 5.5');v('D60','Mt = 0; Mr = 0');
 v('B62','Referencia');v('D62','Shigley: análisis de fuerzas de engranajes y flexión de ejes.');
 v('F62','https://www.mechfamily-ju.com/storage/images/files/file_1731443577xeDvd.pdf');
 v('B63','Alcance');v('D63','Eje de entrada');v('F63','Cargas para diagramas; no modifica materiales, concentradores ni diámetros existentes.');
 s.getRange('D62:E62').merge();s.getRange('D62:E62').format.wrapText=true;s.getRange('B62:F62').format.rowHeight=32;
 s.getRange('D36:E39').conditionalFormats.add('cellIs',{operator:'between',formula:[-0.000001,0.000001],format:{font:{color:'#666666'}}});
 const wt=s.getRange('E24').values[0][0];v('D7',12.2);
 if(Math.abs(s.getRange('E24').values[0][0]/wt-2)>1e-10)throw Error('Sensibilidad del torque incorrecta');
 v('D7',6.1);wb.recalculate();
 console.log((await wb.inspect({kind:'table',range:"'Entrada nominal y arranque'!B22:E39",tableMaxRows:18,tableMaxCols:4,maxChars:3500})).ndjson);
 for(const [name,range] of [['ejes_datos','B2:E18'],['ejes_resultados','B20:E39'],['ejes_tramos','B42:F63']]){
  const p=await wb.render({sheetName:s.name,range,scale:1.5,format:'png'});await fs.writeFile(dir+name+'.png',new Uint8Array(await p.arrayBuffer()));
 }
 await (await SpreadsheetFile.exportXlsx(wb)).save(dir+'ejes_export.xlsx');
}
