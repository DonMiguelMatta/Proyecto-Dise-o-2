from pathlib import Path
import json,math,hashlib
root=Path.cwd();out=root/'outputs/memoria_latex';out.mkdir(parents=True,exist_ok=True)
src=json.loads(Path('tmp/rodamientos/fuentes_memoria.json').read_text(encoding='utf-8'))
bear=json.loads(Path('outputs/rodamientos_caja/calculo.json').read_text(encoding='utf-8'))
lift=json.loads(Path('outputs/elevacion_mesa/resultados.json').read_text(encoding='utf-8'))
flat={n:{s:{k:v for row in rows for k,v in row.items()} for s,rows in b['sheets'].items()} for n,b in src.items()}
def v(n,s,c):return flat[n][s].get(c,{}).get('v')
def e(s,c):return v('ejes',s,c)
def g(s,c):return v('engranes',s,c)
def fmt(x,p=3):return f'{x:.{p}f}' if isinstance(x,(int,float)) else str(x or '--')
parts=[]
def add(t):parts.append(t.strip()+'\n')
def table(headers,rows,align=None):
 headers=[x.replace('\t'+'imes',r'\times').replace('\b'+'ar',r'\bar') for x in headers]
 add(r'\begin{center}\small\begin{tabular}{'+(align or 'l'+'r'*(len(headers)-1))+r'}\toprule')
 add(' & '.join(headers)+r' \\ \midrule')
 for row in rows:add(' & '.join(str(x) for x in row)+r' \\')
 add(r'\bottomrule\end{tabular}\end{center}')
add(r'''\documentclass[11pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[spanish,es-nodecimaldot]{babel}
\usepackage[margin=22mm]{geometry}
\usepackage{amsmath,amssymb,booktabs,longtable,array,graphicx}
\usepackage[colorlinks=true,linkcolor=black,urlcolor=blue]{hyperref}
\setlength{\parindent}{0pt}
\setlength{\parskip}{5pt}
\setlength{\emergencystretch}{2em}
\renewcommand{\arraystretch}{1.16}
\newcommand{\inch}{\,\mathrm{in}}
\newcommand{\lbin}{\,\mathrm{lbf\,in}}
\newcommand{\lbf}{\,\mathrm{lbf}}
\newcommand{\rpm}{\,\mathrm{rpm}}
\newcommand{\ksi}{\,\mathrm{ksi}}
\title{Taladro de mesa\\Memoria de cálculos acumulados}
\author{Proyecto de Diseño 2}
\date{19 de noviembre de 2026}
\begin{document}
\maketitle
\textbf{Alcance.} Recopilación del estado calculado: transmisión, arranque, ejes, cuñas, elevación y rodamientos. Método resistente: Shigley \cite{shigley}; factores de rodamientos: NTN \cite{ntn}. Las propuestas aún no incorporadas al Excel se identifican por separado. No se incluyen resortes.

\textbf{Unidades.} Geometría y resistencia de la caja: pulgadas, lbf y psi. Cálculos de corte y empuje: SI. Rodamientos comerciales: dimensiones métricas de catálogo.
\[
1\lbf=4.44822\,\mathrm{N},\quad
1\lbin=0.112984829\,\mathrm{N\,m},\quad
1\,\mathrm{hp}=550\,\mathrm{ft\,lbf/s}.
\]
\textbf{Estado.} Las verificaciones corresponden a los supuestos indicados. No se presentan como calculados la columna, soldaduras, tornillos, rigidez de guías, freno ni conexión final del mandril.
\tableofcontents
\clearpage
\section{Motor, relaciones y potencia transmitida}
Motor de referencia: Toshiba B1/24EMF2AOZ. Se conservan las condiciones solicitadas de cálculo:
\[
P_1=0.5\,\mathrm{hp},\quad n_1=1800\rpm,\quad
i_1=i_2=\frac{60}{20}=3,\quad\eta_1=\eta_2=0.98.
\]
\begin{align*}
i_T&=i_1i_2=9, & n_2&=1800/3=600\rpm,\\
n_3&=600/3=200\rpm,\\
P_2&=0.5(0.98)=0.49\,\mathrm{hp},&&P_3&=0.49(0.98)=0.4802\,\mathrm{hp},\\
T&=\frac{P(550)(12)}{2\pi n/60}=\frac{63025.36P}{n}\lbin.
\end{align*}
El Excel de ejes redondea la constante a 63025; se conservan sus resultados.
''')
table(['Eje','$n$ (rpm)','$P$ (hp)','$T_{nom}$ (lbf in)','$T_{arr}$ (lbf in)'],[[i+1,e('INICIAR P1',c+'10'),fmt(e('INICIAR P1',c+'3'),4),fmt(e('INICIAR P1',c+'12')),fmt(e('INICIAR P1',c+'13'))] for i,c in enumerate('DEF')])
add(r'''\subsection{Envolvente de arranque}
Se adopta el par de arranque usado en los cálculos previos, no una potencia eléctrica aparente:
\begin{align*}
T_{1,arr}&=6.10\,\mathrm{N\,m}=53.98955\lbin,\\
T_{2,arr}&=53.98955(3)(0.98)=158.72928\lbin,\\
T_{3,arr}&=158.72928(3)(0.98)=466.66407\lbin,\\
k_{arr}&=T_{arr}/T_{nom}=3.08389.
\end{align*}
\[
P_{mec}=T\omega;\qquad\omega=0\ \Longrightarrow\ P_{mec}=0.
\]
El arranque se verifica por torque y esfuerzos. Un valor de kVA de arranque no es potencia mecánica transmitida. Se conserva 6.10 N m como dato de proyecto; no se reemplaza aquí por una curva par--velocidad medida.

\section{Tren de engranajes rectos}
\subsection{Geometría actual: PD = 9.5}
\begin{align*}
P_d&=9.5\,\mathrm{in}^{-1}, & \phi&=20^\circ,&\beta&=0^\circ,\\
d_p&=20/9.5=2.105263\inch,&d_g&=60/9.5=6.315789\inch,\\
a&=(d_p+d_g)/2=4.210526\inch,&p_c&=\pi/P_d=0.330694\inch,\\
h_a&=1/P_d=0.105263\inch,&h_f&=1.25/P_d=0.131579\inch,\\
d_{a,p}&=(20+2)/9.5=2.315789\inch,&d_{a,g}&=(60+2)/9.5=6.526316\inch.
\end{align*}
Anchos: etapa 1, $F=1.5\inch$; etapa 2, $F=2\inch$. El módulo anterior de 4.2333 mm correspondía a PD = 6 y fue sustituido por PD = 9.5.

\subsection{Cargas de dientes}
\[
V=\frac{\pi d_p n_p}{12},\qquad W_t=\frac{2T_p}{d_p},\qquad
W_r=W_t\tan20^\circ,\qquad W_a=0.
\]
''')
table(['Etapa','$V$ (ft/min)','$W_{t,nom}$','$W_{r,nom}$','$W_{t,arr}$','$W_{r,arr}$'],[[1,fmt(e('INICIAR P1','E23')),fmt(e('INICIAR P1','E25')),fmt(e('INICIAR P1','E26')),fmt(e('INICIAR P1','E31')),fmt(e('INICIAR P1','E32'))],[2,fmt(e('INICIAR P1','G23')),fmt(e('INICIAR P1','G25')),fmt(e('INICIAR P1','G26')),fmt(e('INICIAR P1','G31')),fmt(e('INICIAR P1','G32'))]])
add(r'''Las cuatro fuerzas de la tabla están en lbf. Diferencias menores de 0.001 lbf entre ambos libros provienen del redondeo de la constante de potencia.

\subsection{Factores AGMA empleados en el Excel}
Calidad adoptada $Q_v=7$; geometría $J_p=0.34$, $J_g=0.43$, $C_p=2300\sqrt{\mathrm{psi}}$, $K_m=1.18$, $K_B=C_f=K_T=K_R=C_H=1$.
\begin{align*}
B&=0.25(12-Q_v)^{2/3}=0.731004,\\
A&=50+56(1-B)=65.063752,\\
K_v&=\left(\frac{A+\sqrt V}{A}\right)^B,\\
K_s&=1.192\left(\frac{F\sqrt Y}{P_d}\right)^{0.0535},\\
I&=\frac{\cos\phi\sin\phi}{2}\frac{m_G}{m_G+1}=0.1205227,\\
N&=60nLq,\quad L=50000\,\mathrm{h},\quad q=1,\\
Y_N&=1.3558N^{-0.0178},\qquad Z_N=2.466N^{-0.056}.
\end{align*}
Se documentan los valores actuales del archivo: $K_o=1.5$ en etapa 1 y $K_o=1$ en etapa 2. No se adopta automáticamente el $K_o=2$ discutido anteriormente. La comprobación explícita del arranque usa su torque y $K_o=1$, evitando duplicar esa carga.
''')
gearrows=[]
for stage,s in enumerate(['Etapa1','Etapa 2'],1):
 for typ,c in [('Piñón','E'),('Rueda','F')]:gearrows.append([f'{stage} / {typ}',fmt(g(s,c+'16'),0),fmt(g(s,c+'27'),4),fmt(g(s,'E23'),4),fmt(g(s,c+'30'),4),fmt(g(s,c+'31'),4)])
