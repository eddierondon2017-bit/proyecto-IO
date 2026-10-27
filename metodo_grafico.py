# metodo_grafico.py: 2 variables
from fractions import Fraction
from modelo import fmt


class Vertice:
    def __init__(self, x1, x2, z):
        self.x1, self.x2, self.z = x1, x2, z
        self.activas = []
        self.es_optimo = False


class Resultado:
    def __init__(self):
        self.estado = ""     # optimo, alternativos, infactible, no_acotado
        self.vertices = []
        self.pasos = []


def cumple(p, x1, x2):
    # punto factible?
    if x1 < 0 or x2 < 0:
        return False
    for r in p.restricciones:
        v = r["coef"][0] * x1 + r["coef"][1] * x2
        if r["signo"] == "<=" and v > r["b"]:
            return False
        if r["signo"] == ">=" and v < r["b"]:
            return False
        if r["signo"] == "=" and v != r["b"]:
            return False
    return True


def rayo_mejora(p):
    # no acotado? revisa rayos
    c1, c2 = p.costos
    cand = [(1, 0), (0, 1)]
    for r in p.restricciones:
        a1, a2 = r["coef"]
        cand += [(a2, -a1), (-a2, a1)]
    for d1, d2 in cand:
        if d1 < 0 or d2 < 0 or (d1 == 0 and d2 == 0):
            continue
        ok = True
        for r in p.restricciones:
            dot = r["coef"][0] * d1 + r["coef"][1] * d2
            if (r["signo"] == "<=" and dot > 0) or (r["signo"] == ">=" and dot < 0) \
                    or (r["signo"] == "=" and dot != 0):
                ok = False
        if not ok:
            continue
        val = c1 * d1 + c2 * d2
        if (p.objetivo == "max" and val > 0) or (p.objetivo == "min" and val < 0):
            return True
    return False


def resolver(p):
    if p.n != 2:
        raise ValueError("El metodo grafico necesita exactamente 2 variables")
    res = Resultado()
    # rectas: restricciones y ejes
    lineas = [(r["coef"][0], r["coef"][1], r["b"], r["nombre"]) for r in p.restricciones]
    lineas.append((Fraction(1), Fraction(0), Fraction(0), p.nombres[0] + " = 0"))
    lineas.append((Fraction(0), Fraction(1), Fraction(0), p.nombres[1] + " = 0"))
    res.pasos.append("Paso 1: dibujar cada restriccion como recta")
    for a1, a2, b, nom in lineas:
        res.pasos.append(f"   {nom}: {fmt(a1)}*x1 + {fmt(a2)}*x2 = {fmt(b)}")

    # cruces de rectas
    puntos = {}
    for i in range(len(lineas)):
        for j in range(i + 1, len(lineas)):
            a1, a2, b, _ = lineas[i]
            d1, d2, e, _ = lineas[j]
            det = a1 * d2 - a2 * d1
            if det == 0:
                continue
            x1 = (b * d2 - a2 * e) / det
            x2 = (a1 * e - b * d1) / det
            if cumple(p, x1, x2):
                puntos[(x1, x2)] = True
    res.pasos.append("Paso 2: vertices factibles (cruces que cumplen todo)")
    for (x1, x2) in sorted(puntos):
        v = Vertice(x1, x2, p.costos[0] * x1 + p.costos[1] * x2)
        v.activas = [nom for a1, a2, b, nom in lineas if a1 * x1 + a2 * x2 == b]
        res.vertices.append(v)
        res.pasos.append(f"   ({fmt(x1)}, {fmt(x2)})  z = {fmt(v.z)}  activas: {', '.join(v.activas)}")

    if not res.vertices:
        res.estado = "infactible"
        res.pasos.append("Paso 3: no hay region factible")
        return res
    if rayo_mejora(p):
        res.estado = "no_acotado"
        res.pasos.append("Paso 3: la region se abre y z mejora sin limite")
        return res

    zs = [v.z for v in res.vertices]
    mejor = max(zs) if p.objetivo == "max" else min(zs)
    for v in res.vertices:
        v.es_optimo = (v.z == mejor)
    n_opt = sum(v.es_optimo for v in res.vertices)
    res.estado = "alternativos" if n_opt > 1 else "optimo"
    res.pasos.append(f"Paso 3: mejor z = {fmt(mejor)} ({'maximo' if p.objetivo == 'max' else 'minimo'})")
    return res


def interpretar(p, res):
    # frase final
    ops = [v for v in res.vertices if v.es_optimo]
    if not ops:
        return ""
    partes = []
    for v in ops:
        txt = ", ".join(f"{p.nombres[k]} = {fmt(val)} {p.unidades[k]}".strip()
                        for k, val in enumerate((v.x1, v.x2)))
        partes.append(txt)
    z = f"{fmt(ops[0].z)} {p.unidad_z}".strip()
    if len(ops) > 1:
        return "Varios vertices dan el mismo z = " + z + ": " + " | ".join(partes)
    return f"Optimo: {partes[0]}, z = {z}"