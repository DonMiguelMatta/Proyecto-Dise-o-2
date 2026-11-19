# Cálculo preliminar de elevación de la mesa

Fecha: 18 de noviembre de 2026. Unidades de geometría: pulgadas, salvo dimensiones comerciales de rodamientos. Resultados de resistencia condicionados a materiales, geometrías y apoyos indicados. No se modificó el Excel ni el CAD.

## 1. Datos y criterios

- Mesa y soporte suministrados: 5.032 kg. Accesorios y pieza: hasta 15 kg. Peso total considerado: **196.51 N**. Las masas adicionales de cremallera, carro y elementos móviles deberán añadirse al obtenerlas de Inventor.
- Husillo: 200 rpm, potencia transmitida 0.4802 hp, torque nominal 151.323 lb·in (17.10 N·m). Torque de arranque 466.664 lb·in.
- Recorrido útil: 10 in. Accionamiento manual sin limitador de torque. Brazo de 4 in. Fuerza manual máxima SUPUESTA: 20 lbf; no constituye un límite físico impuesto al operador.
- Envolvente axial y de cremallera conservada del plan: **9.50 kN**. Factor de diseño requerido: 1.20, aplicado a resistencia y separado de eficiencias.
- Vida de referencia: 50,000 h y confiabilidad básica de vida L10 (90 %) para rodamientos. En ejes nuevos se utiliza ke=0.897 (90 %). No se confunde con la confiabilidad de 99 % de los números AGMA de los dientes.

## 2. Estimación de perforación