table(['Etapa / pieza','$N$','$K_s$','$K_v$','$Y_N$','$Z_N$'],gearrows)
add(r'''\subsection{Flexión y contacto nominales}
\begin{align*}
\sigma_F&=W_tK_oK_vK_s\frac{P_d}{F}\frac{K_mK_B}{J},\\
\sigma_H&=C_p\sqrt{W_tK_oK_vK_s\frac{K_mC_f}{d_pFI}},\\
S_{t,req}&=\frac{n_F\sigma_FK_TK_R}{Y_N},\qquad
S_{c,req}=\frac{n_H\sigma_HK_TK_R}{Z_NC_H},\quad n_F=n_H=1.2.
\end{align*}
''')
table(['Etapa / pieza','$\sigma_F$ (ksi)','$\sigma_H$ (ksi)','$S_{t,req}$ (ksi)','$S_{c,req}$ (ksi)'],[[f'{st} / {typ}']+[fmt(g(s,c+str(r))/1000) for r in [40,41,38,39]] for st,s in enumerate(['Etapa1','Etapa 2'],1) for typ,c in [('Piñón','E'),('Rueda','F')]])
add(r'''Material de cálculo: acero endurecido por flama o inducción, 50 HRC, grado 1, con $S_t=22\ksi$ y $S_c=170\ksi$. La dureza superficial por sí sola no define las propiedades del núcleo del eje.

\subsection{Verificación explícita al arranque}
Mismas ecuaciones de esfuerzo, con $W_{t,arr}$ y $K_o=1$:
\[
S_F=\frac{S_tY_N}{\sigma_{F,arr}K_TK_R},\qquad
S_H=\frac{S_cZ_NC_H}{\sigma_{H,arr}K_TK_R}.
\]
''')
table(['Engrane','$\sigma_{F,arr}$ (ksi)','$\sigma_{H,arr}$ (ksi)','$S_F$','$S_H$'],[[i+1,fmt(g('Arranque',c+'43')/1000),fmt(g('Arranque',c+'44')/1000),fmt(g('Arranque',c+'45')),fmt(g('Arranque',c+'46'))] for i,c in enumerate('CDEF')])
add(r'''\[
\min S_F=6.460>1.2,\qquad\min S_H=2.618>1.2.
\]
Son factores AGMA bajo el modelo de carga indicado, no una prueba independiente de fluencia del núcleo. La vida de 50,000 h para dientes es la adoptada en el Excel; la vida combinada de rodamientos se comprueba aparte.

\subsection{Inercia y aceleración preliminares}
Las inercias siguientes corresponden al CAD anterior PD = 6. Se conservan como antecedente; no se presentan como inercias verificadas del dentado PD = 9.5.
\[
J_{eq}=\sum_iJ_i\left(\frac{n_i}{n_1}\right)^2.
\]
''')
table(['Engrane','$J$ (kg m$^2$)','$n_i/n_1$','$J$ referido (kg m$^2$)'],[[i-52,fmt(g('Arranque','D'+str(i)),9),fmt(g('Arranque','E'+str(i)),6),fmt(g('Arranque','F'+str(i)),9)] for i in range(53,57)])
add(r'''\begin{align*}
J_{eq}&=0.01726847\,\mathrm{kg\,m^2},\\
\alpha&=\frac{2\pi(1800)/60}{1}=188.4956\,\mathrm{rad/s^2},\\
T_{acel}&=J_{eq}\alpha=3.25503\,\mathrm{N\,m},\\
6.10/T_{acel}&=1.874.
\end{align*}
Modelo sin inercia del rotor, ejes, acople ni mandril; tampoco incluye torque de corte durante el arranque. El cociente no garantiza por sí solo un tiempo de aceleración de 1 s.
\clearpage
\section{Ejes de la caja: geometría y cargas}
\subsection{Dimensiones actuales del Excel}
Diámetros de la fila \texttt{d. iter 4 (manual)}; longitudes de los bosquejos aceptados. Los asientos comerciales propuestos más adelante todavía no sustituyen esta geometría.
''')
lengths=[[4,1.25,1/3,2,.25,.2,1.25],[1.75,.5,1.75,3,2.25,.5,1.75],[1.25,.25,.25,2.25,.25,1.25,4]]
for i in range(1,4):
 order='ABCDEFG' if i<3 else 'GFEDCBA'
 add(r'\subsubsection*{Eje '+str(i)+'}')
 table(['Sección','$d$ (in)','$L$ (in)'],[[s,fmt(e(f'Eje {i}',c+'80'),4),fmt(L,4)] for s,c,L in zip(order,'DEFGHIJ',lengths[i-1])])
 add(r'Longitud total: $L='+fmt(sum(lengths[i-1]),4)+r'\inch$.')
