# Extrae de las actas oficiales (Gaceta del Congreso) el voto de cada senador en las votaciones del Senado
# que usan las preguntas, y escribe votos_senadores.json (comparación senador por senador en los resultados).
# Uso: python3 extraer_senadores.py CARPETA_CACHE   (descarga las actas y el padrón ahí; requiere pdftotext)
# Cada votación se valida contra los totales que anuncia el acta: si un conteo no coincide, el script se detiene.
import json, os, re, subprocess, sys, unicodedata, difflib
here = os.path.dirname(os.path.abspath(__file__))
CACHE = sys.argv[1] if len(sys.argv) > 1 else os.path.join(here, '.cache-actas')
os.makedirs(CACHE, exist_ok=True)
SIDN = 'https://sidn.ramajudicial.gov.co/SIDN/PUBLICACIONES%20PERIODICAS/TEXTO%20COMPLETO%20Y%20TABLAS%20DE%20CONTENIDO/GACETA%20DEL%20CONGRESO/GACETA%20DEL%20CONGRESO%20'
def gc(n, y): return f'{SIDN}{y}/GC%20{n:04d}%20DE%20{y}.PDF'
# pregunta -> (acta, comienzo del título de la votación nominal en el acta, sí, no anunciados por el acta)
VOTOS = {
 'reforma-pensional': (gc(1711, 2024), 'Proposición Negativa presentada por la honorable Senadora Beatriz Lorena Ríos', 41, 50),
 'consulta-popular': ('https://apicongresovisible.uniandes.edu.co/uploads/proyecto-ley/13271/989/25.pdf', 'solicitud de concepto favorable', 47, 49),
 'voto-electronico': (gc(1257, 2023), 'proposiciones no avaladas de los artículos: 153, 154 y 162', 25, 39),
 'presupuesto-2023': ('https://apicongresovisible.uniandes.edu.co/uploads/votacion/14408/Votaciones%20plenaria%20senado%20pto.pdf', 'proposición positiva con que termina el informe de ponencia del Proyecto de ley número 88', 66, 12),
 'impuesto-iglesias': ('https://apicongresovisible.uniandes.edu.co/uploads/votacion/14430/gaceta_121.pdf', 'proposición eliminando el articulo 15', 60, 28),
 'impuesto-ultraprocesados': ('https://apicongresovisible.uniandes.edu.co/uploads/votacion/14430/gaceta_121.pdf', 'proposición de eliminación al artículo 45', 31, 42),
 'impuesto-plasticos': ('https://apicongresovisible.uniandes.edu.co/uploads/votacion/14430/gaceta_121.pdf', 'eliminación de los artículos 42 y 43', 24, 59),
 'pension-semanas-mujeres': (gc(1813, 2024), 'artículo 36 con la proposición modificativa', 43, 40),
 'cannabis-uso-adulto': (gc(1361, 2023), 'Proposición Positiva con que termina el Informe de Ponencia al Proyecto de Acto Legislativo número 33', 47, 43),
 'censura-irene-velez': (gc(433, 2023), 'moción de censura', 16, 58),
 'divorcio-unilateral': (gc(325, 2024), 'omisión de la lectura del articulado, el articulado en bloque con la proposición modificativa al artículo 3', 59, 11),
 'ministerio-igualdad': (gc(244, 2023), 'proposición positiva con que termina el informe de ponencia al Proyecto de ley número 222', 66, 11),
 'igualdad-cuidadoras-animales': (gc(244, 2023), 'proposición al artículo 5° presentado por la honorable Senadora Andrea Padilla', 23, 50),
 'singapur-alianza-pacifico': (gc(16, 2023), 'proposición positiva con que termina el Informe de Ponencia del Proyecto de ley número 375', 71, 12),
 # el acta anuncia 43 por el no, pero su lista repite a un senador (Riascos) y la Secretaría corrige a 42 en la sesión
 'campesinado-consulta-previa': (gc(607, 2023), 'proposición aditiva al artículo 1', 34, 42),
 'jurisdiccion-agraria': (gc(212, 2023), 'la omisión de la lectura del articulado, el bloque del articulado con las proposiciones modificativas al artículo 2', 59, 6),
 'pnd-comision-verdad': (gc(889, 2023), 'proposición eliminando el artículo 8', 50, 31),
 'pnd-concesiones-forestales': (gc(889, 2023), 'proposición de eliminación al artículo 49', 41, 44),
 'transferencias-energia-renovable': (gc(889, 2023), 'proposiciones de eliminación al artículo 207', 59, 21),
 'congresistas-otra-actividad': (gc(19, 2024), 'artículo nuevo presentado por el honorable Senador Carlos Manuel Meisel', 63, 31),
 'gas-vivienda-social': (gc(448, 2024), 'proposición positiva con que termina el Informe de Ponencia del Proyecto de Ley número 231', 46, 21),
}
# Comisión Séptima: el acta transcribe el llamado a lista (no hay listas por el sí y por el no); votos leídos uno por uno
LLAMADO = {
 'reforma-laboral-2025': ('https://apicongresovisible.uniandes.edu.co/uploads/proyecto-ley/13271/290/25,%20607/25,%20608/25,%20613/25.pdf',
   'Acta 31 de la Comisión Séptima del Senado, 18 de marzo de 2025 (Gaceta 613 de 2025): llamado a lista de la ponencia de archivo; sí = archivar',
   ['Agudelo García Ana Paola', 'Andrade Serrano Esperanza', 'Barrera Rodríguez Josué Alirio', 'Bedoya Pérez Sor Berenice', 'Blel Scaff Nadia Georgette', 'Henríquez Pinedo Honorio Miguel', 'Pinto Hernández Miguel Ángel', 'Ríos Cuéllar Beatriz Lorena'],
   ['Arias Castillo Wilson Neber', 'Díaz Plata Edwing Fabián', 'Hurtado Sánchez Norma', 'Peralta Epieyú Martha Isabel', 'Restrepo Correa Ómar de Jesús', 'Silva Idrobo Ferney']),
 'reforma-salud-2024': (gc(940, 2024),
   'Acta 20 de la Comisión Séptima del Senado, 3 de abril de 2024 (Gaceta 940 de 2024): llamado a lista de la proposición de archivo; sí = archivar',
   ['Agudelo García Ana Paola', 'Barrera Rodríguez Josué Alirio', 'Bedoya Pérez Sor Berenice', 'Blel Scaff Nadia Georgette', 'Henríquez Pinedo Honorio Miguel', 'Hurtado Sánchez Norma', 'Marín Lozano José Alfredo', 'Pinto Hernández Miguel Ángel', 'Ríos Cuéllar Beatriz Lorena'],
   ['Arias Castillo Wilson Neber', 'Díaz Plata Edwing Fabián', 'Peralta Epieyú Martha Isabel', 'Restrepo Correa Ómar de Jesús', 'Silva Idrobo Ferney']),
}
# Nombre corto del partido (según el padrón de Congreso Visible), solo para mostrarlo en los resultados
PARTIDO = {'Pacto Histórico Coalición': 'Pacto Histórico', 'Conservador Colombiano': 'Partido Conservador', 'Liberal Colombiano': 'Partido Liberal',
 'Centro Democrático': 'Centro Democrático', 'Cambio Radical': 'Cambio Radical', 'Alianza Verde Centro Esperanza Coalición': 'Alianza Verde - Centro Esperanza',
 'Partido de la U - Partido de la Unión por la Gente': 'Partido de la U', 'Comunes': 'Comunes', 'MIRA - Colombia Justa Libres': 'MIRA - Colombia Justa Libres',
 'Verde-Oxígeno': 'Verde Oxígeno', 'AICO - Autoridades Indígenas de Colombia': 'AICO', 'Liga de gobernantes anticorrupción': 'Liga de Gobernantes Anticorrupción',
 'MAIS - Movimiento Alternativo Indígena y Social': 'MAIS'}

