# Genera los gráficos SVG del resumen (src/figuras/*.html). Las curvas se calculan, no se dibujan a ojo.
# Uso: python3 scripts/figuras.py   (después: node scripts/build.mjs)
from math import exp, log
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent / "src" / "figuras"
OUT.mkdir(exist_ok=True)

# Lienzo común: ejes de (L, B) a (R, T)
W, H = 380, 240
L, R, T, B = 48, 360, 18, 200

def sx(x, x0, x1):  # dato -> píxel horizontal
    return L + (x - x0) / (x1 - x0) * (R - L)

def sy(y, y0, y1):
    return B - (y - y0) / (y1 - y0) * (B - T)

def poly(pts, cls):
    return f'<polyline class="{cls}" points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}"/>'

def flecha_defs(fid):
    return (f'<defs><marker id="{fid}" viewBox="0 0 10 10" refX="9" refY="5" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" orient="auto-start-reverse">'
            f'<path class="flecha" d="M0,0 L10,5 L0,10 z"/></marker></defs>')

def ejes(xlab, ylab, fid):
    return (flecha_defs(fid) +
            f'<line class="eje" x1="{L}" y1="{B}" x2="{R+8}" y2="{B}" marker-end="url(#{fid})"/>'
            f'<line class="eje" x1="{L}" y1="{B}" x2="{L}" y2="{T-8}" marker-end="url(#{fid})"/>'
            f'<text x="{R+8}" y="{B+18}" text-anchor="end">{xlab}</text>'
            f'<text x="{L-8}" y="{T-12}" text-anchor="start">{ylab}</text>')

def figura(nombre, aria, cuerpo, caption, h=H):
    svg = (f'<figure class="fig"><svg viewBox="0 0 {W} {h}" role="img" aria-label="{aria}">{cuerpo}</svg>'
           f'<figcaption>{caption}</figcaption></figure>')
    (OUT / f"{nombre}.html").write_text(svg + "\n", encoding="utf-8")

# ---------- 1. Z vs p ----------
def z_vs_p():
    x0, x1, y0, y1 = 0, 10, 0.6, 1.6
    cuerpo = ejes("p", "Z", "a-z")
    yid = sy(1, y0, y1)
    cuerpo += f'<line class="guia" x1="{L}" y1="{yid:.1f}" x2="{R}" y2="{yid:.1f}"/><text class="m" x="{sx(7.8,x0,x1):.1f}" y="{yid+14:.1f}" text-anchor="middle">gas ideal (Z = 1)</text>'
    curvas = [("s1", "t1", "T baja", lambda p: 1 - 0.09 * p + 0.0095 * p * p),
              ("s3", "t3", "T de Boyle", lambda p: 1 + 0.0035 * p * p),
              ("s2", "t2", "T alta", lambda p: 1 + 0.045 * p)]
    for cls, tcls, lab, f in curvas:
        pts = [(sx(p / 10, x0, x1), sy(f(p / 10), y0, y1)) for p in range(0, 101)]
        cuerpo += poly(pts, cls)
        pos = {"T alta": (6.0, -10, "end"), "T de Boyle": (10, 18, "end"), "T baja": (1.3, 18, "start")}[lab]
        xe, ye = sx(pos[0], x0, x1), sy(f(pos[0]), y0, y1) + pos[1]
        cuerpo += f'<text class="{tcls}" x="{xe:.1f}" y="{ye:.1f}" text-anchor="{pos[2]}">{lab}</text>'
    cuerpo += f'<text class="m" x="{sx(5.2,x0,x1):.1f}" y="{sy(0.64,y0,y1):.1f}" text-anchor="middle">Z &lt; 1: dominan atracciones</text>'
    cuerpo += f'<text class="m" x="{sx(2.6,x0,x1):.1f}" y="{sy(1.5,y0,y1):.1f}" text-anchor="middle">Z &gt; 1: dominan repulsiones</text>'
    figura("z-vs-p", "Factor de compresión Z en función de la presión a tres temperaturas", cuerpo,
           "<b>Factor de compresión.</b> A T baja el gas real ocupa menos que el ideal (Z &lt; 1, atracciones); "
           "a presión alta siempre ganan las repulsiones (Z &gt; 1). En la temperatura de Boyle la curva sale horizontal: B = 0.")

