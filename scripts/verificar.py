# Recalcula todos los ejercicios de las guías (los valores que figuran en src/ejercicios.html).
# Uso: python3 scripts/verificar.py
from math import *
def brentq(f, a, b):
    """Bisección simple (sin depender de scipy)."""
    fa = f(a)
    for _ in range(200):
        m = (a + b) / 2; fm = f(m)
        if (fm > 0) == (fa > 0): a, fa = m, fm
        else: b = m
    return (a + b) / 2
R=8.314; Ra=0.082057
def vdw_V(n,T,p,a,b):
    f=lambda V: (p+a*n*n/V**2)*(V-n*b)-n*Ra*T
    Vi=n*Ra*T/p; return brentq(f, n*b*1.0001+1e-9, Vi*3)
print("III Ne kPa", 0.225/20.18*Ra*122/3*101.325)
nNe=.225/20.18;nAr=.175/39.95;nCH4=.320/16.04;pNe=66.5/760*101325
V=nNe*R*300/pNe;print("IV V dm3",V*1e3,"pAr",nAr*R*300/V/1e3,"Ptot",(nNe+nAr+nCH4)*R*300/V/1e3)
print("V M", 1.23*Ra*300/(150/760))
Vm=0.86*Ra*300/2;print("VII V cm3",0.86*0.0082*Ra*300/2*1e3,"B",(0.86-1)*Vm)
print("IX ideal L",400*Ra*303.15, "vdW",vdw_V(400,303.15,1,3.640,0.04267))
n=50/(Ra*310.15);print("X n CH4",n,"alimento",500*n, "vdw n", 50/ (vdw_V(1,310.15,1,2.283,0.04278)))
print("XI O2 ideal",50*Ra*298.15/3,"vdw",vdw_V(50,298.15,3,1.364,0.03183),"Tr",298.15/154.6,"pr",3/49.8)
print("XII CH4 ideal",100*Ra*303.15/5,"vdw",vdw_V(100,303.15,5,2.283,0.04278),"Tr",303.15/190.6,"pr",5/45.4)
# primera ley
print("PL I", .052*R*260*log(3))
n=4.5/16.04;print("PL II irr",-200/760*101325*3.3e-3,"rev",-n*R*310*log(16/12.7))
n=.07;nRT=n*R*373;nB=n*-0.0287
w=-nRT*(log(6.79/5.25)+nB*(1/5.25-1/6.79));print("PL III w",w,"q",83.5-w,"dpV",nRT*nB*(1/6.79-1/5.25))
dp=3*Ra*52/(20-3*0.04267);print("PL IV dH J",4700+20*dp*101.325)
Vi=3*Ra*200/2;Vf=Vi*(200/250)**(27.5/R);print("PL V",Vi,Vf,3*R*250/(Vf/1e3),3*(27.5+R)*50)
a,b,c=28.58,3.77e-3,-0.50e5;T1,T2=298.15,373.15
print("PL VI",a*(T2-T1)+b/2*(T2**2-T1**2)-c*(1/T2-1/T1))
# termoq
print("TQ I",(2*-436.75+89.4)/2, -425.61-393.51-127.5,(2*90.25-75.5)/2)
print("TQ II",8*-393.51+5*-285.83+12.5,"III",-4003-285.83+4163,"IV",-442+4*R*298.15/1e3)
d=14.73*(350-298.15)+0.1272/2*(350**2-298.15**2)-(2*8.53+3*28.82)*(350-298.15)
print("TQ V",-84.68+d/1e3,"VI",32.5/8.18*R*111.66/101325)
print("TQ VII",64.77-2*105.58,"VIII",105.58-167.16+127.07)
#2a ley
print("SL II",-196.0-298.15*0.1256,"III",-2810-298.15*.1824,"IV dU",-890.3+2*R*298.15/1e3,"dA",-890.3+2*R*298.15/1e3+298.15*.1403,"dG",-890.3+298.15*.1403)
print("SL V",2*33.18-9.16-298.15*.0048,"VI",-2808-310.15*.1824,"VII",-394.36+137.17)
# equilibrio
K=exp(32900/(R*298.15));print("EQ I",K)
print("EQ II ok",K*exp(92200/R*(1/500-1/298.15)),"guia",K*exp(46100/R*(1/500-1/298.15)))
for nm,G in [("a",-202.87+95.30+16.45),("b",3*-856.64+2*1582.3),("c",-100.4+33.56),("d",2*-33.56+166.9),("e",-744.53+2*120.35+27.83)]:
    print("EQ III",nm,G, exp(-G*1e3/(R*298.15)) if abs(G)<600 else "exp(%g)"%(-G*1e3/(R*298.15)/log(10)))
