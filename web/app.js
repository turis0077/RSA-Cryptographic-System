// Interfaz web del sistema RSA. Toda la lógica matemática se ejecuta en Python (Pyodide).
"use strict";

const $ = (sel, raiz = document) => raiz.querySelector(sel);
const dormir = (ms) => new Promise((r) => setTimeout(r, ms));
const fmt = (plantilla, datos) => plantilla.replace(/\{(\w+)\}/g, (_, k) => datos[k]);

let api = null;            // módulo Python app_web
let T = null;              // textos
const estado = { alice: false, bob: false };
const visto = { Alice: false, Bob: false };
const manual = { enc: false, des: false };
let ocupado = false;
let ultimoEmisor = null;
let ultimoReceptor = null;

const puedeVerEmisor = (u) => (u === "Alice" ? estado.alice : estado.bob);
const puedeVerReceptor = puedeVerEmisor;
const otro = (u) => (u === "Alice" ? "Bob" : "Alice");
const llamar = (fn, ...args) => JSON.parse(api[fn](...args));

// ---------------------------------------------------------------- arranque de Python
async function iniciarPython() {
  const py = await loadPyodide();
  const manifiesto = await (await fetch("py/manifest.json")).json();
  for (const ruta of manifiesto) {
    const texto = await (await fetch("py/" + ruta)).text();
    const dir = ruta.includes("/") ? ruta.slice(0, ruta.lastIndexOf("/")) : "";
    if (dir) py.FS.mkdirTree("/home/pyodide/" + dir);
    py.FS.writeFile("/home/pyodide/" + ruta, texto);
  }
  py.runPython("import sys\nif '/home/pyodide' not in sys.path: sys.path.insert(0, '/home/pyodide')");
  api = py.pyimport("app_web");
  return JSON.parse(api.iniciar());
}

// ---------------------------------------------------------------- teléfonos
function crearTelefono(nombre) {
  const contacto = otro(nombre);
  const col = $("#col-" + nombre);
  col.innerHTML = `
    <div class="telefono" id="tel-${nombre}">
      <h3>Teléfono de ${nombre} — @${contacto}</h3>
      <div class="historial"></div>
      <div class="tel-error"></div>
      <div class="tel-entrada">
        <input type="text" autocomplete="off" spellcheck="false" aria-label="Mensaje de ${nombre}">
        <button type="button" aria-label="Enviar">&gt;</button>
      </div>
    </div>
    <div class="privado" id="priv-${nombre}"><h4>Datos internos de ${nombre}</h4><pre></pre></div>`;
  const entrada = $("input", col);
  const enviarEsto = () => enviar(nombre);
  $("button", col).addEventListener("click", enviarEsto);
  entrada.addEventListener("keydown", (e) => { if (e.key === "Enter") { e.preventDefault(); enviarEsto(); } });
}
const telefono = (n) => $("#tel-" + n);
function burbuja(nombre, texto, propia) {
  const h = $(".historial", telefono(nombre));
  const b = document.createElement("div");
  b.className = "burbuja " + (propia ? "propia" : "ajena");
  b.textContent = texto;               // texto tal cual, sin recortar
  h.appendChild(b);
  h.scrollTop = h.scrollHeight;
}
const telError = (n, msg) => { $(".tel-error", telefono(n)).textContent = msg; };
function bloquearTelefonos(bloqueado) {
  for (const n of ["Alice", "Bob"]) {
    $("input", telefono(n)).disabled = bloqueado;
    $("button", telefono(n)).disabled = bloqueado;
  }
}

// ---------------------------------------------------------------- canal
const canal = {
  texto(t) { $("#canal-texto").textContent = t; },
  llave(e, n) { $("#canal-llave").textContent = `Llave pública (e, n) = (${e}, ${n})`; },
  async pasos(lista) { for (const t of lista) { this.texto(t); await dormir(600); } },
  async sobre(textoCifrado, hacia) {
    const caja = $("#canal-sobre");
    caja.textContent = textoCifrado.length <= 22 ? textoCifrado : textoCifrado.slice(0, 21) + "…";
    const [ini, fin] = hacia === "Bob" ? [22, 78] : [78, 22];
    caja.hidden = false;
    const dur = 800, t0 = performance.now();
    await new Promise((res) => {
      const paso = (ahora) => {
        const f = Math.min((ahora - t0) / dur, 1);
        caja.style.left = ini + (fin - ini) * f + "%";
        f < 1 ? requestAnimationFrame(paso) : res();
      };
      requestAnimationFrame(paso);
    });
    caja.hidden = true;
  },
};
const status = (t) => { $("#status").textContent = t; };