# ---------- 2. Trabajo reversible vs irreversible ----------
def trabajo_pv():
    x0, x1, y0, y1 = 0, 4, 0, 1.2
    cuerpo = ejes("V", "p", "a-pv")
    Vi, Vf = 1.0, 3.0
    curva = [(sx(v / 100, x0, x1), sy(1 / (v / 100), y0, y1)) for v in range(int(Vi * 100) - 30, int(Vf * 100) + 61)]
    bajo = [(sx(v / 100, x0, x1), sy(1 / (v / 100), y0, y1)) for v in range(int(Vi * 100), int(Vf * 100) + 1)]
    area = f'M{sx(Vi,x0,x1):.1f},{B} ' + " ".join(f"L{x:.1f},{y:.1f}" for x, y in bajo) + f' L{sx(Vf,x0,x1):.1f},{B} Z'
    cuerpo += f'<path class="f1" d="{area}"/>'
    pf = 1 / Vf
    cuerpo += f'<rect class="f2" x="{sx(Vi,x0,x1):.1f}" y="{sy(pf,y0,y1):.1f}" width="{sx(Vf,x0,x1)-sx(Vi,x0,x1):.1f}" height="{B-sy(pf,y0,y1):.1f}"/>'
    cuerpo += poly(curva, "s1")
    cuerpo += f'<line class="s2" x1="{sx(Vi,x0,x1):.1f}" y1="{sy(pf,y0,y1):.1f}" x2="{sx(Vf,x0,x1):.1f}" y2="{sy(pf,y0,y1):.1f}"/>'
    for v, lab in ((Vi, "i"), (Vf, "f")):
        cx, cy = sx(v, x0, x1), sy(1 / v, y0, y1)
        cuerpo += f'<circle class="pt" cx="{cx:.1f}" cy="{cy:.1f}" r="4"/><text x="{cx+8:.1f}" y="{cy-6:.1f}">{lab}</text>'
        cuerpo += f'<line class="guia" x1="{cx:.1f}" y1="{cy:.1f}" x2="{cx:.1f}" y2="{B}"/>'
    cuerpo += f'<text class="t1" x="{sx(1.6,x0,x1):.1f}" y="{sy(0.82,y0,y1):.1f}">isoterma p = nRT/V</text>'
    cuerpo += f'<text class="t1" x="{sx(1.4,x0,x1):.1f}" y="{sy(0.42,y0,y1):.1f}" text-anchor="middle">w reversible</text>'
    cuerpo += f'<text class="t2" x="{sx(2.0,x0,x1):.1f}" y="{sy(0.15,y0,y1):.1f}" text-anchor="middle">w contra p<tspan dy="3" font-size="9">ex</tspan><tspan dy="-3"> = p</tspan><tspan dy="3" font-size="9">f</tspan></text>'
    figura("trabajo-pv", "Trabajo de expansión: área bajo la isoterma versus rectángulo a presión externa constante", cuerpo,
           "<b>Expansión isotérmica de i a f.</b> El trabajo que entrega el gas es el área bajo la curva que se recorre. "
           "En un paso contra p<sub>ex</sub> = p<sub>f</sub> es el rectángulo naranja; en infinitos pasos (reversible) es toda el área azul: el máximo posible.")

# ---------- 4. Cuadrantes de espontaneidad ----------
def cuadrantes():
    cx, cy, w, h = 190, 118, 150, 88
    c = flecha_defs("a-q")
    celdas = [(cx - w, cy - h, "bien", "ΔH &lt; 0 · ΔS &gt; 0", "espontánea siempre"),
              (cx, cy - h, "depende", "ΔH &gt; 0 · ΔS &gt; 0", "espontánea a T altas"),
              (cx - w, cy, "depende", "ΔH &lt; 0 · ΔS &lt; 0", "espontánea a T bajas"),
              (cx, cy, "mal", "ΔH &gt; 0 · ΔS &lt; 0", "nunca espontánea")]
    for x, y, cls, a, b in celdas:
        c += f'<rect class="{cls}" x="{x+3}" y="{y+3}" width="{w-6}" height="{h-6}" rx="8"/>'
        c += f'<text x="{x+w/2}" y="{y+h/2-6}" text-anchor="middle" font-weight="600">{b}</text>'
        c += f'<text class="m" x="{x+w/2}" y="{y+h/2+14}" text-anchor="middle">{a}</text>'
    c += f'<line class="eje" x1="{cx-w-6}" y1="{cy}" x2="{cx+w+10}" y2="{cy}" marker-end="url(#a-q)"/>'
    c += f'<line class="eje" x1="{cx}" y1="{cy+h+6}" x2="{cx}" y2="{cy-h-10}" marker-end="url(#a-q)"/>'
    c += f'<text x="{cx+w+10}" y="{cy+16}" text-anchor="end">ΔH</text><text x="{cx+8}" y="{cy-h-2}">ΔS</text>'
    figura("cuadrantes", "Signo de delta H y delta S y espontaneidad en cada cuadrante", c,
           "<b>ΔG = ΔH − TΔS.</b> Si los signos coinciden, decide la temperatura: el cambio ocurre en T = ΔH/ΔS (con ΔS en kJ/K).", h=240)