add(r'''\subsection{Modelo estático para MD Solids}
Para cada plano se resuelve por separado:
\begin{align*}
\sum F&=0,\qquad\sum M=0,\\
R_2&=\frac{\sum_jF_j(x_j-x_1)}{x_2-x_1},\qquad R_1=\sum_jF_j-R_2,\\
V(x)&=R_1H(x-x_1)+R_2H(x-x_2)-\sum_jF_jH(x-x_j),\\
M(x)&=R_1\langle x-x_1\rangle+R_2\langle x-x_2\rangle-\sum_jF_j\langle x-x_j\rangle,\\
M_R(x)&=\sqrt{M_{xy}(x)^2+M_{xz}(x)^2}.
\end{align*}
Los signos dependen de los ejes escogidos. En Eje 2 los engranajes están en lados opuestos: fuerzas tangenciales de signos opuestos y radiales del mismo signo. Las reacciones tabuladas siguen la convención de cálculo del libro.
''')
table(['Eje','$x_1$ (in)','$x_2$ (in)','Centros de engranajes (in)'],[[1,'4.6250 (B)','8.6583 (G)','6.5833'],[2,'0.8750 (A)','10.6250 (G)','3.2500 y 8.0000'],[3,'0.6250 (G)','4.8750 (B)','2.8750']], 'llll')
rad=math.hypot(e('INICIAR P1','E25'),e('INICIAR P1','E26'));a=4.625;b=8.6583333333333;x=6.5833333333333
reaction_rows=[]
for pos,factor in [('B',(b-x)/(b-a)),('G',(x-a)/(b-a))]:
 reaction_rows.append(['1 / '+pos,fmt(e('INICIAR P1','E25')*factor),fmt(e('INICIAR P1','E26')*factor),fmt(e('INICIAR P1','E31')*factor),fmt(e('INICIAR P1','E32')*factor)])
for n,positions in [(2,['A','G']),(3,['G','B'])]:
 for j,pos in enumerate(positions):reaction_rows.append([f'{n} / {pos}',fmt(e(f'Eje {n}','S'+str(12+j))),fmt(e(f'Eje {n}','S'+str(14+j))),fmt(e(f'Eje {n}','U'+str(12+j))),fmt(e(f'Eje {n}','U'+str(14+j)))])
table(['Eje / apoyo','$R_{t,nom}$','$R_{r,nom}$','$R_{t,arr}$','$R_{r,arr}$'],reaction_rows)
add('Reacciones en lbf. El arranque multiplica las cargas de engranajes por 3.08389; no multiplica el peso propio. No se incluyen aquí fuerzas de corte laterales ni empuje axial de perforación.')
for n,critical in [(1,['E','G','J']),(2,['D','F','H']),(3,['D','G','I'])]:
 add(r'\subsubsection*{Momentos y torque del Eje '+str(n)+'}')
 table(['Sección','$M_{nom}$ (lbf in)','$T_{nom}$ (lbf in)','$M_{arr}$ (lbf in)','$T_{arr}$ (lbf in)'],[[e(f'Eje {n}',c+'5')]+[fmt(e(f'Eje {n}',c+str(r))) for r in [7,10,92,93]] for c in critical])
add(r'''Se conservan los momentos introducidos en el libro. En Eje 1, las pequeñas diferencias respecto a $\sqrt{M_{xy}^2+M_{xz}^2}$ provienen del ingreso manual/redondeo de los diagramas. La salida G del Eje 1 y el extremo G del Eje 3 no transmiten torque en el tramo anterior al engranaje.

\section{Ejes: fatiga, iteraciones y arranque}
\subsection{Material y resistencia a fatiga}
\[
S_{ut}=95\ksi,\quad S_y=84.4\ksi,\quad S'_e=0.5S_{ut}=47.5\ksi,\quad n_d=1.2.
\]
Valores de proyecto del libro para AISI 1045 CD; no se reemplazan por propiedades certificadas de otro tratamiento.
\begin{align*}
k_a&=2.7(95)^{-0.265}=0.807731,\\
k_b&=1\quad\text{en la primera aproximación},\\
k_b&=0.879d^{-0.107}\quad(0.3\leq d\leq2\inch),\\
S_e&=k_ak_bk_ck_dk_eS'_e,\\
k_c&=1,\quad k_d=1.011954,\quad k_e=0.8684,\\
S_e(k_b=1)&=33.7164\ksi.
\end{align*}
Se reproducen $k_d$ y $k_e$ usados en el Excel ($120\,^{\circ}\mathrm F$, confiabilidad seleccionada 95\%). Para dimensiones menores de 0.3 in el libro toma $k_b=1$. No se interpreta el polinomio térmico como validación fuera de su intervalo de correlación.
\[
K_f=1+q(K_t-1),\qquad K_{fs}=1+q_s(K_{ts}-1).
\]
''')
criticalmap={1:['E','G','J'],2:['D','F','H'],3:['D','G','I']}
table(['Eje / sección','$K_t$','$q$','$K_f$','$K_{ts}$','$q_s$','$K_{fs}$'],[[f"{n} / {e(f'Eje {n}',c+'5')}"]+[fmt(e(f'Eje {n}',c+str(r)),3) for r in [63,64,69,66,67,70]] for n,cs in criticalmap.items() for c in cs])
add(r'''\subsection{Goodman con energía de distorsión}
\begin{align*}
M_m&=(M_{max}+M_{min})/2,&M_a&=(M_{max}-M_{min})/2,\\
T_m&=(T_{max}+T_{min})/2,&T_a&=(T_{max}-T_{min})/2,\\
A&=\sqrt{4(K_fM_a)^2+3(K_{fs}T_a)^2},\\
B&=\sqrt{4(K_fM_m)^2+3(K_{fs}T_m)^2},\\
d_{req}&=\left[\frac{16n_d}{\pi}\left(\frac A{S_e}+\frac B{S_{ut}}\right)\right]^{1/3},\\
n_f&=\frac{\pi d^3}{16}\left(\frac A{S_e}+\frac B{S_{ut}}\right)^{-1}.
\end{align*}
Flexión rotativa: $M_{max}=+M_R$, $M_{min}=-M_R$, por tanto $M_m=0$ y $M_a=M_R$. En marcha se tomó torque constante: $T_m=T_{nom}$, $T_a=0$. El pico de arranque se comprueba aparte por fluencia; eso no sustituye un espectro completo de fatiga por arranques.

\subsection{Iteraciones conservadas}
Iteración inicial: $k_b=1$, $q=q_s=1$. Luego se selecciona $d_2$, se recalculan $k_b$, $K_f$, $K_{fs}$ y $d_3$, y se escoge $d_4$ manualmente. Las demás secciones se fijan por geometría y relaciones $D/d$.
''')
table(['Eje / sec.','$d_{crit,1}$','$d_2$','$k_b(d_2)$','$d_3$','$d_4$'],[[f"{n} / {e(f'Eje {n}',c+'5')}"]+[fmt(e(f'Eje {n}',c+str(r)),4) for r in [53,58,72,78,80]] for n,cs in criticalmap.items() for c in cs])
add('Diámetros en in. El $n_f$ mostrado por el Excel conserva $k_b(d_2)$. Para distinguirlo de una comprobación del diámetro final se calcula además $n_f$ con $k_b(d_4)$, manteniendo los demás datos del libro:')
fatrows=[]
for n,cs in criticalmap.items():
 for c in cs:
  s=f'Eje {n}';diam=e(s,c+'80');kb=1 if diam<.3 else .879*diam**(-.107)
  se=e(s,c+'73')/e(s,c+'72')*kb
  nf=math.pi*diam**3/16/(e(s,c+'75')/se+e(s,c+'76')/e(s,c+'15'))
  fatrows.append([f"{n} / {e(s,c+'5')}",fmt(e(s,c+'82')),fmt(kb,4),fmt(se/1000),fmt(nf)])
