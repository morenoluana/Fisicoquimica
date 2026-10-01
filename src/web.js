(function () {
  const UNIDADES = ["Gases reales", "Primera ley", "Termoquímica", "Segunda ley", "Equilibrio", "Cambio de fases", "Mezclas", "Cinética", "Adsorción y dispersos", "Biorreactores"];
  const SECCIONES = ["inicio", "resumen", "formulas", "ejercicios", "preguntas", "simulacros"];

  const leer = (k) => { try { return localStorage.getItem(k) === "1"; } catch (e) { return false; } };
  const guardar = (k, v) => { try { v ? localStorage.setItem(k, "1") : localStorage.removeItem(k); } catch (e) {} };

  // ---- Secciones por hash ----
  function mostrar(hash) {
    const id = (hash || "").replace("#", "");
    let sec = SECCIONES.includes(id) ? id : null;
    let destino = null;
    if (!sec && id) {
      destino = document.getElementById(id);
      const contenedor = destino && destino.closest(".seccion");
      if (contenedor) sec = contenedor.id;
    }
    sec = sec || "inicio";
    SECCIONES.forEach((s) => { document.getElementById(s).hidden = s !== sec; });
    document.querySelectorAll(".nav a").forEach((a) => {
      if (a.getAttribute("href") === "#" + sec) a.setAttribute("aria-current", "page"); else a.removeAttribute("aria-current");
    });
    if (destino) { if (destino.tagName === "DETAILS") destino.open = true; destino.scrollIntoView(); }
    else setTimeout(() => window.scrollTo(0, 0), 0);
    if (sec === "inicio") progreso();
  }
  window.addEventListener("hashchange", () => mostrar(location.hash));

  // ---- Ejercicios: chip de estado + "Lo resolví" ----
  const ETIQUETA = { ok: "coincide", dif: "difiere", nd: "sin dato" };
  document.querySelectorAll(".ej").forEach((ej) => {
    const h = ej.querySelector("h4");
    const cab = document.createElement("div");
    cab.className = "cab";
    h.replaceWith(cab);
    const izq = document.createElement("div");
    izq.style.cssText = "display:flex;gap:10px;align-items:baseline;flex-wrap:wrap;min-width:0";
    const chip = document.createElement("span");
    chip.className = "chip " + ej.dataset.estado;
    chip.textContent = ETIQUETA[ej.dataset.estado];
    izq.append(h, chip);
    const lbl = document.createElement("label");
    lbl.className = "hecho";
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.id = "hecho-" + ej.id;
    cb.checked = leer("fq-ej-" + ej.id);
    cb.addEventListener("change", () => { guardar("fq-ej-" + ej.id, cb.checked); aplicarFiltro(); });
    lbl.append(cb, document.createTextNode("Lo resolví"));
    cab.append(izq, lbl);
  });

  // ---- Preguntas: "La sé" ----
  document.querySelectorAll(".pr").forEach((pr) => {
    const pie = document.createElement("div");
    pie.className = "pie";
    const lbl = document.createElement("label");
    lbl.className = "hecho";
    const cb = document.createElement("input");
    cb.type = "checkbox"; cb.id = "se-" + pr.id;
    cb.checked = leer("fq-pr-" + pr.id);
    cb.addEventListener("change", () => guardar("fq-pr-" + pr.id, cb.checked));
    lbl.append(cb, document.createTextNode("La sé"));
    pie.append(lbl);
    pr.append(pie);
  });

  // ---- Filtros de ejercicios ----
  let filtro = "todos";
  function aplicarFiltro() {
    document.querySelectorAll(".filtros button").forEach((b) => b.setAttribute("aria-pressed", String(b.dataset.f === filtro)));
    document.querySelectorAll(".ej").forEach((ej) => {
      const hecho = ej.querySelector(".hecho input").checked;
      ej.hidden = (filtro === "dif" && ej.dataset.estado !== "dif") || (filtro === "pendientes" && hecho);
    });
    document.querySelectorAll(".unidad-ej").forEach((u) => {
      const tiene = u.querySelector(".ej");
      u.hidden = filtro !== "todos" && (!tiene || !u.querySelector(".ej:not([hidden])"));
    });
  }
  document.querySelectorAll(".filtros button").forEach((b) => b.addEventListener("click", () => { filtro = b.dataset.f; aplicarFiltro(); }));
  document.querySelectorAll("[data-filtro]").forEach((a) => a.addEventListener("click", () => { filtro = a.dataset.filtro; aplicarFiltro(); }));

  document.getElementById("n-dif").textContent = document.querySelectorAll('.ej[data-estado="dif"]').length + " ejercicios";

  // ---- Tabla de avance ----
  function progreso() {
    const tb = document.querySelector("#progreso tbody");
    tb.innerHTML = "";
    UNIDADES.forEach((nombre, i) => {
      const u = String(i + 1);
      const ejs = [...document.querySelectorAll('.unidad-ej[data-u="' + u + '"] .ej')];
      const prs = [...document.querySelectorAll('.unidad-pr[data-u="' + u + '"] .pr')];
      const ejOk = ejs.filter((e) => e.querySelector(".hecho input").checked).length;
      const prOk = prs.filter((p) => p.querySelector(".hecho input").checked).length;
      const total = ejs.length + prs.length;
      const pct = total ? Math.round(100 * (ejOk + prOk) / total) : 0;
      const tr = document.createElement("tr");
      tr.innerHTML =
        '<td><a href="#u' + u + '">' + u + ". " + nombre + "</a></td>" +
        "<td>" + (ejs.length ? ejOk + "/" + ejs.length : "—") + "</td>" +
        "<td>" + (prs.length ? prOk + "/" + prs.length : "—") + "</td>" +
        '<td><div class="barra" title="' + pct + ' %"><i style="width:' + pct + '%"></i></div></td>';
      tb.append(tr);
    });
  }

  aplicarFiltro();
  mostrar(location.hash);
})();