# ---------- 5. G vs avance ----------
def g_vs_xi():
    x0, x1, y0, y1 = 0, 1, 0, 1
    c = ejes("ξ", "G", "a-g")
    xe = 0.62
    g = lambda x: 0.25 + 1.6 * (x - xe) ** 2 + 0.15 * (x - xe) ** 3
    pts = [(sx(i / 100, x0, x1), sy(g(i / 100), y0, y1)) for i in range(2, 99)]
    c += poly(pts, "s1")
    ex, ey = sx(xe, x0, x1), sy(g(xe), y0, y1)
    c += f'<line class="guia" x1="{ex:.1f}" y1="{ey:.1f}" x2="{ex:.1f}" y2="{B}"/><circle class="pt1" cx="{ex:.1f}" cy="{ey:.1f}" r="5"/>'
    c += f'<text x="{ex:.1f}" y="{ey-44:.1f}" text-anchor="middle" font-weight="600">equilibrio: Q = K, ΔrG = 0</text>'
    c += f'<text class="m" x="{ex:.1f}" y="{B+16}" text-anchor="middle">ξ eq</text>'
    for xa, xb, txt in ((0.18, 0.34, "Q &lt; K: avanza →"), (0.95, 0.82, "← Q &gt; K: retrocede")):
        ya, yb = sy(g(xa), y0, y1), sy(g(xb), y0, y1)
        c += f'<line class="s2" x1="{sx(xa,x0,x1):.1f}" y1="{ya-14:.1f}" x2="{sx(xb,x0,x1):.1f}" y2="{yb-14:.1f}" marker-end="url(#a-g)"/>'
        c += f'<text class="t2" x="{sx((xa+xb)/2,x0,x1):.1f}" y="{min(ya,yb)-24:.1f}" text-anchor="middle">{txt}</text>'
    c += f'<text class="m" x="{sx(0.02,x0,x1):.1f}" y="{B+16}">reactivos</text><text class="m" x="{R-24}" y="{B+16}" text-anchor="end">productos</text>'
    figura("g-vs-xi", "Energía libre en función del avance de reacción con mínimo en el equilibrio", c,
           "<b>La reacción baja por la curva de G.</b> La pendiente es ΔrG = ΔrG° + RT ln Q: negativa si Q &lt; K (avanza), positiva si Q &gt; K (retrocede) y cero en el mínimo, que es el equilibrio.")

