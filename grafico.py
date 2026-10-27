# grafico.py: dibuja region
from matplotlib.figure import Figure


def cortar(poli, f):
    # recorta poligono
    sal = []
    for i in range(len(poli)):
        p, q = poli[i], poli[(i + 1) % len(poli)]
        fp, fq = f(p), f(q)
        if fp >= 0:
            sal.append(p)
        if (fp >= 0) != (fq >= 0):
            t = fp / (fp - fq)
            sal.append((p[0] + t * (q[0] - p[0]), p[1] + t * (q[1] - p[1])))
    return sal


def dibujar(p, res):
    fig = Figure(figsize=(8, 6))
    ax = fig.subplots()
    xs = [float(v.x1) for v in res.vertices]
    ys = [float(v.x2) for v in res.vertices]
    lim1 = max(xs) * 1.3 if xs and max(xs) > 0 else 10
    lim2 = max(ys) * 1.3 if ys and max(ys) > 0 else 10

    # region sombreada
    poli = [(0, 0), (lim1, 0), (lim1, lim2), (0, lim2)]
    for r in p.restricciones:
        a1, a2, b = float(r["coef"][0]), float(r["coef"][1]), float(r["b"])
        if r["signo"] in ("<=", "="):
            poli = cortar(poli, lambda q, a1=a1, a2=a2, b=b: b - (a1 * q[0] + a2 * q[1])) if poli else poli
        if r["signo"] in (">=", "="):
            poli = cortar(poli, lambda q, a1=a1, a2=a2, b=b: (a1 * q[0] + a2 * q[1]) - b) if poli else poli
    if len(poli) >= 3:
        ax.fill([q[0] for q in poli], [q[1] for q in poli], color="#9ecae1", alpha=0.5, label="Region factible")

    # rectas
    for r in p.restricciones:
        a1, a2, b = float(r["coef"][0]), float(r["coef"][1]), float(r["b"])
        if a2 != 0:
            ax.plot([0, lim1], [b / a2, (b - a1 * lim1) / a2], label=f"{r['nombre']} ({r['signo']})")
        else:
            ax.plot([b / a1, b / a1], [0, lim2], label=f"{r['nombre']} ({r['signo']})")

    # vertices
    for v in res.vertices:
        ax.scatter(float(v.x1), float(v.x2), color="red" if v.es_optimo else "black",
                   marker="*" if v.es_optimo else "o", s=200 if v.es_optimo else 40, zorder=5)
        ax.annotate(f"z={float(v.z):g}", (float(v.x1), float(v.x2)),
                    textcoords="offset points", xytext=(6, 6), fontsize=8)

    ax.set_xlim(0, lim1)
    ax.set_ylim(0, lim2)
    ax.set_xlabel(f"{p.nombres[0]} ({p.unidades[0]})")
    ax.set_ylabel(f"{p.nombres[1]} ({p.unidades[1]})")
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=8, loc="upper right")
    return fig