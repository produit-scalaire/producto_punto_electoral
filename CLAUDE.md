# Reglas para este repositorio

- No agregar nunca una línea `Co-Authored-By` ni ninguna mención de atribución a Claude (Claude-Session, "Generated with Claude Code", etc.) en los mensajes de commit, los PR o los archivos.
- Los cambios se suben directamente a `main` (GitHub Pages sirve la raíz de `main`).
- Es una adaptación a Colombia del [Produit scalaire électoral](https://github.com/produit-scalaire/produit-scalaire-electoral). Se comparan las bancadas del Congreso 2022-2026.
- La dirección del repositorio que muestra la página es la constante `REPO_URL` de `source/build.py`.
- La página publicada es `index.html`, generada desde `source/` con `python3 source/build.py`, que también genera `catalogo-preguntas.html` y copia las dos páginas a la raíz.
- Cohesión de las bancadas: `source/votos_bancadas.json` ([a favor, en contra, abstención] por bancada, según la votación nominal); `python3 source/add_cohesion.py` escribe el campo `split` en `questions.json`, y hay que correrlo antes de `build.py` cuando se agrega una votación.
- Cada pregunta se basa en una votación o decisión real con fuente verificable. Nada de posiciones inventadas: si no se conoce la posición de una bancada, se deja vacía.
- Antes de cada push, revisar en celular: capturas con Playwright emulando un iPhone 13 (390 px) y una pantalla de 360 px, en tema claro y oscuro (`colorScheme`), de cada pestaña, de los 6 pasos de la animación (incluida la línea en el paso 2 y la leyenda en los pasos 5 y 6), de la pantalla de inicio, de una pregunta y de los resultados. Corregir cualquier superposición antes de subir. La página sigue el tema del dispositivo (claro u oscuro): no forzar ninguno de los dos.
- Vista previa de los enlaces compartidos: etiquetas Open Graph generadas por `build.py` (constantes `PAGE_URL`, `DESC`), imagen `preview.png` (1200×630) en la raíz, capturada desde `source/vista-previa.html`.
- Enlace para compartir (og:url y botón «Compartir el cuestionario»): constante `SHARE_URL` en `source/build.py`; aumentar `?v=` para que las aplicaciones refresquen la vista previa.
