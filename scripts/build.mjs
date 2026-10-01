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

// Gráficos generados por scripts/figuras.py, insertados donde dice <!-- figura: nombre -->
const conFiguras = (html) => html.replace(/<!-- figura: ([\w-]+) -->/g, (_, f) => leer(`src/figuras/${f}.html`));
const resumen = conFiguras(mate(leer("src/resumen.html")));
const formulas = mate(leer("src/formulas.html"));
const ejercicios = mate(leer("src/ejercicios.html"));
const preguntas = mate(leer("src/preguntas.html"));
const simulacros = mate(leer("src/simulacros.html"));

const titulos = [...leer("src/resumen.html").matchAll(/<section class="unidad" id="u(\d+)">\s*<h2><span class="num">\d+<\/span> ([^<]+)<\/h2>/g)];
const chips = titulos.map(([, n, t]) => `<li data-u="${n}"><a href="#u${n}"><b>${n}</b>${t}</a></li>`).join("");
const indiceRes = titulos.map(([, n, t]) => `<li data-u="${n}"><a href="#u${n}"><b>${n}</b>${t}</a></li>`).join("");
const indiceEj = [...leer("src/ejercicios.html").matchAll(/<section class="unidad-ej" id="(ej\d+)" data-u="\d+">\s*<h2><span class="num">(\d+)<\/span> ([^<]+)<\/h2>/g)]
  .map(([, id, n, t]) => `<li data-u="${n}"><a href="#${id}"><b>${n}</b>${t}</a></li>`).join("");

const llenar = (plantilla, datos) => plantilla.replace(/\{\{(\w+)\}\}/g, (_, k) => datos[k] ?? "");
const cssBase = fuentes + katexCss + leer("assets/estilo.css");

const web = llenar(leer("src/web.html"), {
  CSS: cssBase, JS: leer("src/web.js"), RESUMEN: resumen, FORMULAS: formulas, EJERCICIOS: ejercicios, PREGUNTAS: preguntas, SIMULACROS: simulacros,
  INDICE_RESUMEN: indiceRes, CHIPS: chips, INDICE_EJ: indiceEj,
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

// ---------- Modelos de examen (PDF): consignas + resoluciones ----------
// Respuesta de cada ejercicio/pregunta por id, para completar las que solo remiten a otro ("igual al ...").
const respuestas = {};
for (const html of [ejercicios, simulacros]) {
  for (const [, id, cuerpo] of html.matchAll(/<article class="ej" id="([\w-]+)"[^>]*>([\s\S]*?)<\/article>/g)) {
    const rta = (cuerpo.match(/<p class="rta">[\s\S]*?<\/p>/) || [""])[0];
    const det = (cuerpo.match(/<details[^>]*>([\s\S]*?)<\/details>/) || ["", ""])[1].replace(/<summary>[\s\S]*?<\/summary>/, "");
    respuestas[id] = { rta, det, tieneDet: !!det };
  }
}
for (const [, id, cuerpo] of preguntas.matchAll(/<details class="pr" id="([\w-]+)">([\s\S]*?)<\/details>/g)) {
  respuestas[id] = { rta: "", det: cuerpo.replace(/<summary>[\s\S]*?<\/summary>/, ""), tieneDet: true };
}
const completar = (articulo) => {
  if (/<details/.test(articulo)) return articulo.replace(/<details(?![^>]*open)/g, "<details open");
  const refs = [...articulo.matchAll(/href="#([\w-]+)"/g)].map((m) => respuestas[m[1]]).filter(Boolean);
  const extra = refs.map((r) => `<div class="ref">${r.tieneDet ? r.det : r.rta}</div>`).join("");
  return articulo.replace(/<\/article>$/, extra + "</article>");
};
const tipoDe = (t) => /previo/i.test(t) ? "previo" : /Final/.test(t) ? "final" : /Parcial|Recuperatorio/.test(t) ? "parcial" : "otro";
const enunciadosSrc = leer("src/modelos-enunciados.html");
const modelos = [...enunciadosSrc.matchAll(/<section class="modelo" data-res="([\w-]+)" data-n="(\d+)">\s*<header><span class="tipo">([^<]+)<\/span><h2>([^<]+)<\/h2><\/header>([\s\S]*?)<\/section>/g)];
const cabecera = (n, tipo, titulo) => `<header><span class="n">${n}</span><h2>${titulo}</h2><span class="tipo">${tipo}</span></header>`;
const enunciadosHtml = modelos.map(([, res, n, tipo, titulo, cuerpo]) =>
  `<section class="modelo" data-tipo="${tipoDe(tipo)}">${cabecera(n, tipo, titulo)}${cuerpo}</section>`).join("\n");
const resolucionesHtml = modelos.map(([, res, n, tipo, titulo]) => {
  const sec = simulacros.match(new RegExp(`<section class="examen" id="${res}">([\\s\\S]*?)<\\/section>`));
  if (!sec) throw new Error("Falta la resolución de " + res);
  const cuerpo = sec[1].replace(/^\s*<h3>[\s\S]*?<\/h3>/, "")
    .replace(/<article class="ej"[\s\S]*?<\/article>/g, completar);
  return `<section class="modelo resolucion" data-tipo="${tipoDe(tipo)}">${cabecera(n, tipo, "Resolución · " + titulo)}${cuerpo}</section>`;
}).join("\n");
const indiceModelos = modelos.map(([, , n, tipo, titulo]) => `<tr><td>${n}</td><td>${titulo}</td><td>${tipo}</td></tr>`).join("");
writeFileSync(path.join(raiz, "modelos-de-examen.html"), llenar(leer("src/modelos.html"), {
  CSS: cssImp, N: String(modelos.length), INDICE: indiceModelos, ENUNCIADOS: mate(enunciadosHtml), RESOLUCIONES: resolucionesHtml,
}));
console.log("OK: index.html, hoja-de-formulas.html, resumen.html, modelos-de-examen.html");
