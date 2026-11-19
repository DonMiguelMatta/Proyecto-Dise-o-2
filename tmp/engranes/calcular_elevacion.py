from pathlib import Path
import math,json
from openpyxl import load_workbook
O=Path('outputs/elevacion_mesa');O.mkdir(parents=True,exist_ok=True)
LB=4.4482216152605;NM=.112984829027616;phi=math.radians(20)
W=20.032*9.81;Fmax=9500/LB;nd=1.2;stroke=10;R=4;i=20
def worm(pt,dw,Dg,F):
 C=(dw+Dg)/2;lam=math.atan(1/(pt*dw));eta=lambda mu:(math.cos(phi)-mu*math.tan(lam))/(math.cos(phi)+mu/math.tan(lam))
 # For mG=20, use the smaller of the two neighboring correlation values.
 cm=min(.022*math.sqrt(-20**2+40*20-76)+.46,.0107*math.sqrt(-20**2+56*20+5145))
 nw=20;vs=math.pi*dw*nw/(12*math.cos(lam))
 cv=.659*math.exp(-.0011*vs);cs=720+10.37*C**3 if C<=3 else 1000
 fe=min(F,.67*dw);allow=cs*Dg**.8*fe*cm*cv
 return dict(Pt=pt,dw=dw,Dg=Dg,width=F,C=C,lambda_deg=math.degrees(lam),eta=eta(.1),eta_cases={str(mu):eta(mu) for mu in [.08,.1,.15]},Cs=cs,Cm=cm,Cv=cv,Wallow_lbf=allow)
def rack(d,pd,b,st,sc):
 ks=1.192*(b*math.sqrt(.309)/pd)**.0535;km=1.5;kv=1.02;J=.28;I=math.sin(phi)*math.cos(phi)/2
 sig=Fmax*pd/(b*J)*ks*km*kv;contact=2300*math.sqrt(Fmax*ks*km*kv/(d*b*I))
 return dict(d=d,Pd=pd,b=b,St=st,Sc=sc,Ks=ks,Km=km,Kv=kv,J=J,I=I,bending_psi=sig,contact_psi=contact,SF=st/sig,SH=sc/contact)
initial=worm(8,1.5,2.5,1);revised=worm(3,2.25,20/3,1.5)
for item in [initial,revised]:
 item['Wt_required_lbf']=2*Fmax*.75/item['Dg']
 item['load_ratio']=item['Wallow_lbf']/item['Wt_required_lbf']
 # Compare also a stronger output stage sized for the full envelope with a 3 in rack pinion.
 item['Wt_required_3in_lbf']=2*Fmax*1.5/item['Dg']
 item['load_ratio_3in']=item['Wallow_lbf']/item['Wt_required_3in_lbf']
rack0=rack(1.5,12,1,22000,170000)
rack1=rack(3,6,2.5,65000,225000)
cutT=2500*10**2*.15/8000;cutF=.25*2500*10*.15*math.sin(math.radians(59));cutP=cutT*2*math.pi*200/60
mech=[]
for name,d,wo in [('inicial',1.5,initial),('reforzado',3,revised)]:
 advance=math.pi*d/20;drive=wo['eta']*.95*20*4/(d/2)*LB
 mech.append(dict(name=name,d=d,advance_in=advance,turns=10/advance,manual_rpm_cut=30/(advance*25.4),Ftable_5lbf=5*drive,Faxial_20lbf=20*drive-W,Fideal_20lbf=20*4*20/(d/2)*LB,hand_cut_lbf=(cutF+W)/drive))
# Spindle: evaluate A and B, add pulsed axial stress to rotating nominal bending.
p=Path(r'D:\migue\OneDrive - UVG\A2UVG 2026\Diseño_2\Proyecto\Calculos\CALCULADORA EJES.xlsx')
w=load_workbook(p,data_only=True);s=w['Eje 3'];ka_se=s['I73'].value/s['I72'].value
sp=[]
for label,d,mn,ms in [('A actual',.5,0,0),('A propuesta',.625,0,0),('B actual',s['I80'].value,s['I7'].value,s['I92'].value)]:
 kt=2.7;kts=2.2;sy=s['I16'].value;sut=s['I15'].value
 bend=32*kt*ms/(math.pi*d**3);ax=4*kt*Fmax/(math.pi*d*d);shear=16*kts*w['INICIAR P1']['F13'].value/(math.pi*d**3)
 vm=math.hypot(bend+ax,math.sqrt(3)*shear)
 se=ka_se*.879*d**(-.107)
 sa=32*kt*mn/(math.pi*d**3)+ax/2
 sm=math.hypot(ax/2,math.sqrt(3)*16*kts*w['INICIAR P1']['F12'].value/(math.pi*d**3))
 nf=1/(sa/se+sm/sut)
 sp.append(dict(section=label,d=d,vm_psi=vm,ny=sy/vm,nf=nf))
# Keys: 1020 CD. Full overload torque at the reinforced rack-pinion shaft.
Tshaft=Fmax*1.5;sykey=57000;keys=[]
for name,t,d,b,L in [('Corona-eje',Tshaft,2,.5,2),('Manivela-sinfín',80,1,.25,.5)]:
 force=2*t/d;keys.append(dict(name=name,T_inlb=t,d=d,b=b,L=L,SF=.577*sykey*b*L/force,SC=sykey*b*L/(2*force)))
