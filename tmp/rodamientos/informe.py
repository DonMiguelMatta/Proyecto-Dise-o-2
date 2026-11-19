from pathlib import Path
import json
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak
from reportlab.lib.styles import getSampleStyleSheet,ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import pypdfium2 as pdf

d=json.loads(Path('outputs/rodamientos_caja/calculo.json').read_text(encoding='utf-8'));rs=d['rows']
out=Path('output/pdf');out.mkdir(parents=True,exist_ok=True)
pdfmetrics.registerFont(TTFont('Arial','C:/Windows/Fonts/arial.ttf'))
pdfmetrics.registerFont(TTFont('ArialB','C:/Windows/Fonts/arialbd.ttf'))
pdfmetrics.registerFontFamily('Arial',normal='Arial',bold='ArialB',italic='Arial',boldItalic='ArialB')
ss=getSampleStyleSheet()
ss.add(ParagraphStyle(name='BodyA',fontName='Arial',fontSize=9,leading=13,spaceAfter=8))
ss.add(ParagraphStyle(name='HeadA',fontName='ArialB',fontSize=15,leading=19,textColor=colors.HexColor('#173e52'),spaceAfter=12))
ss.add(ParagraphStyle(name='SubA',fontName='ArialB',fontSize=10.5,leading=14,spaceBefore=8,spaceAfter=7))
ss.add(ParagraphStyle(name='CellA',fontName='Arial',fontSize=8,leading=10))
story=[]
def p(t):story.append(Paragraph(t,ss['BodyA']))
def h(t):story.append(Paragraph(t,ss['HeadA']))
def sub(t):story.append(Paragraph(t,ss['SubA']))
def table(data,widths):
 t=Table([[Paragraph(str(c),ss['CellA']) for c in row] for row in data],colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#dcecf1')),('VALIGN',(0,0),(-1,-1),'TOP'),('LINEBELOW',(0,0),(-1,0),.7,colors.HexColor('#45829a')),('LINEBELOW',(0,1),(-1,-1),.25,colors.HexColor('#d4dee2')),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7)]))
 story.append(t);story.append(Spacer(1,10))
def new():story.append(PageBreak())

h('Rodamientos de la caja reductora')
p('Selección preliminar calculada • Taladro de mesa • 18/11/2026')
p('<b>Criterio solicitado:</b> 50,000 h de vida combinada de los seis apoyos. Se interpreta como vida básica L10 del conjunto: probabilidad de supervivencia del conjunto del 90 %, bajo independencia de fallas por fatiga. No equivale a asignar 50,000 h a cada rodamiento.')
table([['Apoyo','NTN propuesto','d × D × ancho total (mm)','C / C0 (kN)']]+[[r['shaft']+' '+r['position'],r['number'],f"{r['d_mm']} × {r['D_mm']} × {r['B_mm']}",f"{r['C_kN']:.2f} / {r['C0_kN']:.2f}"] for r in rs],[65,115,170,155])
p('<b>Distribución:</b> ejes 1 y 2 con apoyo superior libre axialmente y apoyo inferior localizador. Eje 3 con dos rodamientos de rodillos cónicos opuestos, disposición DB, para resistir empuje en ambos sentidos. El inferior B recibe el empuje de perforación hacia arriba; la orientación de las pistas debe corresponder a esa reacción.')
sub('Resultado calculado')
p(f"Vida conjunta conservadora: <b>{d['L_joint_conservative_h']:,.0f} h &gt; 50,000 h</b>. Factor estático mínimo: <b>{min(r['S0'] for r in rs):.2f}</b>. El apoyo que limita la vida es G del Eje 2, no el husillo.")
p('<b>Alcance:</b> cumple las comprobaciones de fatiga y capacidad estática del modelo declarado. La selección queda condicionada a las masas actuales, el ciclo real, la carga mínima, la lubricación y el montaje. No se ha cambiado el Excel ni se autorizan aquí los nuevos diámetros de los ejes.')
sub('Datos de partida')
p('Motor 0.5 hp a 1800 rpm; reducciones 3:1 y 3:1; velocidades 1800, 600 y 200 rpm. Engranajes rectos: 20° y PD = 9.5. Reacciones obtenidas de las geometrías y resultados de Eje 1, Eje 2 y Eje 3 del libro CALCULADORA EJES.xlsx; se descartan los datos de ejemplo de la pestaña rodamientos.')

new();h('Cargas y ciclo adoptado')
p('Se conservan las reacciones radiales del diseño actual. El peso del motor se transmite a su soporte; se supone acople flexible sin carga radial adicional significativa. Se añaden las cargas gravitatorias de las piezas giratorias a los apoyos localizadores.')
table([['Apoyo','Fr nominal (N)','Fr arranque (N)','Fa nominal envolvente (N)','Fa pico envolvente (N)']]+[[r['shaft']+' '+r['position'],f"{r['Fr_nom_N']:.1f}",f"{r['Fr_start_N']:.1f}",f"{r['Fa_nom_bound_N']:.1f}",f"{r['Fa_start_bound_N']:.1f}"] for r in rs],[65,95,95,125,125])
p('<b>Pesos provisionales:</b> se reutilizan como cota de diseño las masas CAD antiguas de los engranajes PD = 6, más 1 kg supuesto por eje y herrajes. Resultan 26.19, 179.65 y 207.13 N para los ejes 1, 2 y 3. No son las masas verificadas de los engranajes actuales PD = 9.5; deben reemplazarse por el CAD actualizado.')
p('<b>Empuje del husillo:</b> 804 N nominales, procedentes de la estimación previa de corte, y 9,500 N como caso axial extremo previo del mecanismo manual. No se deducen del peso de la mesa. El segundo valor es una envolvente propuesta, no un límite físico garantizado sin limitador de esfuerzo.')
p('<b>Ciclo supuesto para esta memoria:</b> 20 arranques por hora, de 1 s cada uno, con velocidad media de 0.5 veces la nominal; 3580 s/h a velocidad nominal. Se aplica conservadoramente toda la carga de arranque y el empuje extremo durante esos pulsos. No se supone que el empuje extremo actúe continuamente. Los empujes de peso sin corte también se verifican por separado.')
p('Fracción de revoluciones con carga pico: f = (20 × 1 × 0.5)/(3580 + 20 × 1 × 0.5) = 0.0027855. Velocidades medias: 1795, 598.33 y 199.44 rpm. Si el ciclo real produce más revoluciones bajo empuje extremo, se debe recalcular la vida.')
sub('Cargas equivalentes según NTN / método de Shigley')
p('Bolas: P = Fr cuando Fa/Fr ≤ e; en el otro caso P = 0.56 Fr + Y Fa. Se interpolan e e Y con f0 Fa/C0. Estática: P0 = máx(Fr, 0.6 Fr + 0.5 Fa).')
p('Rodillos cónicos: P = Fr cuando Fa/Fr ≤ e; en el otro caso P = 0.4 Fr + Y Fa. Estática: P0 = máx(Fr, 0.5 Fr + Y0 Fa). Se incluyen empujes inducidos S = Fr/(2Y), con equilibrio del par sin precarga: FaB = máx(SB, SG + Fexterna); FaG = FaB - Fexterna. Se verifica la envolvente de corte sin crédito de peso, corte menos peso y peso sin corte.')

new();h('Vida conjunta y comprobación estática')
p('P_eq = [(1 - f) Pnom^p + f Ppico^p]^(1/p), ponderado por revoluciones. Se adopta un margen de carga fw = 1.20 para dimensionar: Pd = fw P_eq. Este margen se declara para rodamientos y no modifica el Ko de engranajes.')
p('L10h = [10^6/(60 nmedia)] (C/Pd)^p; p = 3 para bolas y p = 10/3 para rodillos. C y P deben expresarse en las mismas unidades. S0 = C0/[1.20 × máx(P0nom, P0pico)].')
table([['Apoyo','P_eq (N)','Pd (N)','L10 individual (h)','S0']]+[[r['shaft']+' '+r['position'],f"{r['P_eq_N']:.1f}",f"{r['P_design_N']:.1f}",f"{r['L10_h']:,.0f}",f"{r['S0']:.2f}"] for r in rs],[65,95,95,155,95])
p('<b>Combinación:</b> NTN da exponentes de dispersión e = 10/9 para bolas y 9/8 para rodillos. Con fallas independientes se resuelve Σ(t/Li)^ei = 1. Así Rconjunto(t) = exp[ln(0.9) Σ(t/Li)^ei].')
p(f"La solución con exponentes distintos es {d['L_joint_h']:,.0f} h. Para informar una cota conservadora se usa e = 10/9 en los seis: Lconjunto = [Σ Li^(-10/9)]^(-9/10) = <b>{d['L_joint_conservative_h']:,.0f} h</b>. Es una cota porque t es menor que cada vida individual y 10/9 es el menor exponente.")
p('Comprobación de escala: asignar por igual las vidas exigiría Li = 50,000 × 6^(9/10) = 250,788 h para seis apoyos con e = 10/9. No se exige igualdad; la comprobación conjunta admite vidas individuales diferentes.')
p('Comprobaciones adicionales: todos satisfacen 1.20 Ppico ≤ 0.5 C, condición de aplicabilidad del cálculo básico indicada por NTN. Se obtienen S0 ≥ 2 en bolas y S0 ≥ 3 en cónicos, usando el criterio conservador de precisión y suavidad de marcha de la tabla estática del catálogo.')
p(f"Sensibilidad ilustrativa: si todas las vidas se redujeran por un factor 0.50, la cota conjunta bajaría a {0.5*d['L_joint_conservative_h']:,.0f} h. Este factor no es un a3 determinado para la caja: faltan temperatura, viscosidad y limpieza. La vida básica no incluye automáticamente esas condiciones.")

new();h('Ajustes de montaje que requiere la propuesta')
table([['Zona','Asiento anterior','Asiento propuesto','Comprobación de montaje']],[55,90,100,260]) if False else None
table([['Zona','Asiento anterior','Asiento propuesto','Comprobación de montaje'],['Eje 1 B/G','0.500 in','12 mm','6001: hombro de apoyo ≥ 14 mm; radio ≤ 0.30 mm. Los hombros actuales adyacentes permiten ese apoyo.'],['Eje 2 A','0.375 in','10 mm','6000: hombro ≥ 12 mm; radio ≤ 0.30 mm. Revisar el escalón y su resistencia con el asiento nuevo.'],['Eje 2 G','0.375 in','10 mm','6300: hombro entre 14 y 17 mm; radio ≤ 0.60 mm. F actual de 0.500 in es insuficiente; proponer F = 0.625 in.'],['Eje 3 G','0.500 in','15 mm','30302: cara principal de apoyo ≥ 20.5 mm; proponer separador local de 21 mm. Radio ≤ 1 mm.'],['Eje 3 B','0.625 in','20 mm','30304CA: cara principal de apoyo ≥ 28.5 mm; proponer separador desmontable de 29 mm y radio ≤ 1.5 mm.']],[55,90,100,260])
p('Para Eje 3 B, C debe permitir el asiento y el montaje de 20 mm. El apoyo de 29 mm se propone desmontable: convertirlo en hombro integral mayor que el asiento del engranaje D de 1 in puede impedir introducir el engranaje. Verificar secuencia de montaje, tuerca y retención axial en ambos sentidos. Los límites db de NTN corresponden a otra cara y no son un intervalo único con da.')
p('Los centros efectivos adoptados, medidos desde el origen de cada bosquejo, son: Eje 1 B = 4.625 y G = 8.6583 in; Eje 2 A = 0.875 y G = 10.625 in; Eje 3 G = 0.625 y B = 4.875 in. Para los cónicos, ubicar los cuerpos teniendo en cuenta el centro de carga a = 9.5 y 13.5 mm del catálogo. Si esos centros cambian, deben actualizarse las reacciones.')
sub('Condiciones antes de cerrar la selección')
p('Carga mínima: varios apoyos trabajan con P &lt; 0.04 C0, advertencia de NTN A-70. Confirmar con NTN la carga mínima admisible en estas velocidades; la vida muy alta calculada no descarta deslizamiento. No se añade una precarga arbitraria: el modelo del par cónico usa precarga nula.')
p('Juego, ajuste y lubricación: cerrar tolerancias de eje/alojamiento y juego operativo con dilatación térmica y ajustes reales. Para una caja lubricada por aceite, garantizar alimentación a ambos niveles de rodamientos verticales; no basta suponer salpicadura. Determinar viscosidad a temperatura de trabajo, sellado y limpieza antes de asignar factores de vida modificada. No se fija aún un grado ISO VG ni un valor de precarga.')
p('La elección del rodamiento no valida por sí sola el extremo A del husillo frente al empuje de 9.50 kN. Los cambios de asientos y hombros requieren volver a comprobar los diámetros del eje, concentradores y montaje, conservando el flujo de cálculo de Shigley.')
sub('Referencias y trazabilidad')
p('Método: Shigley, diseño de rodamientos por vida, carga equivalente y capacidad estática; datos y factores numéricos tomados del catálogo NTN aportado. NTN: A-17 a A-20 (vida y estática), A-25/A-26 (cargas y pares), A-58/A-66/A-70 (juego, precarga, carga mínima), B-8/B-9 (bolas), B-142/B-143 (cónicos). Material de clase 13 y 14 usado como referencia; se mantiene el criterio del usuario de 50,000 h combinadas.')
p('Libro fuente: CALCULADORA EJES.xlsx, carpeta Proyecto/Calculos. Lectura sin cambios. SHA-256: '+d['source_sha256'][:32]+'... Registro reproducible: outputs/rodamientos_caja/calculo.json y tmp/rodamientos/calcular_caja.py.')

def footer(c,doc):
 c.setFont('Arial',8);c.setFillColor(colors.HexColor('#496471'));c.drawString(45,27,'Taladro de mesa | Selección preliminar de rodamientos');c.drawRightString(A4[0]-45,27,str(doc.page))
path=out/'Calculo_rodamientos_caja.pdf'
SimpleDocTemplate(str(path),pagesize=A4,rightMargin=45,leftMargin=45,topMargin=42,bottomMargin=45,title='Cálculo de rodamientos de la caja reductora',author='Proyecto Diseño 2').build(story,onFirstPage=footer,onLaterPages=footer)
f=pdf.PdfDocument(str(path));print('pages',len(f))
for i in range(len(f)):f[i].render(scale=1.3).to_pil().save(f'tmp/rodamientos/informe_{i+1}.png')