def fetch(url, name):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p) or not os.path.getsize(p):
        subprocess.run(['curl', '-sSfL', '--max-time', '600', '-o', p, url], check=True)
    return p

def padron():
    p = os.path.join(CACHE, 'padron-senado-2022-2026.json')
    if os.path.exists(p): return json.load(open(p))
    out = []
    for page in range(1, 10):
        h = subprocess.run(['curl', '-sSf', '--max-time', '60', f'https://congresovisible.uniandes.edu.co/congresistas/?corporacion=2&cuatrienio=9&page={page}'], capture_output=True, text=True, check=True).stdout
        L = json.loads(re.search(r'__NEXT_DATA__" type="application/json">(.*?)</script>', h).group(1))['props']['pageProps']['ListaInicial']
        if not L: break
        out += L
    json.dump(out, open(p, 'w'), ensure_ascii=False)
    return out

def norm(s):
    s = unicodedata.normalize('NFD', s); s = ''.join(c for c in s if unicodedata.category(c) != 'Mn')
    return re.sub(r'[^a-z ]', ' ', s.lower()).split()

P = padron()
R = [dict(id=x['persona_id'], ap=norm(x['apellidos']), no=norm(re.sub(r"'.*?'", '', x['nombres'])), x=x) for x in P]
for r in R: r['full'] = ' '.join(r['ap'] + r['no'])

def match(line):
    """Senador del padrón cuyo nombre es esta línea del acta («Apellidos Nombres»), o None."""
    t = norm(line)
    if len(t) < 2 or len(t) > 8: return None
    for r in R:
        if sorted(t) == sorted(r['ap'] + r['no']): return r
    s = ' '.join(t); best = None; bs = 0
    for r in R:
        k = len(r['ap'])
        if t[:k] != r['ap'] and difflib.SequenceMatcher(None, ' '.join(t[:k]), ' '.join(r['ap'])).ratio() < 0.85: continue
        sc = difflib.SequenceMatcher(None, s, r['full']).ratio(); rest = t[k:]
        if rest and r['no'] and rest[0] != r['no'][0] and difflib.SequenceMatcher(None, rest[0], r['no'][0]).ratio() < 0.75: sc -= 0.3
        if sc > bs: bs, best = sc, r
    return best if bs >= 0.72 else None

