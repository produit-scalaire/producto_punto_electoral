# Arma la página única, que funciona sin conexión, a partir de template.html + questions.json + disclaimer.md + animation-axes.html.
import json,re,html,os
here=os.path.dirname(os.path.abspath(__file__))
t=open(os.path.join(here,'template.html')).read()
d=json.load(open(os.path.join(here,'questions.json')))
data=json.dumps(d,ensure_ascii=False).replace('</','<\\/')

def inline(s):
    s=html.escape(s,quote=False)
    s=re.sub(r'\[([^\]]+)\]\((https?://[^)\s]+)\)',r'<a href="\2" target="_blank" rel="noopener">\1</a>',s)
    return re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',s)
def md(src):
    out=[];ul=False
    for line in src.splitlines():
        if line.startswith('- '):
            if not ul: out.append('<ul>');ul=True
            out.append('<li>'+inline(line[2:])+'</li>');continue
        if ul: out.append('</ul>');ul=False
        if line.startswith('## '): out.append('<h2>'+inline(line[3:])+'</h2>')
        elif line.startswith('# '): out.append('<h1>'+inline(line[2:])+'</h1>')
        elif line.strip(): out.append('<p>'+inline(line)+'</p>')
    if ul: out.append('</ul>')
    return '\n'.join(out)
# DIRECCIÓN DEL REPOSITORIO PÚBLICO: cambiarla solo aquí (texto «Método» y pie de página)
REPO_URL='https://github.com/produit-scalaire/producto_punto_electoral'
FORM_URL=''  # formulario de comentarios (Google Forms); vacío mientras no exista
PAGE_URL='https://produit-scalaire.github.io/producto_punto_electoral/'
# Enlace para compartir: cambiar el número de versión para que las aplicaciones recarguen la vista previa
SHARE_URL=PAGE_URL+'?v=1'
# Vista previa del enlace (WhatsApp, iMessage, redes): imagen preview.png en la raíz del sitio, generada desde vista-previa.html
DESC="Responda a las votaciones reales del Congreso y mida su cercanía con cada partido, tema por tema."
FAV="data:image/svg+xml,"+__import__('urllib.parse').parse.quote('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 30 30"><rect width="30" height="30" rx="6" fill="#0f1633"/><path d="M5 25 L25 21" stroke="#8ea2ff" stroke-width="3" stroke-linecap="round"/><path d="M5 25 L19 6" stroke="#fff" stroke-width="3" stroke-linecap="round"/></svg>')
META=f'''<meta name="description" content="{html.escape(DESC)}">
<link rel="icon" href="{FAV}">
<meta property="og:type" content="website"><meta property="og:locale" content="es_CO">
<meta property="og:site_name" content="Producto punto electoral">
<meta property="og:title" content="¿Qué partido vota de verdad como usted?">
<meta property="og:description" content="{html.escape(DESC)}">
<meta property="og:url" content="{SHARE_URL}">
<meta property="og:image" content="{PAGE_URL}preview.png"><meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">
<meta property="og:image:alt" content="El hemiciclo de la Cámara de Representantes y la pregunta: ¿qué partido vota de verdad como usted?">
<meta name="twitter:card" content="summary_large_image"><meta name="twitter:title" content="¿Qué partido vota de verdad como usted?">
<meta name="twitter:description" content="{html.escape(DESC)}"><meta name="twitter:image" content="{PAGE_URL}preview.png">
'''
about=md(open(os.path.join(here,'disclaimer.md')).read().replace('__REPO__',REPO_URL).replace('__PAGE__',PAGE_URL).replace('__FORM__',FORM_URL))
# subpestañas: una sección por título de nivel 2
SHORT={'Nuestra intención':'Intención','Nuestro método':'Método','Los límites que hay que tener en cuenta':'Límites','Recolección de datos: ninguna':'Datos','Agradecimientos':'Gracias'}
parts=re.split(r'(?=<h2>)',about)
head,secs=parts[0],parts[1:]
if secs:
    btns=[];panels=[]
    for i,sec in enumerate(secs):
        h2t=re.match(r'<h2>(.*?)</h2>',sec).group(1);lab=SHORT.get(html.unescape(re.sub('<[^>]+>','',h2t)),h2t)
        btns.append(f'<button role="tab" data-sub="{i}" aria-selected="{"true" if i==0 else "false"}">{lab}</button>')
        panels.append(f'<div class="subpanel" data-subpanel="{i}"{"" if i==0 else " hidden"}>{sec}</div>')
    about=head+'<nav class="tabs subtabs" role="tablist" aria-label="Subsecciones">'+''.join(btns)+'</nav>'+''.join(panels)

