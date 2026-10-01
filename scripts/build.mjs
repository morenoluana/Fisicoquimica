// Arma la web y las versiones para imprimir a partir de src/.
// Uso: node scripts/build.mjs   (después: node scripts/pdf.mjs para los PDF)
// Las fórmulas ($...$ y $$...$$) se renderizan con KaTeX acá, así las páginas no necesitan JS ni internet.
import { createRequire } from "node:module";
import { readFileSync, writeFileSync } from "node:fs";
import path from "node:path";

const raiz = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");
const leer = (p) => readFileSync(path.join(raiz, p), "utf8");
const katex = createRequire(import.meta.url)("./katex.min.js");

const desescapar = (s) => s.replace(/&lt;/g, "<").replace(/&gt;/g, ">").replace(/&amp;/g, "&");
function mate(html) {
  const render = (tex, display) => katex.renderToString(desescapar(tex), { displayMode: display, throwOnError: true, strict: false, output: "html" });
  return html
    .replace(/\$\$([\s\S]+?)\$\$/g, (_, t) => render(t, true))
    .replace(/\$([^$]+?)\$/g, (_, t) => render(t, false));
}

// Fuentes embebidas como data: URI (la página funciona sola, offline y como Artifact)
const b64 = (p) => "data:font/woff2;base64," + readFileSync(path.join(raiz, p)).toString("base64");
const fuentes = leer("assets/fuentes/fuentes.css").replace(/url\(([^)]+\.woff2)\)/g, (_, f) => `url(${b64("assets/fuentes/" + f)})`);
const katexCss = leer("assets/katex/katex.min.css").replace(
  /src:url\(fonts\/([^)]+?)\.woff2\) format\("woff2"\)[^;}]*/g,
  (_, f) => `src:url(${b64("assets/katex/fonts/" + f + ".woff2")}) format("woff2")`
);

const resumen = mate(leer("src/resumen.html"));
const formulas = mate(leer("src/formulas.html"));
const ejercicios = mate(leer("src/ejercicios.html"));
const preguntas = mate(leer("src/preguntas.html"));
const simulacros = mate(leer("src/simulacros.html"));

const titulos = [...leer("src/resumen.html").matchAll(/<section class="unidad" id="u(\d+)">\s*<h2><span class="num">\d+<\/span> ([^<]+)<\/h2>/g)];
const indiceRes = titulos.map(([, n, t]) => `<li><a href="#u${n}"><b>${n}</b>${t}</a></li>`).join("");
const indiceEj = [...leer("src/ejercicios.html").matchAll(/<section class="unidad-ej" id="(ej\d+)" data-u="\d+">\s*<h2><span class="num">(\d+)<\/span> ([^<]+)<\/h2>/g)]
  .map(([, id, n, t]) => `<li><a href="#${id}"><b>${n}</b>${t}</a></li>`).join("");

const llenar = (plantilla, datos) => plantilla.replace(/\{\{(\w+)\}\}/g, (_, k) => datos[k] ?? "");
const cssBase = fuentes + katexCss + leer("assets/estilo.css");

const web = llenar(leer("src/web.html"), {
  CSS: cssBase, JS: leer("src/web.js"), RESUMEN: resumen, FORMULAS: formulas, EJERCICIOS: ejercicios, PREGUNTAS: preguntas, SIMULACROS: simulacros,
  INDICE_RESUMEN: indiceRes, INDICE_EJ: indiceEj,
});
// index.html: documento completo para abrir en el navegador o GitHub Pages
const fin = web.indexOf("</style>") + "</style>".length; // título + estilos van al <head>
writeFileSync(path.join(raiz, "index.html"),
  '<!doctype html>\n<html lang="es">\n<head>\n<meta charset="utf-8">\n' +
  '<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n' +
  web.slice(0, fin) + "\n</head>\n<body>" + web.slice(fin) + "</body>\n</html>\n");
// Fragmento sin <html>/<head> para publicarlo como Artifact (el servicio agrega el esqueleto)
if (process.env.ARTIFACT) writeFileSync(process.env.ARTIFACT, web);
const cssImp = cssBase + leer("assets/imprimir.css");
writeFileSync(path.join(raiz, "hoja-de-formulas.html"), llenar(leer("src/hoja.html"), { CSS: cssImp, FORMULAS: formulas }));
writeFileSync(path.join(raiz, "resumen.html"), llenar(leer("src/resumen-imprimir.html"), { CSS: cssImp, RESUMEN: resumen }));
console.log("OK: index.html, hoja-de-formulas.html, resumen.html");