// ---------------------------------------------------------------- detalle
function dibujarDetalle(tipo, r) {
  const cont = $(`#tabs-detalle [data-panel="${tipo}"]`);
  cont.textContent = "";
  const add = (clase, texto) => {
    const d = document.createElement("div");
    d.className = clase; d.textContent = texto; cont.appendChild(d); return d;
  };
  if (r.params) add("params", r.params);
  if (r.aviso) add("aviso", r.aviso);
  if (r.columnas.length) {
    const caja = document.createElement("div");
    caja.className = "tabla-caja";
    const tabla = document.createElement("table");
    const cab = tabla.createTHead().insertRow();
    for (const c of r.columnas) { const th = document.createElement("th"); th.textContent = c; cab.appendChild(th); }
    const cuerpo = tabla.createTBody();
    for (const fila of r.filas) {
      const tr = cuerpo.insertRow();
      for (const celda of fila) tr.insertCell().textContent = celda;   // siempre cadenas (ceros iniciales)
    }
    caja.appendChild(tabla); cont.appendChild(caja);
  }
  if (r.log.length) {
    const log = add("log", "");
    for (const [texto, tag] of r.log) {
      const s = document.createElement("div");
      s.className = tag; s.textContent = texto; log.appendChild(s);
    }
  }
}
const renderDetalle = (tipo, proceso, privado) => dibujarDetalle(tipo, llamar("render", tipo, proceso, privado));
function mostrarTab(grupo, tab) {
  const raiz = $("#tabs-" + grupo);
  raiz.querySelectorAll(".tabs-botones button").forEach((b) => b.classList.toggle("activo", b.dataset.tab === tab));
  raiz.querySelectorAll(".tab-panel").forEach((p) => { p.hidden = p.dataset.panel !== tab; });
}

// ---------------------------------------------------------------- modos
function refrescarPrivados() {
  for (const n of ["Alice", "Bob"]) {
    const visible = n === "Alice" ? estado.alice : estado.bob;
    const filas = llamar("privado_usuario", n, visible);
    $("pre", $("#priv-" + n)).textContent = filas.map(([k, v]) => `${k} = ${v}`).join("\n");
  }
}
function aplicarModos() {
  refrescarPrivados();
  if (manual.enc) renderDetalle("enc", true, true);
  else if (ultimoEmisor) renderDetalle("enc", puedeVerEmisor(ultimoEmisor), puedeVerReceptor(ultimoReceptor));
  else renderDetalle("enc", false, false);
  if (manual.des) renderDetalle("des", true, true);
  else if (ultimoReceptor) { const v = puedeVerReceptor(ultimoReceptor); renderDetalle("des", v, v); }
  else renderDetalle("des", false, false);
}
function pintarBarra() {
  $("#btn-alice").classList.toggle("activo", estado.alice);
  $("#btn-bob").classList.toggle("activo", estado.bob);
  $("#btn-real").classList.toggle("activo", !estado.alice && !estado.bob);
}
function ventanaExplicativa(quien) {
  const modal = $("#modal"), texto = $("#modal-texto"), boton = $("#modal-boton");
  texto.textContent = quien === "Alice" ? T.popup_alice : T.popup_bob;
  boton.textContent = "Siguiente →";
  modal.hidden = false;
  boton.onclick = () => {
    if (boton.textContent.startsWith("Siguiente")) {
      texto.textContent = T.popup_explicacion; boton.textContent = "Entendido";
    } else { modal.hidden = true; }
  };
  boton.focus();
}
function alternar(quien) {
  estado[quien.toLowerCase()] = !estado[quien.toLowerCase()];
  if (estado[quien.toLowerCase()] && !visto[quien]) { visto[quien] = true; ventanaExplicativa(quien); }
  pintarBarra(); aplicarModos();
}
function modoReal() { estado.alice = false; estado.bob = false; pintarBarra(); aplicarModos(); }

// ---------------------------------------------------------------- chat
async function enviar(origen) {
  if (ocupado) return;
  const entrada = $("input", telefono(origen));
  const texto = entrada.value;                 // sin trim
  telError(origen, "");
  const r = llamar("enviar", origen, texto);
  if (!r.ok) {
    telError(origen, r.error.mensaje);
    manual.enc = false;
    renderDetalle("enc", true, false);
    mostrarTab("detalle", "enc");
    status(fmt(T.status.error, { mensaje: r.error.mensaje }));
    return;
  }
  ocupado = true;
  bloquearTelefonos(true);
  try {
    const destino = r.destino;
    ultimoEmisor = origen; ultimoReceptor = destino;
    burbuja(origen, texto, true);
    entrada.value = "";
    manual.enc = false;
    renderDetalle("enc", puedeVerEmisor(origen), puedeVerReceptor(destino));
    mostrarTab("detalle", "enc");
    const f = { origen, destino, e: r.e, n: r.n };
    status(fmt(T.status.llave, f));
    await canal.pasos([fmt(T.status.llave, f), fmt(T.status.llave_ok, f)]);
    canal.llave(r.e, r.n);
    status(fmt(T.status.cifrando, f));
    await dormir(400);
    status(T.status.sobre);
    await canal.sobre(r.C, destino);
    await alLlegar(origen, destino);
  } finally {
    ocupado = false;
    bloquearTelefonos(false);
  }
}
async function alLlegar(origen, destino) {
  const r = llamar("llegar");
  limpiarErrores("des");
  limpiarSalidas("des");
  $("#des-C").value = r.C;                      // autocompleta C y L (siguen editables)
  $("#des-L").value = String(r.L);
  status(fmt(T.status.descifrando, { destino }));
  manual.des = false;
  if (!r.ok) {
    telError(destino, r.error.mensaje);
    renderDetalle("des", true, puedeVerReceptor(destino));
    status(fmt(T.status.error, { mensaje: r.error.mensaje }));
    return;
  }
  burbuja(destino, r.M, false);
  const v = puedeVerReceptor(destino);
  renderDetalle("des", v, v);
  status(fmt(T.status.entregado, { destino }));
}