# ---------- 6a. Diagrama de fases ----------
def diagrama_fases():
    c = ejes("T", "p", "a-f")
    tx, ty = 150, 140   # punto triple
    kx, ky = 300, 52    # punto crítico
    sub = [(x, ty + (tx - x) ** 2 / 2200 * 0 + (tx - x) * 0.45 + (tx - x) ** 2 * 0.0006) for x in range(58, tx + 1)]
    sub = [(x, min(y, B - 2)) for x, y in sub]
    vap = [(tx + (kx - tx) * t, ty + (ky - ty) * t + 18 * t * (1 - t)) for t in [i / 60 for i in range(61)]]
    c += poly(sub, "s3") + poly(vap, "s3")
    c += f'<line class="s1" x1="{tx}" y1="{ty}" x2="{tx+22}" y2="{T+4}"/>'
    c += f'<line class="s2 d" x1="{tx}" y1="{ty}" x2="{tx-22}" y2="{T+4}"/>'
    c += f'<circle class="pt" cx="{tx}" cy="{ty}" r="4.5"/><circle class="pt" cx="{kx}" cy="{ky}" r="4.5"/>'
    c += f'<text x="{tx+10}" y="{ty+16}">punto triple (F = 0)</text>'
    c += f'<text x="{kx-6}" y="{ky-10}" text-anchor="end">punto crítico</text>'
    c += f'<text x="{L+30}" y="{T+40}" font-weight="600">sólido</text>'
    c += f'<text x="{205}" y="{72}" text-anchor="middle" font-weight="600">líquido</text>'
    c += f'<text x="{tx+80}" y="{B-28}" font-weight="600">gas</text>'
    c += f'<text class="m" x="{kx+4}" y="{ky+28}">fluido</text><text class="m" x="{kx+4}" y="{ky+41}">supercrítico</text>'
    c += f'<text class="t1" x="{tx+26}" y="{T+12}">ΔV<tspan dy="3" font-size="9">fus</tspan><tspan dy="-3"> &gt; 0</tspan></text>'
    c += f'<text class="t2" x="{tx-26}" y="{T+12}" text-anchor="end">agua: ΔV<tspan dy="3" font-size="9">fus</tspan><tspan dy="-3"> &lt; 0</tspan></text>'
    c += f'<text class="t3" x="{118}" y="{190}">sublimación</text>'
    figura("diagrama-fases", "Diagrama de fases presión temperatura con punto triple, punto crítico y las dos pendientes posibles de la curva sólido líquido", c,
           "<b>Las curvas son coexistencia de dos fases (F = 1).</b> La pendiente sólido-líquido sale de Clapeyron, dp/dT = ΔH<sub>fus</sub>/(TΔV<sub>fus</sub>): "
           "si la fusión normal está a <b>mayor</b> T que el punto triple, ΔV &gt; 0 y el sólido es más denso; si está a <b>menor</b> T (como el agua), el sólido ocupa más.")

# ---------- 6b. mu vs T ----------
def mu_vs_t():
    c = ejes("T", "μ", "a-m")
    sol = lambda x: 70 + 0.15 * (x - 40)
    liq = lambda x: 83.5 + 0.35 * (x - 130)
    gas = lambda x: 125.5 + 0.8 * (x - 250)
    tf, te = 130, 250
    c += poly([(x, sol(x)) for x in (40, 330)], "s1 d") + poly([(x, sol(x)) for x in (40, tf)], "s1 grueso")
    c += poly([(x, liq(x)) for x in (100, 330)], "s3 d") + poly([(x, liq(x)) for x in (tf, te)], "s3 grueso")
    c += poly([(x, gas(x)) for x in (165, 330)], "s2 d") + poly([(x, gas(x)) for x in (te, 330)], "s2 grueso")
    for x, lab, f in ((tf, "T<tspan dy='3' font-size='9'>f</tspan>", sol), (te, "T<tspan dy='3' font-size='9'>e</tspan>", liq)):
        c += f'<line class="guia" x1="{x}" y1="{f(x):.1f}" x2="{x}" y2="{B}"/><text class="m" x="{x}" y="{B+16}" text-anchor="middle">{lab}</text>'
    c += f'<text class="t1" x="{L+8}" y="{sol(40)-8:.1f}">sólido</text>'
    c += f'<text class="t3" x="{190}" y="{liq(190)+20:.1f}" text-anchor="middle">líquido</text>'
    c += f'<text class="t2" x="{296}" y="{178}" text-anchor="end">gas</text>'
    figura("mu-vs-t", "Potencial químico de sólido, líquido y gas en función de la temperatura a presión constante", c,
           "<b>La fase estable es la de menor μ</b> (tramo grueso). La pendiente es −S<sub>m</sub>: el gas, más desordenado, baja más rápido. Donde se cruzan las rectas están T<sub>f</sub> y T<sub>e</sub>.")