Caso ilustrativo para acero dulce y broca HSS de 10 mm: kc=2500 N/mm², avance fn=0.15 mm/rev, ángulo de entrada 59°. El coeficiente kc y el avance son supuestos de diseño, no una ficha de la broca del proyecto. El cálculo de fuerza de mecanizado procede de [Sandvik](https://cdn.sandvik.coromant.com/files/sitecollectiondocuments/services/metal-cutting-e-learning/formulas-and-definitions/formulas-and-deinitions-for-drilling-metric-enu.pdf); las verificaciones de los elementos se realizan con Shigley.

- Velocidad de corte: π·0.010·200 = **6.28 m/min**.
- Avance vertical: 200·0.15 = **30 mm/min**.
- Torque estimado: kc·D²·fn/8000 = **4.69 N·m**.
- Potencia estimada: T·2πn/60 = **98.17 W**, frente a aproximadamente 358 W disponibles.
- Empuje aproximado: 0.25·kc·D·fn·sin(59°) = **803.59 N**.
- Elevación cuasiestática durante el corte: Fp+W = **1000.11 N**, más rozamiento de guías.

Existe margen de torque y potencia en este modelo. Esto no valida cualquier acero ni garantiza el desempeño de una broca real: el empuje del filo transversal, afilado, desgaste y condiciones de corte deben confirmarse. A 200 rpm el mecanizado será lento.

## 3. Fuerza y cinemática

Se usa: Tentrada=Fmano·R; Tsalida=ηs·i·Tentrada; Fcremallera=ηr·Tsalida/rp. Se adopta ηr=0.95 para el engrane piñón–cremallera y μ=0.10 como caso central del sinfín. El rozamiento de guías no está incluido en estas eficiencias.

La eficiencia del sinfín se calcula con la ecuación de Shigley:

ηs=(cosφn−μ·tanλ)/(cosφn+μ·cotλ).

| Parámetro | Propuesta inicial | Alternativa reforzada |
|---|---:|---:|
| Manivela | 4 in | 4 in |
| Piñón de cremallera | 18 dientes, Pd12 | 18 dientes, Pd6 |
| Diámetro primitivo | 1.50 in | 3.00 in |
| Reducción sinfín/corona | 20:1 | 20:1 |
| Avance por vuelta | 0.2356 in | 0.4712 in |
| Vueltas para 10 in | 42.44 | 21.22 |
| Manivela durante corte a 30 mm/min | 5.01 rpm | 2.51 rpm |
| Eficiencia del sinfín, μ=0.10 | 0.435 | 0.573 |
| Esfuerzo manual para corte y peso, sin fricción de guías | 5.10 lbf | 7.75 lbf |
| Empuje sobre husillo con 20 lbf, a plena carga, sin fricción de guías | 3.73 kN | 2.39 kN |
| Fuerza ideal de cremallera con 20 lbf, sin pérdidas | 9.49 kN | 4.74 kN |

**La alternativa cambia la geometría y, por tanto, también la fuerza máxima teórica y las vueltas.** Se conserva 9.50 kN como capacidad de cálculo por acuerdo previo, aunque supera el límite ideal de la alternativa a 20 lbf. No se presenta 9.50 kN como empuje operativo esperado.

Para la alternativa, μ=0.08/0.10/0.15 da ηs=0.627/0.573/0.470. La fuerza manual necesaria para el corte calculado, sin guías, va de aproximadamente 7.08 a 9.44 lbf.

## 4. Dientes: resultado inicial y alternativa

La evaluación de dientes usa las ecuaciones AGMA resumidas en [Shigley, capítulos 14 y 15](https://www.sweetstudy.com/sites/default/files/qx/16/11/08/08/shigleymechanicalengineeringdesignch13-15.pdf). Los factores geométricos, materiales y calidad deben comprobarse en el dentado fabricado.

### Piñón y cremallera

La propuesta inicial no había fijado ancho ni material. Para evaluarla se tomó ancho 1 in, acero endurecido por inducción tipo B, St=22 ksi y Sc=170 ksi. J=0.28 conservador para ambos elementos, I=sin20°cos20°/2, Km=1.5 supuesto, Kv=1.02 y Ks por Shigley. Ko=KB=1. Se aplicó toda la envolvente de 9.50 kN, sin otro multiplicador de arranque.

Resultado inicial: σflexión=141.63 ksi y σcontacto=269.30 ksi; SF=0.16 y SH=0.63. **No cumple la envolvente**; la condición es más exigente que levantar la mesa durante el corte normal.

Alternativa: piñón integral con eje, 18 dientes, Pd6, diámetro primitivo 3 in; cremallera del mismo paso; ancho de cara 2.50 in. Acero apropiado para carburizar, calidad metalúrgica AGMA grado 2, St≥65 ksi y Sc≥225 ksi, con núcleo certificado Sy≥77 ksi y Sut≥91 ksi. No basta indicar solamente una dureza superficial. Cremallera dentada propuesta: 12 in de longitud para 10 in útiles y margen de 1 in en cada extremo; el recorrido real debe verificarse en CAD.

Con los mismos criterios preliminares de reparto y geometría:

- σflexión=30.87 ksi; **SF=2.11**.
- σcontacto=125.73 ksi; **SH=1.79**.
- Se usan YN=ZN=1: clasificación a 10⁷ ciclos de diente. Debe confirmarse que el uso acumulado no exceda esa referencia; se debe verificar Km con alineación y carcasa definitivas.
- El piñón es integral: **no lleva cuña piñón–eje**. Así se evita dejar una pared insuficiente entre el cuñero y la raíz de un piñón pequeño.

### Sinfín y corona

Modelo inicial: una entrada, corona de 20 dientes, Pt8, dw=1.50 in, DG=2.50 in, ancho efectivo 1 in. La ecuación (Wt)all=Cs·DG^0.8·Fe·Cm·Cv da capacidad **894.7 lbf**, frente a **1281.4 lbf** exigidos por la envolvente y el piñón inicial. Cociente=0.70<1.20: **no cumple**.

Alternativa reforzada:

- Una entrada y 20 dientes; Pt3; dw=2.25 in; DG=6.6667 in; centros=4.4583 in.
- Ancho efectivo de corona=1.50 in, menor que 0.67dw. Ángulo normal 20°, avance λ=8.427°.
- Sinfín de acero con superficie ≥58 HRC y núcleo certificado; corona de bronce centrifugado apropiado para engranajes. Estas condiciones son necesarias para aplicar la correlación de capacidad adoptada.
- Cs=1000. Se utiliza Cm=0.8194 como valor conservador en la frontera de las correlaciones de relación 20. Cv=0.6504, calculado a 20 rpm del sinfín.
- Capacidad=3647.0 lbf; carga de diseño sobre la corona con piñón de 3 in=961.1 lbf. **Cociente de capacidad=3.79>1.20**.

Este cociente es la comparación de carga de la correlación de desgaste AGMA/Shigley; no se interpreta como una comprobación estática universal ni como certificación de choque. El cálculo de fatiga de los ejes utiliza la envolvente y el núcleo mínimo especificado.

## 5. Ejes, manivela y cuñas del mecanismo nuevo

Distribución propuesta para poder efectuar las comprobaciones: eje corona–piñón entre centros efectivos de rodamientos separados 7 in; corona a 1.75 in y piñón a 5 in desde el primer apoyo. Sinfín centrado entre apoyos efectivos separados 6 in. Cambiar esta distribución obliga a recalcular. Se suman conservadoramente fuerzas transversales y el par de vuelco producido por las fuerzas axiales descentradas.

Se exige núcleo Sy≥77 ksi, Sut≥91 ksi. Se usa Goodman con ka=2.7(Sut en ksi)^−0.265, kb=0.879d^−0.107, ke=0.897; Kf=Kt=2.7 y Kfs=Kts=2.2 como estimaciones conservadoras. Flexión rotativa totalmente alternante; axial y torsión pulsantes de cero al máximo de diseño. La validez de concentradores y propiedades exige radios y tratamiento definitivos.

| Componente propuesto | Diámetro/sección | n fluencia | n Goodman |
|---|---|---:|---:|
| Eje integral piñón–corona | Ø2 in en secciones de transmisión | 4.19 | 1.50 |
| Raíz del sinfín | Ø1.4787 in; dw2.25 in | 4.57 | 1.71 |

Manivela: brazo 4 in, barra rectangular 1 × 1/2 in, carga manual 20 lbf, momento de raíz 80 lb·in. Con Kt=2.7: σ=5.184 ksi y **ny=14.85**. La masa y el peso de esta manivela no están incluidos en el empuje de perforación, pues pertenece al mecanismo fijo.

Cuñas cuadradas de AISI1020 CD, Sy57 ksi; verificadas por corte y aplastamiento:

| Unión | Cuña b×h×L, in | n corte | n aplastamiento |
|---|---|---:|---:|
| Corona–eje Ø2 in | 1/2 × 1/2 × 2 | 10.27 | 8.90 |
| Manivela–extensión Ø1 in | 1/4 × 1/4 × 1/2 | 25.69 | 22.27 |

La corona necesita un cubo que dé 2 in útiles de cuña, aunque su cara dentada sea 1.5 in. El aplastamiento de su cubo de bronce debe comprobarse además con su propia fluencia: se requiere Sy del cubo≥7.69 ksi para n=1.20; no se le atribuyen los57 ksi de la cuña de acero. La cuña de manivela se comprueba con el máximo de entrada supuesto de 80 lb·in. El dimensionamiento excedente del resto del mecanismo no aumenta ese esfuerzo manual adoptado.

## 6. Carga axial sobre el husillo existente

Envolvente combinada: 9.50 kN de empuje y torque de arranque del husillo 466.664 lb·in. Se aplica axial máxima con Kt=2.7 y torsión con Kts=2.2; el pico de flexión se suma a la tensión axial en la fibra más solicitada. Sy=84.4 ksi y Sut=95 ksi se conservaron del Excel del usuario; no se validan aquí como propiedades normativas del material.

σVM = sqrt[(32KtM/(πd³)+4KtFa/(πd²))²+3(16KtsT/(πd³))²].

| Sección | Diámetro | ny, axial+arranque | n Goodman con axial pulsante |
| A actual | 0.500 in | 1.08 | 1.33 |
| A propuesta | 0.625 in | 2.03 | 2.16 |
| B actual | 0.625 in | 1.89 | 1.91 |

**A actual Ø0.500 in no cumple ny≥1.20 con esta envolvente.** Propuesta resistente: Ø0.625 in mínimo en A. B actual Ø0.625 in cumple bajo el modelo, pero un rodamiento comercial puede exigir otro asiento. Se presupone que el empuje se recoge en un apoyo axial próximo a B; la ruta exacta de carga debe quedar reflejada en el montaje. No se declara validado un cono, rosca o conexión del mandril que todavía no esté definida.

## 7. Rodamientos y retención

### Husillo

Para carga nominal aproximada 0.804 kN y picos de 9.50 kN se supuso, exclusivamente para evaluar vida, 20 picos/h de 1 s, mientras gira a 200 rpm. No es una frecuencia medida ni limita sobrecargas. La ponderación debe hacerse por revoluciones cargadas en el diseño final.

P equivalente=[(1−p)·Fnom³+p·Fpeak³]^(1/3), p=20/3600. Resultado: **1.741 kN**. Para 50,000 h: L=600 millones de revoluciones; con factor de carga1.20, **Ca requerida=17.62 kN** y **C0a requerida≥11.40 kN**.

Candidato: [NSK51204](https://www.nsk.com/engineering/products/bearings/ball-bearings/thrust-ball-bearings/single-direction-thrust-ball-bearings/51204-tb-sd.html), Ca22.5 kN, C0a37.5 kN. Dimensiones20×40×14 mm. Cumple la capacidad calculada para ese espectro; **no cabe directamente en el asiento actual de Ø0.625 in**. Requiere asiento20 mm, apoyo de arandela de eje≥32 mm y alojamiento conforme al catálogo. Esas interfaces deben rediseñarse, no añadirse como si fueran compatibles. El rodamiento axial no sustituye los apoyos radiales.

Si 9.50 kN actuaran continuamente durante 50,000 h, se necesitaría Ca≈**96.2 kN**, y ese candidato NO cumpliría. No se atribuye la vida de50,000 h a cualquier espectro.

### Mecanismo nuevo

Proponer rodamientos cónicos enfrentados, con uno que absorba empuje en cada sentido y ajuste axial según fabricante. Para la estimación se acota la carga axial incluyendo las inducidas de ambos rodamientos: Si=0.47Fr/K; después se usa P conservador=Fr,max+Y·(Fa externa+SiA+SiB). Las distancias anteriores son entre centros efectivos de carga, no necesariamente entre caras de conos.

- Eje corona–piñón: dos [TimkenLM104949/LM104911](https://engineering.timken.com/details/bearing/TRB/TS/LM104949/LM104911/), diámetro2 in. C1=96.3 kN, C0=104 kN, K1.91, Y1.97. P acotada=19.40 kN; para50,000 h a1 rpm media, C1 requerida=32.36 kN. Cumple esta estimación de vida. Se necesitan hombros y tuercas conforme al catálogo; no basta el diámetro de eje.
- Sinfín: dos [TimkenLM29749/LM29710](https://cad.timken.com/item/tapered-roller-bearings---single-cones/tapered-roller-bearings-single-cones-imperial/lm29749), diámetro1.5 in. C1=48.6 kN, C0=60.3 kN, K1.76 y Y1.8. P acotada=11.33 kN; para50,000 h a20 rpm media, C1 requerida=46.42 kN. Cumple con margen pequeño; velocidades medias mayores obligan a revisar la selección. El asiento1.5 in y la raíz1.4787 in son dimensiones distintas.

**La retención no queda garantizada por el sinfín.** La alternativa puede retroceder según fricción y lubricación. Especificar bloqueo mecánico de mesa o freno en el eje del piñón con capacidad≥1.20·9500·0.0381=**434.34 N·m** si se conserva la envolvente9.50 kN. El diseño del freno y sus fijaciones queda fuera de esta comprobación; el mecanismo no se considera aprobado para sostener la mesa sin esa retención.

## 8. Alcance y verificaciones realizadas

Se comprobó conservación de trabajo para las dos cinemáticas ideales, geometría y relación20:1, capacidad de dientes frente a la envolvente, flexión–axial–torsión de los ejes, corte/aplastamiento de las cuñas y vida básica de los candidatos a rodamientos bajo los espectros declarados. Los resultados se calcularon con un script independiente y se verificaron por aserciones de equilibrio, límites y criterios de aceptación.

La alternativa es una propuesta preliminar que satisface esas desigualdades bajo los supuestos indicados; **no es un diseño liberado para fabricación**. La correlación de carga del sinfín es una clasificación empírica de referencia de25,000 h; su margen no sustituye una confirmación de50,000 h de desgaste por fabricante. Faltan compatibilidad en Inventor (la alternativa es sensiblemente mayor), masa móvil definitiva, deformaciones y rozamiento de guías, retención efectiva, tolerancias, lubricación, propiedades certificadas y empuje de perforación real. No se validaron en este informe la columna, soldaduras ni los tornillos de fijación. Una distancia185 mm entre husillo y columna implicaría momento de columna del orden9.50·0.185=1.76 kN·m bajo la envolvente, además de los pesos: debe analizarse posteriormente.

Fuente del estado de los ejes: CALCULADORA EJES.xlsx, hoja Eje3 e INICIARP1, leído de la carpeta Proyecto/Calculos. La hoja rodamientos contiene referencias de otro problema y no se usó como selección validada. Los archivos existentes permanecen intactos.
