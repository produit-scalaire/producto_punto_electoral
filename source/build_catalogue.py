# Genera catalogo-preguntas.html: todas las preguntas de questions.json, legibles de una vez, agrupadas por tema.
# Uso: python3 build_catalogue.py   (build.py también lo llama al final)
import json, html, os
here = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(here, 'questions.json')))
e = lambda s: html.escape(str(s))
parties = d['parties']
pname = {p['id']: p['name'] for p in parties}
REL = {1: 'baja', 2: 'media', 3: 'buena'}

by_theme = {}
for q in d['questions']:
    by_theme.setdefault(q['theme'], []).append(q)
order = [t for t in d['themes'] if t in by_theme] + [t for t in by_theme if t not in d['themes']]

def question_html(n, q):
    opts = q['options']
    rows = []
    for i, o in enumerate(opts):
        sp = q.get('split', {})
        def lab(p):
            c = sp.get(p); n = pname.get(p, p)
            if c and (c[0]-c[1])/sum(c) < 0.9: n += f" ({round(100*c[0]/sum(c))} % de la bancada: {c[0]} en ese sentido, {c[1]} en sentido contrario, {c[2]} abst.)"
            return n
        who = [lab(p) for p in pname if q['positions'].get(p) == i]
        who += [p for p, v in q['positions'].items() if v == i and p not in pname]
        rows.append(f'<tr><td class="opt"><b>{chr(65+i)}.</b> {e(o)}</td><td>{e(", ".join(who)) or "<span class=muted>ningún partido</span>"}</td></tr>')
    unknown = [pname[p] for p in pname if p not in q['positions']]
    if unknown:
        rows.append(f'<tr class="muted"><td class="opt">Posición no establecida</td><td>{e(", ".join(unknown))}</td></tr>')
    r = q.get('reliability', 0)
    src = ' · '.join(f'<a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["name"])}</a>' for s in q.get('sources', []))
    ordered = '<p class="note">Opciones graduadas (de un extremo al otro).</p>' if q.get('ordered') else ''
    nuance = f'<p><b>Matiz:</b> {e(q["nuance"])}</p>' if q.get('nuance') else ''
    ctx = f'<details open><summary>Contexto (i)</summary><p>{e(q["contexte"])}</p></details>' if q.get('contexte') else ''
    return f'''<article id="{e(q["id"])}">
  <h3><span class="num">{n}</span> {e(q["question"])}</h3>
  <p class="meta">{e(q.get("date",""))} · ref. <code>{e(q["id"])}</code> · confiabilidad <span class="dots">{"●"*r}{"○"*(3-r)}</span> {REL.get(r,"?")}</p>
  <p class="situation">{e(q["situation"])}</p>
  {ordered}<table><thead><tr><th>Respuesta</th><th>Partidos</th></tr></thead><tbody>{"".join(rows)}</tbody></table>
  <p><b>Fuente de la ubicación:</b> {e(q.get("actor",""))}</p>{nuance}{'<p class="note">Cohesión de las bancadas según la votación nominal. Una bancada dividida pesa menos en el cálculo.</p>' if q.get('split') else ''}
  <p class="src">{src}</p>{ctx}
</article>'''

body, toc, n = [], [], 0
for t in order:
    label = d['themes'].get(t, t)
    toc.append(f'<li><a href="#t-{e(t)}">{e(label)}</a> ({len(by_theme[t])})</li>')
    arts = []
    for q in by_theme[t]:
        n += 1
        arts.append(question_html(n, q))
    body.append(f'<section id="t-{e(t)}"><h2>{e(label)}</h2>{"".join(arts)}</section>')

page = f'''<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Catálogo de preguntas</title><style>
:root{{--bg:#fbfaf7;--fg:#1d1d1b;--muted:#6b6a65;--line:#e2dfd8;--card:#fff;--accent:#2f5d8a}}
@media (prefers-color-scheme:dark){{:root{{--bg:#161615;--fg:#ecebe6;--muted:#9a988f;--line:#33322f;--card:#1f1f1d;--accent:#8cb8e6}}}}
body{{margin:0;background:var(--bg);color:var(--fg);font:16px/1.55 ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif}}
main{{max-width:860px;margin:0 auto;padding:24px 16px 80px}}
h1{{margin:0 0 4px}} h2{{margin:48px 0 12px;padding-bottom:6px;border-bottom:2px solid var(--fg)}}
h3{{margin:0 0 4px;font-size:1.1em}} .num{{color:var(--muted);font-weight:400;margin-right:4px}}
article{{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:16px 18px;margin:14px 0}}
.meta,.muted,.note,.src{{color:var(--muted);font-size:.9em}} .situation{{font-style:italic}}
table{{width:100%;border-collapse:collapse;margin:10px 0;font-size:.95em}} th,td{{text-align:left;vertical-align:top;padding:6px 8px;border-top:1px solid var(--line)}}
th{{font-size:.8em;text-transform:uppercase;letter-spacing:.04em;color:var(--muted)}} td.opt{{width:45%}}
a{{color:var(--accent)}} .dots{{letter-spacing:1px}} details summary{{cursor:pointer;color:var(--accent)}}
.toc{{columns:2;padding-left:18px}} @media (max-width:560px){{.toc{{columns:1}} td.opt{{width:auto}}}}
@media print{{details{{display:block}} details>*{{display:block}} article{{break-inside:avoid}}}}
</style></head><body><main>
<h1>Catálogo de preguntas</h1>
<p class="meta">Banco del {e(d.get("version",""))} · {n} preguntas · {len(parties)} partidos. Generado desde <code>questions.json</code>.</p>
<p class="meta">Confiabilidad: qué tan sólida es la ubicación de los partidos (●●● votación nominal en el Congreso bancada por bancada, ●●○ posición pública o votación parcial reportada por la prensa, ●○○ caso local). «Posición no establecida»: partido ausente de la votación o sin posición conocida, no cuenta en el cálculo.</p>
<ul class="toc">{"".join(toc)}</ul>
{"".join(body)}
</main></body></html>
'''
out = os.path.join(here, 'catalogo-preguntas.html')
open(out, 'w').write(page)
print('catálogo ok', n, 'preguntas ->', out)