# ---------- 7. Raoult y Henry ----------
def raoult_henry():
    x0, x1, y0, y1 = 0, 1, 0, 1
    c = ejes("x<tspan dy='3' font-size='9'>B</tspan>", "p<tspan dy='3' font-size='9'>B</tspan>", "a-r")
    ps, gam = 0.62, 0.85
    real = lambda x: ps * x * exp(gam * (1 - x) ** 2)
    K = ps * exp(gam)
    c += poly([(sx(0, x0, x1), sy(0, y0, y1)), (sx(1, x0, x1), sy(ps, y0, y1))], "s1 d")
    c += poly([(sx(0, x0, x1), sy(0, y0, y1)), (sx(0.6, x0, x1), sy(K * 0.6, y0, y1))], "s2 d")
    c += poly([(sx(i / 100, x0, x1), sy(real(i / 100), y0, y1)) for i in range(0, 101)], "s3")
    c += f'<circle class="pt1" cx="{sx(1,x0,x1):.1f}" cy="{sy(ps,y0,y1):.1f}" r="4.5"/>'
    c += f'<text class="t1" x="{sx(0.74,x0,x1):.1f}" y="{sy(ps*0.74,y0,y1)+30:.1f}" text-anchor="middle">Raoult: p = x p*</text>'
    c += f'<text class="t2" x="{sx(0.6,x0,x1)+4:.1f}" y="{sy(K*0.6,y0,y1):.1f}">Henry: p = K x</text>'
    c += f'<text class="t3" x="{sx(0.45,x0,x1):.1f}" y="{sy(real(0.45),y0,y1)-10:.1f}" text-anchor="middle">real</text>'
    c += f'<text class="m" x="{sx(1,x0,x1):.1f}" y="{sy(ps,y0,y1)-10:.1f}" text-anchor="end">p*<tspan dy="3" font-size="8">B</tspan></text>'
    c += f'<text class="m" x="{sx(0.02,x0,x1):.1f}" y="{B+16}">soluto diluido</text><text class="m" x="{R-24}" y="{B+16}" text-anchor="end">B casi puro</text>'
    figura("raoult-henry", "Presión parcial real de un componente comparada con las rectas de Raoult y de Henry", c,
           "<b>Cada ley vale en un extremo.</b> Diluido, el soluto sigue Henry (recta tangente en x → 0, pendiente K ≠ p*); "
           "casi puro, sigue Raoult (recta hasta p*). Solvente en Raoult + soluto en Henry = solución idealmente diluida.")

# ---------- 8a. Primer orden ----------
def primer_orden():
    x0, x1, y0, y1 = 0, 4.2, 0, 1.1
    c = ejes("t", "[A]", "a-c")
    pts = [(sx(t / 50, x0, x1), sy(exp(-log(2) * t / 50), y0, y1)) for t in range(0, 211)]
    c += poly(pts, "s1")
    for n in range(4):
        y = 0.5 ** n
        px, py = sx(n, x0, x1), sy(y, y0, y1)
        c += f'<circle class="pt1" cx="{px:.1f}" cy="{py:.1f}" r="4"/>'
        c += f'<line class="guia" x1="{L}" y1="{py:.1f}" x2="{px:.1f}" y2="{py:.1f}"/>'
        if n:
            c += f'<line class="guia" x1="{px:.1f}" y1="{py:.1f}" x2="{px:.1f}" y2="{B}"/>'
            c += f'<text class="m" x="{(sx(n-1,x0,x1)+px)/2:.1f}" y="{B+16}" text-anchor="middle">t½</text>'
        lab = ["[A]₀", "½", "¼", "⅛"][n]
        c += f'<text class="m" x="{L-6}" y="{py+4:.1f}" text-anchor="end">{lab}</text>'
    c += f'<text class="t1" x="{sx(2.2,x0,x1):.1f}" y="{sy(0.5,y0,y1):.1f}">[A] = [A]₀ e<tspan dy="-5" font-size="9">−kt</tspan></text>'
    figura("primer-orden", "Decaimiento exponencial de primer orden con vidas medias iguales", c,
           "<b>Primer orden: cada t½ = ln2/k reduce [A] a la mitad, sin importar de dónde se parte.</b> "
           "Por eso, si te dan dos concentraciones, k = ln(C₀/C)/t, y el tiempo hasta C<sub>f</sub> es ln(C₀/C<sub>f</sub>)/k.")

