# verificacion_externa.py: compara con scipy
# SOLO para comprobar, el codigo del grupo no usa scipy
import json
import os

import metodo_grafico as mg
import simplex_dual as sd
from modelo import construir_problema

RUTA = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ejemplos.json")


def con_scipy(p):
    from scipy.optimize import linprog
    sg = 1 if p.objetivo == "min" else -1
    a_ub, b_ub, a_eq, b_eq = [], [], [], []
    for r in p.restricciones:
        fila = [float(v) for v in r["coef"]]
        b = float(r["b"])
        if r["signo"] == "<=":
            a_ub.append(fila); b_ub.append(b)
        elif r["signo"] == ">=":
            a_ub.append([-v for v in fila]); b_ub.append(-b)
        else:
            a_eq.append(fila); b_eq.append(b)
    res = linprog([sg * float(c) for c in p.costos], A_ub=a_ub or None, b_ub=b_ub or None,
                  A_eq=a_eq or None, b_eq=b_eq or None, bounds=(0, None), method="highs")
    if res.status == 0:
        return "optimo", sg * res.fun
    return {2: "infactible", 3: "no_acotado"}.get(res.status, "otro"), None


def main():
    try:
        import scipy  # noqa: F401
    except ImportError:
        print("Instale scipy: pip install scipy")
        return
    with open(RUTA, encoding="utf-8") as f:
        ejemplos = json.load(f)
    print(f"{'Ejemplo':38}{'scipy':>20}{'grafico':>20}{'dual':>20}")
    for nombre, datos in ejemplos.items():
        p, _ = construir_problema(datos)
        est, z = con_scipy(p)
        col_s = f"{est} {z:g}" if z is not None else est
        col_g = col_d = "-"
        if p.n == 2:
            g = mg.resolver(p)
            zg = [v.z for v in g.vertices if v.es_optimo]
            col_g = f"{g.estado} {float(zg[0]):g}" if zg else g.estado
        d = sd.resolver(p)
        col_d = f"{d.estado} {float(d.z):g}" if d.z is not None else d.estado
        print(f"{nombre:38}{col_s:>20}{col_g:>20}{col_d:>20}")


if __name__ == "__main__":
    main()