HDR = re.compile(r'^\s*(por\s+el|votos?\s+por\s+el)\s+(s[ií]|no)\b\s*:?\s*$', re.I)
def listas(txt):
    """Listas nominales del acta: [(título de la votación, lado, [ids])] en el orden del texto."""
    L = open(txt).read().split('\n'); out = []; cur = None; title = ''
    for i, l in enumerate(L):
        if re.search(r'votaci[oó]n\s+nominal', l, re.I): title = re.sub(r'\s+', ' ', ' '.join(L[i:i + 5]))
        m = HDR.match(l)
        if m:
            cur = dict(title=title, side='si' if m.group(2).lower().startswith('s') else 'no', ids=[], last=''); out.append(cur); gap = 0; continue
        if cur is None: continue
        r = match(l) if not l.strip().isupper() else None   # las firmas en mayúsculas no son votos
        if r:
            key = ' '.join(norm(l))
            if key < cur['last'] and re.search(r'[.:]\s*$', l): continue   # «Fulano.»: intervención después de la lista
            if r['id'] not in cur['ids']: cur['ids'].append(r['id']); cur['last'] = key
            gap = 0
        else:
            gap += 1
            if gap > 60: cur = None
    return out

Q = {q['id']: q for q in json.load(open(os.path.join(here, 'questions.json')))['questions']}
V = json.load(open(os.path.join(here, 'votos_bancadas.json')))
def si_es(qid):
    """Opción de la pregunta que corresponde al «sí» de la votación (se deduce de las bancadas, como en add_cohesion.py)."""
    q = Q[qid]; po = set()
    for p, pos in q['positions'].items():
        c = V[qid].get(p)
        if not c or c[0] == c[1]: continue
        po.add(pos if c[0] > c[1] else 1 - pos)
    assert len(po) == 1, qid
    return po.pop()

usados = set(); vot = {}
for qid, (url, titulo, nsi, nno) in VOTOS.items():
    pdf = fetch(url, re.sub(r'[^A-Za-z0-9]+', '_', url.split('/', 3)[3])[-80:])
    txt = pdf + '.txt'
    if not os.path.exists(txt): subprocess.run(['pdftotext', '-raw', pdf, txt], check=True)
    B = listas(txt); key = ' '.join(norm(titulo)); hit = None
    for k, b in enumerate(B):
        if b['side'] == 'si' and key in ' '.join(norm(b['title'])):
            no = next((c for c in B[k + 1:k + 3] if c['side'] == 'no'), None)
            if no and len(b['ids']) == nsi and len(no['ids']) == nno: hit = (b, no); break
    if not hit: sys.exit(f'{qid}: no se encontró la votación «{titulo}» con {nsi} sí y {nno} no')
    si, no = hit[0]['ids'], hit[1]['ids']; ambos = sorted(set(si) & set(no))
    vot[qid] = {'acta': url, 'votacion': hit[0]['title'].split(' Honorables')[0].strip(), 'si_es_opcion': si_es(qid),
                'si': sorted(i for i in si if i not in ambos), 'no': sorted(i for i in no if i not in ambos)}
    if ambos: vot[qid]['excluidos'] = ambos; vot[qid]['nota'] = 'Figura en las dos listas del acta: no se cuenta.'
for qid, (url, desc, si, no) in LLAMADO.items():
    ids = lambda names: sorted(match(n)['id'] for n in names)
    vot[qid] = {'acta': url, 'votacion': desc, 'si_es_opcion': si_es(qid), 'si': ids(si), 'no': ids(no)}
for v in vot.values(): usados |= set(v['si']) | set(v['no'])
sen = {str(x['persona_id']): {'nombre': re.sub(r"\s+", ' ', f"{x['nombres']} {x['apellidos']}").strip(), 'partido': PARTIDO.get(x['partido'], x['partido'])}
       for x in P if x['persona_id'] in usados}
out = {'_descripcion': 'Voto de cada senador en las votaciones nominales del Senado usadas por las preguntas, leído en las actas oficiales '
       '(listas «por el sí» y «por el no», o llamado a lista en comisión) y cruzado con el padrón de Congreso Visible (Senado 2022-2026, con reemplazos). '
       'si_es_opcion: índice de la opción de la pregunta que corresponde al «sí». Generado por extraer_senadores.py; no editar a mano.',
       'senadores': dict(sorted(sen.items(), key=lambda kv: ' '.join(norm(kv[1]['nombre'])))), 'votaciones': vot}
json.dump(out, open(os.path.join(here, 'votos_senadores.json'), 'w'), ensure_ascii=False, indent=1)
print(len(vot), 'votaciones,', len(sen), 'senadores')