# New shaft is conditional on the proposed straddle mounting, 6 in between bearings.
# Conservative transverse loads: wheel and rack forces treated as aligned; axial mesh couple added in full.
fmu=.15;lam=math.atan(1/(3*2.25));wg=2*Tshaft/(20/3)
normal=wg/(math.cos(phi)*math.cos(lam)-fmu*math.sin(lam))
ww=normal*(math.cos(phi)*math.sin(lam)+fmu*math.cos(lam));wr=normal*math.sin(phi)
load1=math.hypot(wg,wr);load2=Fmax/math.cos(phi)
ra=(load1*(7-1.75)+load2*(7-5))/7;rb=load1+load2-ra
M=max(ra*1.75,rb*2)+ww*(20/3)/2
def shaft(d,m,t,ax):
 kt=2.7;kts=2.2;sy=77000;sut=91000
 kb=.879*d**(-.107);ka=2.7*(sut/1000)**(-.265);se=.5*sut*ka*kb*.897
 sb=32*kt*m/(math.pi*d**3);sx=4*kt*ax/(math.pi*d*d);tau=16*kts*t/(math.pi*d**3)
 vm=math.hypot(sb+sx,math.sqrt(3)*tau)
 # Conservative independent cycles: full rotating bending, pulsed axial and torsion.
 sa=math.hypot(sb+sx/2,math.sqrt(3)*tau/2);sm=math.hypot(sx/2,math.sqrt(3)*tau/2)
 return dict(d=d,vm_psi=vm,ny=sy/vm,nf=1/(sa/se+sm/sut),Se=se)
shaft_output=shaft(2,M,Tshaft,ww)
# Worm includes off-axis axial-load couple at the pitch radius, root diameter per Shigley.
root=2.25-2*1.157/3;tw=ww*2.25/2;Mw=math.hypot(ww,wr)*6/4+wg*2.25/2
shaft_worm=shaft(root,Mw,tw,wg)
# Crank: rectangular 1 x .5 in bar; full 80 in-lbf at its root.
crank_stress=2.7*6*80/(1*.5**2);crank_n=77000/crank_stress
# Bearing capacity requirements, not a claim of fitted catalog selection.
life_rev=60*200*50000/1e6;duty=20/3600
peq=((1-duty)*(cutF/1000)**3+duty*(9.5)**3)**(1/3)
bearing=dict(Fnom_kN=cutF/1000,Fpeak_kN=9.5,L_million=life_rev,peak_duty_assumed=duty,P_eq_kN=peq,C_required_kN=nd*peq*life_rev**(1/3),C0_required_kN=nd*9.5,C_continuous_peak_kN=nd*9.5*life_rev**(1/3),NSK51204_C_kN=22.5,NSK51204_C0_kN=37.5)
def bearing_pair(frA,frB,fa,K,Y,C,n):
 induced=.47*(frA+frB)/K;fa_bound=abs(fa)+induced
 pe=max(frA,frB)+Y*fa_bound
 rev=60*n*50000/1e6;creq=nd*pe*LB/1000*rev**.3
 return dict(FrA_kN=frA*LB/1000,FrB_kN=frB*LB/1000,Fa_external_kN=fa*LB/1000,Fa_bound_kN=fa_bound*LB/1000,P_bound_kN=pe*LB/1000,mean_rpm=n,C_required_kN=creq,C_catalog_kN=C)
couple=ww*(20/3)/2
output_bearings=bearing_pair(ra+couple/7,rb+couple/7,ww,1.91,1.97,96.3,1)
worm_rad=math.hypot(ww,wr)/2+wg*2.25/2/6
worm_bearings=bearing_pair(worm_rad,worm_rad,wg,1.76,1.8,48.6,20)
for mech_case in mech:
 force=20*4*20/(mech_case['d']/2)
 assert math.isclose(force*mech_case['advance_in'],2*math.pi*20*4,rel_tol=1e-12)
assert initial['load_ratio']<nd and rack0['SF']<nd and sp[0]['ny']<nd
assert revised['load_ratio_3in']>nd and rack1['SF']>nd and rack1['SH']>nd
assert min(shaft_output['nf'],shaft_output['ny'],shaft_worm['nf'],shaft_worm['ny'])>nd
assert all(x['SF']>nd and x['SC']>nd for x in keys)
assert output_bearings['C_required_kN']<output_bearings['C_catalog_kN']
assert worm_bearings['C_required_kN']<worm_bearings['C_catalog_kN']
assert bearing['C_required_kN']<bearing['NSK51204_C_kN']
result=dict(weight_N=W,cut=dict(T_Nm=cutT,P_W=cutP,F_N=cutF),initial_worm=initial,revised_worm=revised,rack_initial=rack0,rack_reinforced=rack1,mechanism=mech,spindle=sp,keys=keys,new_shaft_output=shaft_output,new_worm_root=shaft_worm,shaft_assumptions=dict(span_in=7,wheel_x_in=1.75,pinion_x_in=5,M_bound_inlb=M,axial_lbf=ww,RA_bound_lbf=ra,RB_bound_lbf=rb,worm_span_in=6,worm_M_bound_inlb=Mw),crank=dict(stress_psi=crank_stress,ny=crank_n),bearing=bearing,output_bearings=output_bearings,worm_bearings=worm_bearings)
(O/'resultados.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False))