table(['Eje / sec.','$n_f$ Excel','$k_b(d_4)$','$S_e(d_4)$ (ksi)','$n_f(d_4)$'],fatrows)
add(r'''\subsection{Fluencia por flexión y torsión}
\begin{align*}
\sigma_b&=\frac{32K_tM}{\pi d^3},&\tau&=\frac{16K_{ts}T}{\pi d^3},\\
\sigma_{VM}&=\sqrt{\sigma_b^2+3\tau^2},&n_y&=S_y/\sigma_{VM}.
\end{align*}
Para arranque se usan $M=M_{arr}$ y $T=T_{arr}$. Se conservan $K_t$ y $K_{ts}$ teóricos en la comprobación estática.
''')
table(['Eje / sección','$d_4$ (in)','$n_{y,nom}$ Excel','$n_{y,arr}$'],[[f"{n} / {e(f'Eje {n}',c+'5')}",fmt(e(f'Eje {n}',c+'80')),fmt(e(f'Eje {n}',c+'87')),fmt(e(f'Eje {n}',c+'97'))] for n,cs in criticalmap.items() for c in cs])
add(r'''Las secciones tabuladas cumplen $n_y\geq1.2$ bajo cargas de engranajes y torque. Las casillas sin análisis del libro no se interpretan como verificaciones favorables; tampoco se trasladan errores de división por cero de celdas no utilizadas.

\section{Cuñas de los cuatro engranajes}
Cuñas cuadradas/rectangulares de extremos rectos; una por engrane. Material AISI 1020 CD: $S_y=57\ksi$, $S_{sy}=0.577S_y=32.889\ksi$, $n_d=1.2$. Se usa torque de arranque.
\begin{align*}
F&=T/r=2T/d,\\
\tau&=\frac F{bL},\qquad \sigma_{ap}=\frac F{hL/2}=\frac{2F}{hL},\\
L_{corte}&=\frac{n_dF}{0.577S_yb},\qquad
L_{ap}=\frac{2n_dF}{S_yh},\\
L_{min}&=\max(L_{corte},L_{ap}),\\
n_{corte}&=\frac{0.577S_ybL}{F},\qquad n_{ap}=\frac{S_yhL}{2F}.
\end{align*}
''')
table(['Unión','$d$ (in)','$T_{arr}$ (lbf in)','$F$ (lbf)','$b\times h\times L$ (in)'],[[e('Cuña',c+'1'),fmt(e('Cuña',c+'14')),fmt(e('Cuña',c+'13')),fmt(e('Cuña',c+'15')),f"{fmt(e('Cuña',c+'3'))} $\\times$ {fmt(e('Cuña',c+'4'))} $\\times$ {fmt(e('Cuña',c+'21'))}"] for c in 'CDEF'])
table(['Cuña','$L_{corte}$ (in)','$L_{ap}$ (in)','$n_{corte}$','$n_{ap}$'],[[i+1]+[fmt(e('Cuña',c+str(r)),4 if r<20 else 3) for r in [18,19,23,24]] for i,c in enumerate('CDEF')])
add(r'''Las cuatro cumplen con $L=0.5\inch$. Se conserva la cuña de $1/4\times1/4\inch$ del libro: falta confirmar ancho comercial, profundidad real del cuñero y pared de cubo para cada diámetro. El aplastamiento del eje y cubo debe comprobarse con su propia resistencia. No se ha dimensionado una quinta cuña para el acople ni la unión del mandril.
\clearpage
\section{Mesa móvil y empuje sobre el husillo}
El husillo permanece fijo; sube la mesa. El peso de la mesa no determina por sí solo la fuerza de perforación:
\begin{align*}
m&=5.032+15=20.032\,\mathrm{kg},\\
W&=mg=20.032(9.81)=196.514\,\mathrm N,\\
F_{rack}&=W+F_{corte}+F_{\mathrm{guias}}+ma,\\
F_{husillo}&=F_{rack}-W-F_{\mathrm{guias}}-ma.
\end{align*}
Se consideran movimiento cuasiestático y rozamiento de guías pendiente. Deben añadirse las masas móviles de carro y cremallera cuando se conozcan.

\subsection{Caso ilustrativo de perforación calculado previamente}
El alcance inicial mencionaba aluminio y broca de 4 mm; el siguiente cálculo posterior es un \textbf{escenario ilustrativo distinto}: acero dulce, broca HSS de 10 mm, $k_c=2500\,\mathrm{N/mm^2}$, $f_n=0.15\,\mathrm{mm/rev}$ y semiángulo de punta $59^\circ$. No se declara como requisito definitivo de broca. Fórmulas de mecanizado de Sandvik \cite{sandvik}; resistencia de elementos por Shigley.
\begin{align*}
v_c&=\pi(0.010)(200)=6.283\,\mathrm{m/min},\\
v_f&=nf_n=200(0.15)=30\,\mathrm{mm/min},\\
T_c&=\frac{k_cD^2f_n}{8000}=4.6875\,\mathrm{N\,m},\\
P_c&=T_c\frac{2\pi n}{60}=98.175\,\mathrm W,\\
F_c&\simeq0.25k_cDf_n\sin59^\circ=803.594\,\mathrm N,\\
F_{rack,corte}&=803.594+196.514=1000.108\,\mathrm N.
\end{align*}
Potencia disponible aproximada: $0.4802\,\mathrm{hp}\simeq358\,\mathrm W$; torque disponible $17.097\,\mathrm{N\,m}>4.6875\,\mathrm{N\,m}$. El coeficiente de corte y avance son supuestos; falta validar broca, material, desgaste y fuerza real de avance.

\section{Elevación: manivela, piñón--cremallera y sinfín}
\subsection{Fuerza, eficiencia y recorrido}
Propuesta manual: brazo $R=4\inch$, fuerza máxima supuesta $F_m=20\lbf$, $i=20$, $\eta_r=0.95$, $\mu=0.10$, $\phi_n=20^\circ$, recorrido $10\inch$.
\begin{align*}
T_{in}&=F_mR=80\lbin,\\
\tan\lambda&=\frac{N_w}{P_t d_w},\quad N_w=1,\\
\eta_s&=\frac{\cos\phi_n-\mu\tan\lambda}{\cos\phi_n+\mu\cot\lambda},\\
T_{out}&=\eta_s i T_{in},\qquad F_{rack}=\frac{\eta_rT_{out}}{r_p},\\
\Delta y&=\frac{\pi d_p}{i},\quad N_{vueltas}=\frac{10}{\Delta y},\quad
F_{m,corte}=\frac{(F_c+W)r_p}{\eta_ri\eta_sR}.
\end{align*}
''')
table(['Parámetro','Propuesta inicial','Alternativa reforzada'],[
['Piñón cremallera','$18$ dientes, PD $12$','$18$ dientes, PD $6$'],['$d_p$ (in)','1.5','3'],['Sinfín / corona','$P_t=8$, $d_w=1.5$ in','$P_t=3$, $d_w=2.25$ in'],['$D_G$ (in)','2.5','6.6667'],['Centros (in)','2','4.4583'],['$\lambda$ (grados)','4.7636','8.4270'],['$\eta_s$','0.4353','0.5728'],['$\Delta y$ (in/vuelta)','0.23562','0.47124'],['Vueltas / 10 in','42.44','21.22'],['Manivela al cortar (rpm)','5.013','2.506'],['$F_{m,corte}$ (lbf)','5.097','7.747'],['$F_{husillo}$ con 20 lbf (kN)','3.728','2.385'],['$F_{rack,ideal}$ con 20 lbf (kN)','9.490','4.745']], 'lll')
add(r'''\textbf{Envolvente conservada de resistencia:} $F_d=9.50\,\mathrm{kN}$. Procede del límite ideal aproximado de la propuesta inicial a 20 lbf. Se conserva para comparar resistencia de la alternativa, aunque supera su fuerza ideal con la misma manivela. No es fuerza normal de corte ni un límite físico impuesto al operador.

Para la alternativa, $\mu=0.08/0.10/0.15$ produce $\eta_s=0.627/0.573/0.470$ y esfuerzo manual de corte aproximadamente $7.08/7.75/9.44\lbf$ sin rozamiento de guías.

\subsection{Resistencia del piñón y cremallera}
\[
W_t=\frac{9500}{4.44822}=2135.567\lbf,\quad
J=0.28,\quad I=\frac{\sin20^\circ\cos20^\circ}{2}=0.160697.
\]
Se usan las ecuaciones AGMA anteriores: $K_m=1.5$, $K_v=1.02$, $K_o=K_B=1$, $Y_N=Z_N=1$, factores de tamaño calculados. La carga ya es la envolvente de 9.50 kN.
''')
table(['Caso','$d_p$ / $F$ (in)','$S_t$ / $S_c$ (ksi)','$\sigma_F$ / $\sigma_H$ (ksi)','$S_F$ / $S_H$'],[[label,f"{r['d']:.2f} / {r['b']:.2f}",f"{r['St']/1000:.0f} / {r['Sc']/1000:.0f}",f"{r['bending_psi']/1000:.2f} / {r['contact_psi']/1000:.2f}",f"{r['SF']:.3f} / {r['SH']:.3f}"] for label,r in [('Inicial',lift['rack_initial']),('Reforzado',lift['rack_reinforced'])]])
add(r'''La propuesta inicial no cumple. Alternativa: piñón integral con eje, ancho $2.5\inch$, acero para carburizar grado AGMA 2, $S_t\geq65\ksi$, $S_c\geq225\ksi$, núcleo $S_y\geq77\ksi$, $S_{ut}\geq91\ksi$. Cremallera propuesta de 12 in para recorrido útil de 10 in; confirmar en CAD. El piñón integral no lleva cuña. $Y_N=Z_N=1$ corresponde a la referencia de $10^7$ ciclos; confirmar uso acumulado.

\subsection{Capacidad del sinfín y corona}
\begin{align*}
(W_t)_{adm}&=C_sD_G^{0.8}F_eC_mC_v,\qquad F_e\leq0.67d_w,\\
C_s&=720+10.37C^3\quad(C\leq3\inch);\qquad C_s=1000\quad(C>3\inch),\\
V_s&=\frac{\pi d_wn_w}{12\cos\lambda},\qquad
C_v=0.659e^{-0.0011V_s},\\
C_m&=\min\!\left[0.022\sqrt{-i^2+40i-76}+0.46,\right.\\
&\hspace{28mm}\left.0.0107\sqrt{-i^2+56i+5145}\right]=0.81944,\\
(W_t)_{req}&=\frac{2F_dr_p}{D_G}.
\end{align*}
''')
table(['Caso','$C_s$','$F_e$ (in)','$C_v$','Admisible (lbf)','Exigida (lbf)','Cociente'],[['Inicial',fmt(lift['initial_worm']['Cs'],2),'1',fmt(lift['initial_worm']['Cv'],4),fmt(lift['initial_worm']['Wallow_lbf'],1),fmt(lift['initial_worm']['Wt_required_lbf'],1),'0.698'],['Reforzado','1000','1.5',fmt(lift['revised_worm']['Cv'],4),fmt(lift['revised_worm']['Wallow_lbf'],1),fmt(lift['revised_worm']['Wt_required_3in_lbf'],1),'3.795']])
add(r'''El reforzado supera el cociente requerido 1.20. La correlación supone sinfín de acero con superficie $\geq58$ HRC y corona de bronce centrifugado apropiado. Es una clasificación empírica de desgaste, de referencia 25,000 h; su cociente no certifica automáticamente 50,000 h ni resistencia universal a choque.

\subsection{Ejes del mecanismo propuesto}
Núcleo mínimo $S_y=77\ksi$, $S_{ut}=91\ksi$, $k_e=0.897$. Se acotan fuerzas con $\mu=0.15$:
\begin{align*}
W_{t,G}&=2T_G/D_G,\\
W_N&=\frac{W_{t,G}}{\cos\phi_n\cos\lambda-\mu\sin\lambda},\\
W_{t,w}&=W_N(\cos\phi_n\sin\lambda+\mu\cos\lambda),\\
W_r&=W_N\sin\phi_n,\quad F_{a,G}=W_{t,w},\quad F_{a,w}=W_{t,G}.
\end{align*}
Eje corona--piñón: apoyos separados 7 in, corona a 1.75 in y piñón a 5 in. Sinfín: apoyos separados 6 in. Se suman conservadoramente fuerzas transversales y pares producidos por fuerzas axiales descentradas.
\[
T_G=F_d(1.5)=3203.527\lbin,\quad
F_{a,G}=302.954\lbf,\quad M_G\leq4770.149\lbin,
\]
\[
M_w\leq1789.462\lbin,\qquad d_{\mathrm{raiz},w}=2.25-\frac{2(1.157)}3=1.478667\inch.
\]
Para fatiga: $K_f=K_t=2.7$, $K_{fs}=K_{ts}=2.2$, flexión rotativa y axial/torsión pulsantes de cero al máximo. Con $\sigma_b$, $\sigma_x$ y $\tau$ concentrados:
\begin{align*}
\sigma_x&=\frac{4K_tF_a}{\pi d^2},\\
\sigma'_a&=\sqrt{(\sigma_b+\sigma_x/2)^2+3(\tau/2)^2},\\
\sigma'_m&=\sqrt{(\sigma_x/2)^2+3(\tau/2)^2},\\
n_f&=\left(\frac{\sigma'_a}{S_e}+\frac{\sigma'_m}{S_{ut}}\right)^{-1},\qquad
n_y=\frac{S_y}{\sqrt{(\sigma_b+\sigma_x)^2+3\tau^2}}.
\end{align*}
''')
table(['Elemento','$d$ (in)','$S_e$ (ksi)','$n_y$','$n_f$'],[[label,fmt(r['d'],4),fmt(r['Se']/1000),fmt(r['ny']),fmt(r['nf'])] for label,r in [('Corona--piñón',lift['new_shaft_output']),('Raíz del sinfín',lift['new_worm_root'])]])
add(r'''\subsection{Manivela y cuñas de elevación}
Manivela rectangular $1\times0.5\inch$:
\[
M=20(4)=80\lbin,\quad\sigma=\frac{2.7(6)(80)}{1(0.5)^2}=5.184\ksi,
\quad n_y=77/5.184=14.85.
\]
Cuñas AISI 1020 CD: mismas ecuaciones de corte y aplastamiento de la caja.
''')
table(['Unión','$d$ (in)','$T$ (lbf in)','$b\times h\times L$ (in)','$n_{corte}$','$n_{ap}$'],[[r['name'],fmt(r['d']),fmt(r['T_inlb']),f"{r['b']} $\\times$ {r['b']} $\\times$ {r['L']}",fmt(r['SF']),fmt(r['SC'])] for r in lift['keys']])
add(r'''La corona necesita cubo con 2 in útiles de cuña aunque su cara dentada sea de 1.5 in. Para el aplastamiento del cubo de bronce se requiere $S_{y,cubo}\geq7.69\ksi$ con $n_d=1.2$; no se le atribuyen los 57 ksi del acero de la cuña.

\subsection{Retención y momento transmitido a la columna}
No se acredita autobloqueo del sinfín para toda lubricación. Bloqueo mecánico o freno propuesto en el eje de piñón:
\[
T_{freno}\geq1.2(9500)(0.0381)=434.34\,\mathrm{N\,m}.
\]
El freno, sus fijaciones y la rigidez de guías no están dimensionados. Si la distancia husillo--columna es 185 mm, el orden de momento por empuje es:
\[
M_{columna}\simeq9500(0.185)=1757.5\,\mathrm{N\,m},
\]
además de los pesos. No constituye comprobación de columna ni soldadura.

\section{Husillo: comprobación adicional con carga axial}
Envolvente simultánea: $F_a=9.50\,\mathrm{kN}$, $T=T_{3,arr}=466.664\lbin$, $K_t=2.7$, $K_{ts}=2.2$ y pico de flexión del eje. Se suma la tensión axial a la fibra más solicitada:
\[
\sigma_{VM}=\sqrt{\left(\frac{32K_tM_{arr}}{\pi d^3}+\frac{4K_tF_a}{\pi d^2}\right)^2
+3\left(\frac{16K_{ts}T_{arr}}{\pi d^3}\right)^2}.
\]
Para la estimación de Goodman previa: axial pulsante $0\rightarrow F_a$, flexión nominal alternante y torque nominal medio. En ese antecedente se conservó $K_f=K_t$ y $K_{fs}=K_{ts}$ como cota.
''')
table(['Sección','$d$ (in)','$\sigma_{VM}$ (ksi)','$n_y$','$n_f$'],[[r['section'],fmt(r['d']),fmt(r['vm_psi']/1000),fmt(r['ny']),fmt(r['nf'])] for r in lift['spindle']])
add(r'''El extremo A de 0.500 in no satisface $n_y\geq1.2$ bajo esta envolvente. La propuesta A de 0.625 in sí lo satisface en el modelo. No se ha aplicado al Excel ni valida una rosca/cono del mandril sin definir.
\clearpage
\section{Rodamientos: seis apoyos de la caja reductora}
\subsection{Criterio de vida y cargas}
Se solicitan 50,000 h \textbf{combinadas del conjunto}, interpretadas como vida básica L10 con 90\% de supervivencia conjunta y fallas independientes. Se analizan primero los seis apoyos de la caja.

Pesos provisionales: masas CAD de engranajes PD = 6 más 1 kg supuesto por eje/herrajes:
\[
W_1=(1.670+1)g=26.193\,\mathrm N,
\quad W_2=(15.086+2.227+1)g=179.651\,\mathrm N,
\]
\[
W_3=(20.114+1)g=207.128\,\mathrm N.
\]
Se usan como cota preliminar; reemplazar por masas CAD actuales. Las cargas radiales proceden de las reacciones anteriores. En Eje 3 se verifican corte sin crédito de peso, corte menos peso y peso sin corte. No se atribuye el peso del motor al eje del reductor.
''')
table(['Apoyo','$F_{r,nom}$ (N)','$F_{r,arr}$ (N)','$F_{a,nom}^{max}$ (N)','$F_{a,pico}^{max}$ (N)'],[[r['shaft']+' '+r['position']]+[fmt(r[k],1) for k in ['Fr_nom_N','Fr_start_N','Fa_nom_bound_N','Fa_start_bound_N']] for r in bear['rows']])
add(r'''\subsection{Cargas equivalentes y equilibrio axial}
Bolas de ranura profunda, factores $e,Y$ de NTN en función de $f_0F_a/C_0$:
\[
P=\begin{cases}F_r,&F_a/F_r\leq e,\\0.56F_r+YF_a,&F_a/F_r>e,\end{cases}
\quad P_0=\max(F_r,0.6F_r+0.5F_a).
\]
Rodillos cónicos:
\[
P=\begin{cases}F_r,&F_a/F_r\leq e,\\0.4F_r+YF_a,&F_a/F_r>e,\end{cases}
\quad P_0=\max(F_r,0.5F_r+Y_0F_a).
\]
Par cónico sin precarga, carga externa positiva resistida por B:
\[
S_G=\frac{F_{r,G}}{2Y_G},\quad S_B=\frac{F_{r,B}}{2Y_B},\quad
F_{a,B}=\max(S_B,S_G+F_{ext}),\quad F_{a,G}=F_{a,B}-F_{ext}.
\]
Para 4T-30302: $e=0.29$, $Y=2.11$, $Y_0=1.16$. Para 4T-30304CA: $e=0.55$, $Y=1.10$, $Y_0=0.60$.

\subsection{Ciclo de arranque y vida individual}
Supuesto: 20 arranques/h, 1 s cada uno, velocidad media durante aceleración $0.5n$; carga extrema durante esos pulsos. Resto: 3580 s/h a velocidad nominal. La carga extrema no se supone continua.
\begin{align*}
f&=\frac{20(1)(0.5)}{3580+20(1)(0.5)}=0.002785515,\\
\bar n&=n\frac{3580+20(1)(0.5)}{3600},\\
P_{eq}&=[(1-f)P_{nom}^p+fP_{pico}^p]^{1/p},\\
P_d&=f_wP_{eq},\quad f_w=1.20,\\
L_{10h}&=\frac{10^6}{60\bar n}\left(\frac C{P_d}\right)^p,
\quad p=3\text{ (bolas)},\quad p=10/3\text{ (rodillos)},\\
S_0&=\frac{C_0}{1.20\max(P_{0,nom},P_{0,pico})}.
\end{align*}
El factor $f_w$ es un margen de carga para rodamientos, no un cambio del $K_o$ de los engranajes.
''')
table(['Apoyo','NTN','$d\times D\times T$ (mm)','$C$ (kN)','$C_0$ (kN)'],[[r['shaft']+' '+r['position'],r['number'],f"{r['d_mm']} $\\times$ {r['D_mm']} $\\times$ {r['B_mm']}",fmt(r['C_kN'],2),fmt(r['C0_kN'],2)] for r in bear['rows']], 'llrrr')
table(['Apoyo','$P_{nom}$ (N)','$P_{pico}$ (N)','$P_{eq}$ (N)','$L_{10}$ (h)','$S_0$'],[[r['shaft']+' '+r['position'],fmt(r['P_nom_N'],1),fmt(r['P_start_N'],1),fmt(r['P_eq_N'],1),fmt(r['L10_h'],0),fmt(r['S0'],2)] for r in bear['rows']])
add(r'''Todos satisfacen $1.20P_{pico}\leq0.5C$ y los criterios estáticos adoptados $S_0\geq2$ para bolas, $S_0\geq3$ para cónicos. El cálculo de vida no sustituye la comprobación de carga mínima.

\subsection{Vida combinada}
Exponentes de dispersión: $e_i=10/9$ para bolas y $e_i=9/8$ para rodillos. Extensión por independencia al conjunto mixto:
\[
R_{conj}(t)=\exp\left[\ln(0.9)\sum_i(t/L_i)^{e_i}\right],\qquad
\sum_i(t/L_i)^{e_i}=1\quad\text{para }R_{conj}=0.9.
\]
\[
L_{10,conj}=101198.77\,\mathrm h.
\]
Cota conservadora, válida aquí porque $t<L_i$ para todos y $10/9\leq e_i$:
\[
L_{conj,conservador}=\left(\sum_iL_i^{-10/9}\right)^{-9/10}
=\boxed{100826.53\,\mathrm h>50000\,\mathrm h}.
\]
Si se exigieran vidas individuales iguales, se requeriría $L_i=50000(6)^{9/10}=250788\,\mathrm h$, no 50000 h por apoyo. No se exige igualdad: se verifica la suma del conjunto.

Sensibilidad ilustrativa: reducir todas las vidas a la mitad deja la cota conjunta en 50413.26 h. No equivale a calcular un factor de lubricación $a_3$; faltan temperatura, viscosidad y limpieza.

\subsection{Montaje propuesto y cambios pendientes}
Ejes 1 y 2: apoyo superior libre axialmente y apoyo inferior localizador. Eje 3: dos cónicos opuestos en disposición DB. El inferior B resiste el empuje de perforación; orientar las pistas de acuerdo con esa reacción.
''')
table(['Zona','Asiento actual (in)','Propuesto (mm)','Apoyo mínimo de hombro (mm)'],[['Eje 1 B/G','0.500','12','$d_a\geq14$'],['Eje 2 A','0.375','10','$d_a\geq12$'],['Eje 2 G','0.375','10','$14\leq d_a\leq17$'],['Eje 3 G','0.500','15','$d_a\geq20.5$'],['Eje 3 B','0.625','20','$d_a\geq28.5$']], 'lrrl')
add(r'''Eje 2: F actual de 0.500 in no da el hombro mínimo del 6300; proponer F = 0.625 in. Eje 3 G: separador de apoyo local de 21 mm. Eje 3 B: C debe permitir el asiento/montaje de 20 mm y un separador \emph{desmontable} de 29 mm; un hombro integral mayor que el asiento del engranaje puede impedir su montaje. Confirmar tuercas y retención en ambos sentidos.

Radios máximos: 6000/6001, 0.3 mm; 6300, 0.6 mm; 30302, 1 mm; 30304CA, 1.5 mm. Los límites $d_a$ y $d_b$ de cónicos corresponden a caras diferentes y no forman un intervalo único.

Los centros de carga efectivos adoptados deben conservarse. Para los cónicos: $a=9.5$ mm y $a=13.5$ mm desde la cara de referencia del catálogo. Si la posición efectiva cambia, recalcular las reacciones.

Quedan pendientes: carga mínima ($P<0.04C_0$ en varios apoyos, advertencia NTN A-70), juego operativo, ajuste térmico, alimentación de aceite a ambos niveles y viscosidad a temperatura real. El modelo usa precarga nula; no se añade precarga arbitraria. Cambiar asientos obliga a revisar resistencia de los ejes.

\subsection{Antecedente de rodamiento axial independiente: sustituido}
Antes de la selección de seis apoyos se evaluó un axial NSK 51204 de $20\times40\times14$ mm. No se suma al arreglo actual de seis rodamientos: es una alternativa previa, reemplazada por el par cónico.
\begin{align*}
f_{previo}&=20/3600,\quad L=60(200)(50000)/10^6=600,\\
P_{eq,a}&=[(1-f)(0.803594)^3+f(9.5)^3]^{1/3}=1.74123\,\mathrm{kN},\\
C_{a,req}&=1.2P_{eq,a}(600)^{1/3}=17.623\,\mathrm{kN},\\
C_{0a,req}&\geq1.2(9.5)=11.40\,\mathrm{kN}.
\end{align*}
El catálogo consultado previamente daba $C_a=22.5$ kN y $C_{0a}=37.5$ kN. Ese cálculo usaba carga axial aislada y pico a velocidad nominal, no el espectro actualizado por revoluciones ni la vida combinada. Si 9.5 kN fueran continuos: $C_{a,req}=96.15$ kN. El candidato no encaja directamente en asiento de 0.625 in.

\section{Antecedente de rodamientos de elevación}
La selección actual se limita a la caja reductora. Se conserva aquí el cálculo previo de elevación como antecedente separado: 50,000 h individuales, no vida combinada validada de ese mecanismo. Con pares cónicos:
\[
S_{ind}\leq0.47(F_{rA}+F_{rB})/K,\quad
P_{cota}=F_{r,max}+Y(|F_{a,ext}|+S_{ind}),
\]
\[
C_{req}=1.2P_{cota}\left(\frac{60\bar n(50000)}{10^6}\right)^{3/10}.
\]
''')
table(['Eje / candidato','$P_{cota}$ (kN)','$\bar n$ (rpm)','$C_{req}$ (kN)','$C_{cat}$ (kN)'],[['Corona / LM104949--LM104911',fmt(lift['output_bearings']['P_bound_kN']),1,fmt(lift['output_bearings']['C_required_kN']),'96.3'],['Sinfín / LM29749--LM29710',fmt(lift['worm_bearings']['P_bound_kN']),20,fmt(lift['worm_bearings']['C_required_kN']),'48.6']], 'lrrrr')
add(r'''Se habían propuesto dos por eje, asientos de 2 in y 1.5 in respectivamente. Las capacidades Timken y el ajuste deben reconfirmarse al cerrar ese mecanismo; estas cuatro unidades no participan en la vida combinada de los seis apoyos NTN de la caja.

\section{Estado y referencias de los cálculos}
\begin{itemize}
\item Configuración actual: PD = 9.5; reducciones 3:1 y 3:1; 1800/600/200 rpm. Se conservan geometría y valores manuales del Excel.
\item Verificados en el modelo: flexión/contacto AGMA nominal y arranque; secciones críticas de ejes por Goodman y fluencia; cuatro cuñas de engranajes; alternativa de elevación; seis rodamientos de caja por vida conjunta y estática.
\item Propuestas sin aplicar: refuerzo A del husillo, nuevos asientos comerciales y apoyos de hombro; alternativa reforzada de elevación.
\item Por completar: masa e inercias actuales, curva de arranque, espectro real de perforación, detalles de acople/mandril, ajustes y lubricación, retención de mesa, columna, guías, tornillos y soldaduras.
\end{itemize}

\subsection*{Fuentes de proyecto}
''')
for name,b in src.items():
 path=Path(b['path']);h=hashlib.sha256(path.read_bytes()).hexdigest()
 rel=Path('../Calculos/CALCULADORA EJES.xlsx') if name=='ejes' else Path('Calculos/EXCEL ENGRANES.xlsx')
 add(r'Ruta respecto a la carpeta del proyecto: \path{'+str(rel).replace('\\','/')+r'}.')
 add(r'SHA-256: \texttt{'+h[:32]+r'}\ldots')