# ---------- 8b. Perfil de energía ----------
def perfil_energia():
    c = flecha_defs("a-e")
    c += f'<line class="eje" x1="{L}" y1="{B}" x2="{R+8}" y2="{B}" marker-end="url(#a-e)"/>'
    c += f'<line class="eje" x1="{L}" y1="{B}" x2="{L}" y2="{T-8}" marker-end="url(#a-e)"/>'
    c += f'<text x="{R+8}" y="{B+18}" text-anchor="end">avance de reacción</text><text x="{L-8}" y="{T-12}">E</text>'
    yr, yp = 140, 172
    def camino(alto):
        pts = []
        for i in range(101):
            t = i / 100
            base = yr + (yp - yr) * (3 * t * t - 2 * t ** 3)
            pts.append((70 + 270 * t, base - alto * exp(-((t - 0.45) / 0.16) ** 2)))
        return pts
    c += poly(camino(110), "s2") + poly(camino(55), "s1")
    xr, xp, xm = 70, 340, 70 + 270 * 0.45
    c += f'<line class="guia" x1="{xr}" y1="{yr}" x2="{xm-20}" y2="{yr}"/><line class="guia" x1="{xm+30}" y1="{yp}" x2="{xp}" y2="{yp}"/>'
    c += f'<line class="eje" x1="{xm-60}" y1="{yr}" x2="{xm-60}" y2="{yr-104}" marker-end="url(#a-e)"/>'
    c += f'<text class="t2" x="{xm-66}" y="{yr-60}" text-anchor="end">E<tspan dy="3" font-size="9">a</tspan></text>'
    c += f'<line class="eje" x1="{xm+50}" y1="{yr}" x2="{xm+50}" y2="{yr-49}" marker-end="url(#a-e)"/>'
    c += f'<text class="t1" x="{xm+56}" y="{yr-26}">E<tspan dy="3" font-size="9">a</tspan><tspan dy="-3"> con catalizador</tspan></text>'
    c += f'<line class="eje" x1="{xp-10}" y1="{yr}" x2="{xp-10}" y2="{yp-2}" marker-end="url(#a-e)"/><text x="{xp-16}" y="{(yr+yp)/2+4}" text-anchor="end">ΔH</text>'
    c += f'<text class="m" x="{xr}" y="{yr-8}">reactivos</text><text class="m" x="{xp}" y="{yp+16}" text-anchor="end">productos</text>'
    c += f'<text class="t2" x="{xm}" y="{T+6}" text-anchor="middle">sin catalizador</text>'
    figura("perfil-energia", "Perfil de energía de una reacción con y sin catalizador", c,
           "<b>El catalizador baja la barrera, no los extremos.</b> Cambia E<sub>a</sub> (y la velocidad), pero ΔH, ΔG y K quedan iguales.")

# ---------- 9. Isoterma de sorción con histéresis ----------
def isoterma():
    x0, x1, y0, y1 = 0, 1, 0, 1
    c = ejes("a<tspan dy='3' font-size='9'>w</tspan>", "humedad", "a-i")
    mm, cc, K = 0.22, 12, 0.85
    gab = lambda a: mm * cc * K * a / ((1 - K * a) * (1 - K * a + cc * K * a))
    ads = [(sx(i / 100, x0, x1), sy(gab(i / 100), y0, y1)) for i in range(0, 96)]
    des = [(sx(i / 100, x0, x1), sy(gab(i / 100) + 0.22 * (i / 100) ** 0.9 * (1 - (i / 95) ** 4), y0, y1)) for i in range(0, 96)]
    c += poly(ads, "s1") + poly(des, "s2 d")
    am = 0.12
    px, py = sx(am, x0, x1), sy(gab(am), y0, y1)
    c += f'<circle class="pt" cx="{px:.1f}" cy="{py:.1f}" r="4.5"/><text x="{px+8:.1f}" y="{py+18:.1f}">humedad de monocapa</text>'
    c += f'<text class="t1" x="{sx(0.62,x0,x1):.1f}" y="{sy(gab(0.62),y0,y1)+20:.1f}">adsorción</text>'
    c += f'<text class="t2" x="{sx(0.5,x0,x1):.1f}" y="{sy(gab(0.5)+0.22*0.5**0.9*(1-(50/95)**4),y0,y1)-10:.1f}" text-anchor="end">desorción</text>'
    c += f'<text class="m" x="{sx(0.36,x0,x1):.1f}" y="{T+30}" text-anchor="middle">histéresis: más agua al secar</text>'
    figura("isoterma", "Isoterma de sorción de agua con humedad de monocapa y lazo de histéresis", c,
           "<b>Isoterma de sorción (tipo II, BET/GAB).</b> El codo marca la monocapa, el punto de máxima estabilidad. "
           "La curva de desorción queda arriba: a igual a<sub>w</sub>, el alimento retiene más agua cuando se seca que cuando se humedece.")

for f in (z_vs_p, trabajo_pv, cuadrantes, g_vs_xi, diagrama_fases, mu_vs_t, raoult_henry, primer_orden, perfil_energia, isoterma):
    f()
print("figuras:", sorted(p.stem for p in OUT.glob("*.html")))
