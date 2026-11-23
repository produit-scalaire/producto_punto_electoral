# Agrega a questions.json, para cada pregunta basada en una votación nominal, la distribución de los votos de cada bancada
# (votos_bancadas.json). Campo escrito: q["split"][partido] = [con su posición, en contra, abstención].
# Uso: python3 add_cohesion.py   (luego python3 build.py)
import json, os
here = os.path.dirname(os.path.abspath(__file__))
QP = os.path.join(here, 'questions.json')
d = json.load(open(QP)); V = json.load(open(os.path.join(here, 'votos_bancadas.json')))
# Nombre de la bancada en la fuente -> id del partido en questions.json (se completa en el paso 2)
GROUPES = {'COM':'COM','PH':'PH','AV':'AV','LIB':'LIB','U':'U','CR':'CR','PC':'PC','CD':'CD'}
done = 0
for q in d['questions']:
    q.pop('split', None)
    if q['id'] not in V or len(q['options']) != 2: continue
    v = {GROUPES[g]: c for g, c in V[q['id']].items() if g in GROUPES}  # bancadas que no se comparan: se ignoran
    # ¿qué opción corresponde al «sí»? se deduce de las bancadas mayoritariamente a favor o en contra
    pour_opt = set()
    for p, pos in q['positions'].items():
        c = v.get(p)
        if not c or sum(c) == 0 or c[2] >= max(c[0], c[1]): continue
        pour_opt.add(pos if c[0] > c[1] else 1 - pos)
    if len(pour_opt) != 1:
        print('incoherente, se ignora:', q['id'], pour_opt); continue
    po = pour_opt.pop(); split = {}
    for p, pos in q['positions'].items():
        c = v.get(p)
        if not c or sum(c) == 0: continue
        w, a = (c[0], c[1]) if pos == po else (c[1], c[0])
        if w < a or c[2] > w: continue   # posición fijada por otra vía que esta votación: no se toca
        split[p] = [w, a, c[2]]
    q['split'] = split; done += 1
json.dump(d, open(QP, 'w'), ensure_ascii=False, indent=1)
print('cohesión agregada en', done, 'preguntas')