a=open(os.path.join(here,'animation-axes.html')).read().replace('__NQ__',str(len(d['questions'])))
a=re.sub(r'<link[^>]*fonts\.(googleapis|gstatic)[^>]*>\s*','',a)
a=re.sub(r'--display:[^;]*;','--display:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;',a)
a=re.sub(r'--body:[^;]*;','--body:ui-sans-serif,system-ui,-apple-system,"Segoe UI",Roboto,Arial,sans-serif;',a)
a=re.sub(r'--mono:[^;]*;','--mono:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;',a)
a=re.sub(r'<meta name="claude:viewport-fit-sides"[^>]*>','',a)
assert 'googleapis' not in a and 'http' not in re.sub(r'href="https?://[^"]*"','',a).split('<script>')[0], 'external resource left in animation'
a=a+'<style>@media (max-width:620px){body{padding-left:8px!important;padding-right:8px!important}figure{padding:4px!important}svg .lab{font-size:21px}svg .lab.pour{font-size:21px}svg .plabel{font-size:22px}svg .cap{font-size:17px}svg .big{font-size:44px}}</style>'
a='<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><base target="_blank"></head><body style="margin:0">'+a+'</body></html>'
anim=a.replace('&','&amp;').replace('"','&quot;')

dl_top='<a class="dl" href="" download="producto-punto-electoral.html" onclick="this.href=location.href.split(\'#\')[0]">Descargar la página</a>'
dl2='<p class="label"><a href="" download="producto-punto-electoral.html" onclick="this.href=location.href.split(\'#\')[0]">Descargue la página</a> para usarla sin conexión.</p>'
if not FORM_URL: t=re.sub(r'<span>¿Una pregunta, una sugerencia.*?</span>(?=</footer>)','',t)
base=t.replace('__SHARE__',SHARE_URL).replace('__FORM__',FORM_URL).replace('__REPO__',REPO_URL).replace('__DATA__',data).replace('__ABOUT__',about).replace('__ANIM__',anim)
std=base.replace('__DOWNLOAD_TOP__',dl_top).replace('__DOWNLOAD2__',dl2)
art=base.replace('__DOWNLOAD_TOP__','').replace('__DOWNLOAD2__','')
open(os.path.join(here,'producto-punto-electoral.html'),'w').write('<!doctype html>\n<html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'+META+std.replace('<div class="shell"','</head><body>\n<div class="shell"',1)+'\n</body></html>\n')
open(os.path.join(here,'artifact.html'),'w').write(art)
print('ok',len(d['questions']),'preguntas')

# Regenera también el catálogo legible de las preguntas
import subprocess,sys
subprocess.run([sys.executable,os.path.join(here,'build_catalogue.py')],check=True)

# Copia las páginas publicadas a la raíz del repositorio (GitHub Pages sirve la raíz de main)
import shutil
root=os.path.dirname(here)
shutil.copy(os.path.join(here,'producto-punto-electoral.html'),os.path.join(root,'index.html'))
shutil.copy(os.path.join(here,'catalogo-preguntas.html'),os.path.join(root,'catalogo-preguntas.html'))
print('index.html y catalogo-preguntas.html copiados a la raíz')