// ---------------------------------------------------------------- formularios manuales
const val = (id) => document.getElementById(id).value;     // sin modificar
function limpiarErrores(form) {
  document.querySelectorAll(`#c-${form}-M, #c-${form}-C, #c-${form}-L, #c-${form}-p, #c-${form}-q, #c-${form}-e`)
    .forEach((c) => { c.classList.remove("error"); $(".ayuda", c).textContent = ""; });
  const m = document.getElementById(form + "-msg"); if (m) m.textContent = "";
}
function mostrarError(form, err) {
  limpiarErrores(form);
  document.getElementById(form + "-msg").textContent = err.mensaje;
  for (const campo of err.campos) {
    const c = document.getElementById(`c-${form}-${campo}`);
    if (c) { c.classList.add("error"); $(".ayuda", c).textContent = err.mensaje; }
  }
}
function limpiarSalidas(form) {
  document.querySelectorAll(`[id^="${form}-out-"]`).forEach((i) => { i.value = ""; });
}
function encriptarManual() {
  limpiarErrores("enc");
  manual.enc = true;
  const r = llamar("encriptar_manual", val("enc-M"), val("enc-p"), val("enc-q"), val("enc-e"));
  if (r.ok) {
    $("#enc-out-C").value = r.C; $("#enc-out-L").value = String(r.L); $("#enc-out-llave").value = r.llave;
  } else { limpiarSalidas("enc"); mostrarError("enc", r.error); }
  renderDetalle("enc", true, true);
  mostrarTab("detalle", "enc");
}
function desencriptarManual() {
  limpiarErrores("des");
  manual.des = true;
  const r = llamar("desencriptar_manual", val("des-C"), val("des-L"), val("des-p"), val("des-q"), val("des-e"));
  if (r.ok) {
    $("#des-out-d").value = String(r.d); $("#des-out-M").value = r.M; $("#des-out-Mq").value = `"${r.M}"`;
  } else { limpiarSalidas("des"); mostrarError("des", r.error); }
  renderDetalle("des", true, true);
  mostrarTab("detalle", "des");
}
function actualizarLlaves() {
  limpiarErrores("llaves");
  $("#llaves-ok").textContent = "";
  const r = llamar("actualizar_llaves", val("llaves-usuario"), val("llaves-p"), val("llaves-q"), val("llaves-e"));
  if (!r.ok) { mostrarError("llaves", r.error); return; }
  $("#llaves-ok").textContent = r.mensaje;
  refrescarPrivados();
}

// ---------------------------------------------------------------- arranque
async function main() {
  try {
    const datos = await iniciarPython();
    T = datos.textos;
    document.title = T.titulo;
    crearTelefono("Alice"); crearTelefono("Bob");
    $("#btn-alice").addEventListener("click", () => alternar("Alice"));
    $("#btn-bob").addEventListener("click", () => alternar("Bob"));
    $("#btn-real").addEventListener("click", modoReal);
    document.querySelectorAll(".tabs-botones button").forEach((b) =>
      b.addEventListener("click", () => mostrarTab(b.closest(".tabs").id.replace("tabs-", ""), b.dataset.tab)));
    document.querySelector('form[data-panel="enc"]').addEventListener("submit", (e) => { e.preventDefault(); encriptarManual(); });
    document.querySelector('form[data-panel="des"]').addEventListener("submit", (e) => { e.preventDefault(); desencriptarManual(); });
    document.querySelector('form[data-panel="llaves"]').addEventListener("submit", (e) => { e.preventDefault(); actualizarLlaves(); });
    $("#enc-M").placeholder = T.ayuda_m;
    $("#des-C").placeholder = T.ayuda_c;
    $("#des-L").placeholder = T.ayuda_l;
    status(T.status.listo);
    aplicarModos();
    $("#cargando").classList.add("oculto");
  } catch (err) {
    console.error(err);
    $("#cargando").textContent = "No se pudo iniciar Python en el navegador: " + err;
  }
}
window.addEventListener("error", (e) => status("Error inesperado: " + e.message));
main();