add(r'''Resultados auxiliares utilizados:
\begin{itemize}
\item \path{outputs/elevacion_mesa/resultados.json}
\item \path{outputs/rodamientos_caja/calculo.json}
\end{itemize}
El documento no modifica los libros de cálculo. Los errores de celdas auxiliares no usadas no se presentan como resultados resistentes.

\begin{thebibliography}{9}
\bibitem{shigley} Budynas y Nisbett. \emph{Diseño en ingeniería mecánica de Shigley}. Capítulos de ejes, uniones con cuña, rodamientos y engranajes rectos/sinfín. Se conserva la notación del proyecto; confirmar numeración de ecuaciones con la edición empleada en clase.
\bibitem{ntn} NTN. \emph{Catálogo general}, PDF aportado. A-17--A-20: vida/carga estática; A-25--A-26: equivalentes y pares; A-58/A-66/A-70: juego, precarga y carga mínima; B-8--B-9: bolas; B-142--B-143: rodillos cónicos.
\bibitem{clases} \emph{Clase 13: Rodamientos de bolas y contacto angular}; \emph{Clase 14: Juego, precarga y lubricación}. Referencias docentes aportadas; no sustituyen el criterio del usuario de 50,000 h combinadas.
\bibitem{sandvik} Sandvik Coromant. \emph{Formulas and definitions for drilling, metric}. Fuente del modelo ilustrativo de mecanizado usado previamente; $k_c$ y avance son supuestos del proyecto. \url{https://cdn.sandvik.coromant.com/files/sitecollectiondocuments/services/metal-cutting-e-learning/formulas-and-definitions/formulas-and-deinitions-for-drilling-metric-enu.pdf}
\bibitem{previos} \emph{Cálculos preliminares de elevación de la mesa} y \emph{Cálculo de rodamientos de la caja reductora}, archivos del proyecto, noviembre de 2026. Los candidatos NSK/Timken se conservan como antecedentes; la selección actual de caja usa NTN.
\end{thebibliography}
\end{document}
''')
path=out/'Memoria_calculos_taladro.tex';path.write_text('\n'.join(parts),encoding='utf-8')
print(path.resolve())
