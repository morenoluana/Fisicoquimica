// Genera los PDF A4 para imprimir: hoja-de-formulas.pdf y resumen.pdf.
// Uso: node scripts/build.mjs && node scripts/pdf.mjs
import { createRequire } from "node:module";
import { execSync } from "node:child_process";
import { existsSync } from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";

const globalRoot = execSync("npm root -g").toString().trim();
const { chromium } = createRequire(path.join(globalRoot, "noop.js"))("playwright");
const raiz = path.resolve(path.dirname(new URL(import.meta.url).pathname), "..");

const exe = process.env.CHROMIUM_PATH || (existsSync("/opt/pw-browsers/chromium") ? "/opt/pw-browsers/chromium" : undefined);
const browser = await chromium.launch(exe ? { executablePath: exe } : {});
for (const nombre of ["hoja-de-formulas", "resumen", "modelos-de-examen"]) {
  const page = await browser.newPage();
  await page.goto(pathToFileURL(path.join(raiz, nombre + ".html")).href, { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);
  await page.emulateMedia({ media: "print" });
  await page.pdf({ path: path.join(raiz, nombre + ".pdf"), format: "A4", printBackground: true, preferCSSPageSize: true });
  console.log("PDF:", nombre + ".pdf");
  await page.close();
}
await browser.close();