print("EQ IV xA",1/1.0106)
print("EQ V dG37",1670+R*310.15*log(1/3),"K",exp(-1670/(R*310.15)))
dG=-239.9+R*298.15/1e3*log(1e-6);print("EQ VI",dG,dG*-1e3/(4*96485))
E0=-474260/(4*96485);print("EQ VII E0",E0,"E",E0-R*298.15/(4*96485)*log(0.02**2*0.05),"K",-474260/(R*298.15)/log(10))
# fases
for t in (-10,-5,0,5):
    T=273.15+t;print("CF I",t,611*exp(-51060/R*(1/T-1/273.16))/1e5)
print("CF II dp/dT bar/K",8300/(216.15*44e-6*(1/0.78-1/1.53))/1e5)
print("CF III",1/(1/373.15-R*log(2)/(2.26e6*0.018015)))
dH=R*log(760/400)/(1/72.25-1/77.35);print("CF IV",dH,1/(1/77.35+R*log(760/30)/dH))
h=log(1.25/.74)/(1/330-1/400);print("CF V",1/(1/330-log(1/.74)/h))
# mezclas
print("MZ I",R*298.15*(3*log(.9)+log(.1)))
print("MZ II",[p/x for p,x in [(32,.005),(76.9,.012),(121.8,.019)]])
print("MZ III KA",.041*34.121/.098,"KB",(1-.7284)*15.496/(1-.9105))
print("MZ IV",5*R*298*(.4*log(.4)+.6*log(.6)),"V",R*300*log(.98),"VI",R*298*log(.5),"VII",R*298*(.01*log(.01)+.99*log(.99)))
for x,y,P in [(0.098,.041,34.121),(.2476,.1154,30.9),(.3577,.1762,28.626),(.5194,.2772,25.239),(.6036,.3393,23.402),(.7188,.4450,20.698),(.8019,.5435,18.592),(.9105,.7284,15.496)]:
    a=y*P/12.295;print("MZ VIII",x,round(y*P,3),round((1-y)*P,3),round(a,3),round(a/x,3))
print("MZ IX",30*100/(10.5*.75),"X",273.15-1.86*120e3/(R*300)/1e3)
# cinetica
print("CI 1",log(2)/6.65e-4,"4",.1*exp(-log(2)/654*90),log(2)/654*.02)
print("CI 5 (v=-1/2 d/dt)",log(3)/(2*2.09e-3),"(k directo)",log(3)/2.09e-3)
Ea=R*log(1.16e-6/2.41e-10)/(1/300-1/400);print("CI 6",Ea,2.41e-10*exp(Ea/(R*300)))
for t,c in [(50,.0079),(100,.0065),(200,.0048),(300,.0038)]: print("CI 7",t,(1/c-100)/t, log(.01/c)/t)
print("CI 8",103930/(R*log(74.72e8/(log(2)/10))))
k1=1/5.9;k2=1/.42;Ea=1.987*log(k2/k1)/(1/700.15-1/781.15);print("CI 9",k1,k2,Ea,(1/.01-1/.05)/k1)
