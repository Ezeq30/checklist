"use strict";

const DIAS_SEMANA = ["DOMINGO", "LUNES", "MARTES", "MIÉRCOLES", "JUEVES", "VIERNES", "SÁBADO"];
const ICONO_OK = '<svg class="estado-icon" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28"/><path d="M20 33l8 8 16-17"/></svg>';
const ICONO_INFO = '<svg class="estado-icon info" viewBox="0 0 64 64"><circle cx="32" cy="32" r="28"/><path d="M32 20v16M32 44v1"/></svg>';

const S = { estado: null, panel: "hoy", claveBody: "", calAnio: null, calMes: null, calendario: null };
let api = null;

const $ = (sel) => document.querySelector(sel);

function el(tag, clase, texto) {
  const nodo = document.createElement(tag);
  if (clase) nodo.className = clase;
  if (texto !== undefined) nodo.textContent = texto;
  return nodo;
}

function panelActual() {
  return S.estado.paneles[S.panel];
}

// Avisos y modales

function toast(tipo, titulo, mensaje, ms = 3600) {
  const t = el("div", `toast ${tipo}`);
  const cuerpo = el("div");
  cuerpo.append(el("strong", "", titulo));
  if (mensaje) cuerpo.append(el("span", "", mensaje));
  t.append(cuerpo);
  $("#toasts").append(t);
  setTimeout(() => {
    t.classList.add("saliendo");
    setTimeout(() => t.remove(), 400);
  }, ms);
}

function avisarResultado(res) {
  if (!res || res.tipo === "cancelado" || (res.ok && res.tipo === "ok" && !res.titulo)) return;
  const tipo = res.ok ? "ok" : res.tipo === "error" ? "error" : "warn";
  toast(tipo, res.titulo, res.mensaje);
}

function abrirModal(construir) {
  const capa = $("#modal-layer");
  const modal = $("#modal");
  modal.replaceChildren();
  capa.classList.remove("hidden");
  const cerrar = () => capa.classList.add("hidden");
  construir(modal, cerrar);
  capa.onclick = (e) => {
    if (e.target === capa) cerrar();
  };
  return cerrar;
}

function confirmar(titulo, mensaje, textoOk, claseOk = "accent") {
  return new Promise((resolve) => {
    abrirModal((modal, cerrar) => {
      modal.append(el("h3", "", titulo), el("p", "", mensaje));
      const acciones = el("div", "modal-acciones");
      const no = el("button", "btn", "Cancelar");
      const si = el("button", `btn ${claseOk}`, textoOk);
      no.onclick = () => {
        cerrar();
        resolve(false);
      };
      si.onclick = () => {
        cerrar();
        resolve(true);
      };
      acciones.append(no, si);
      modal.append(acciones);
      setTimeout(() => si.focus(), 50);
    });
  });
}

function modalAbierto() {
  return !$("#modal-layer").classList.contains("hidden");
}

// Render principal

function aplicar(estado) {
  S.estado = estado;
  render();
}

function render() {
  const p = panelActual();
  const raiz = document.documentElement.style;
  raiz.setProperty("--hipo", p.color);
  raiz.setProperty("--hipo-claro", p.claro);
  raiz.setProperty("--hipo-fg", p.fg);

  renderTabs();
  renderHead(p);
  renderXml();
  renderBody(p);
  renderLogin();
}

function renderTabs() {
  const tabs = $("#tabs");
  tabs.dataset.index = S.panel === "hoy" ? "0" : "1";
  const activo = panelActual();
  tabs.style.setProperty("--slider", activo.color);
  tabs.style.setProperty("--slider-fg", activo.fg);
  for (const panel of ["hoy", "manana"]) {
    const datos = S.estado.paneles[panel];
    $(`#tab-hipo-${panel}`).textContent = datos.nombre;
    tabs.querySelector(`[data-panel="${panel}"]`).classList.toggle("active", panel === S.panel);
  }
}

function renderHead(p) {
  $("#hipo-name").textContent = p.nombre;
  const fecha = new Date(`${p.fecha}T12:00:00`);
  $("#hipo-date").textContent = `${S.panel === "hoy" ? "HOY" : "MAÑANA"} · ${DIAS_SEMANA[fecha.getDay()]} ${p.fecha_display}`;

  const seg = $("#mode-seg");
  seg.dataset.index = p.modo === "dia1" ? "0" : "1";
  seg.classList.toggle("locked", !p.d1_hecho);
  seg.style.setProperty("--slider", p.color);
  seg.style.setProperty("--slider-fg", p.fg);
  seg.querySelectorAll(".seg-btn").forEach((b) => b.classList.toggle("active", b.dataset.modo === p.modo));

  const conChecks = p.vista === "checks";
  $("#progress").style.visibility = conChecks ? "visible" : "hidden";
  $("#btn-guardar").classList.toggle("hidden-soft", !conChecks);
  actualizarProgreso(p);
}

function actualizarProgreso(p) {
  const pct = p.total ? (p.hechos / p.total) * 100 : 0;
  $("#progress-fill").style.width = `${pct}%`;
  $("#progress-text").textContent = `${p.hechos}/${p.total}`;
  $("#progress").classList.toggle("full", p.total > 0 && p.hechos === p.total);
}

function renderXml() {
  const caja = $("#xml-alert");
  const x = S.estado.xml;
  if (!x || S.panel !== "hoy") {
    caja.classList.add("hidden");
    return;
  }
  caja.classList.remove("hidden", "saliendo");
  caja.style.setProperty("--x1", x.color);
  caja.style.setProperty("--x2", x.claro);
  $("#xml-text").textContent = x.texto;
}

function renderLogin() {
  const btn = $("#btn-login");
  btn.classList.toggle("admin", S.estado.admin);
  btn.title = S.estado.admin ? "Sesión de administrador activa (cerrar sesión)" : "Iniciar sesión de administrador";
}

function renderBody(p) {
  const clave = [S.panel, p.fecha, p.modo, p.vista, p.items.map((i) => i.nombre).join("|")].join("#");
  const body = $("#panel-body");
  if (clave === S.claveBody) {
    p.items.forEach((item, i) => {
      const card = body.querySelector(`.card[data-i="${i}"]`);
      if (card) card.classList.toggle("checked", item.checked);
    });
    return;
  }
  S.claveBody = clave;
  body.replaceChildren();

  if (p.vista === "completo") {
    body.append(vistaEstado(ICONO_OK, "Checklist completo", "Guardá el PDF, imprimilo o reiniciá el checklist.", [
      ["Imprimir", "ok", () => accionPdf("imprimir")],
      ["Guardar PDF", "info", () => accionPdf("guardar_pdf")],
      ["Reiniciar", "danger", reiniciar],
    ]));
    return;
  }
  if (p.vista === "d1_hecho") {
    body.append(vistaEstado(ICONO_OK, "Día 1 completado", "D2 habilitado. Continuá con el Día 2.", [
      ["Ir a D2", "accent", () => cambiarModo("dia2")],
    ]));
    return;
  }
  if (p.vista === "sin_items") {
    body.append(vistaEstado(ICONO_INFO, "Sin checklist de Día 2", "Este día no tiene hipódromo con checklist de Día 2.", []));
    return;
  }

  const grid = el("div", "grid");
  grid.style.setProperty("--filas", Math.max(1, Math.ceil(p.items.length / 2)));
  p.items.forEach((item, i) => grid.append(crearCard(item, i, p)));
  body.append(grid);
}

function vistaEstado(icono, titulo, sub, botones) {
  const box = el("div", "estado-box entrando");
  box.insertAdjacentHTML("beforeend", icono);
  box.append(el("div", "estado-titulo", titulo), el("div", "estado-sub", sub));
  if (botones.length) {
    const acciones = el("div", "estado-acciones");
    for (const [texto, clase, fn] of botones) {
      const b = el("button", `btn ${clase}`, texto);
      b.onclick = fn;
      acciones.append(b);
    }
    box.append(acciones);
  }
  return box;
}

function crearCard(item, i, p) {
  const card = el("div", `card${item.checked ? " checked" : ""}`);
  card.dataset.i = i;
  card.style.setProperty("--i", i);
  const tick = el("span", "tick");
  tick.innerHTML = '<svg viewBox="0 0 24 24"><path d="M5 12.5l4.5 4.5L19 7.5"/></svg>';
  card.append(tick);

  if (item.setear) {
    const texto = el("div", "card-setear");
    texto.append(el("span", "card-text", "SETEAR CATEGORIA"), el("span", "setear-hipo", p.nombre));
    card.append(texto);
  } else {
    card.append(el("span", "card-text", item.nombre));
  }

  card.onclick = () => toggleCheck(i);
  return card;
}

// Acciones del checklist

async function toggleCheck(i) {
  const p = panelActual();
  const item = p.items[i];
  item.checked = !item.checked;
  p.hechos += item.checked ? 1 : -1;
  $(`.card[data-i="${i}"]`).classList.toggle("checked", item.checked);
  actualizarProgreso(p);
  const r = await api.toggle_check(S.panel, item.nombre, item.checked);
  aplicar(r.estado);
}

async function cambiarModo(modo) {
  const p = panelActual();
  if (p.modo === modo) return;
  const r = await api.set_modo(S.panel, modo);
  if (!r.resultado.ok) {
    const seg = $("#mode-seg");
    seg.classList.remove("shake");
    void seg.offsetWidth;
    seg.classList.add("shake");
    avisarResultado(r.resultado);
  }
  aplicar(r.estado);
}

async function guardar() {
  const p = panelActual();
  const r = await api.guardar(S.panel, p.modo, p.items.map((i) => i.nombre));
  if (r.resultado.tipo === "desfasado") S.claveBody = "";
  avisarResultado(r.resultado);
  aplicar(r.estado);
}

async function reiniciar() {
  const ok = await confirmar("Reiniciar checklist", "Se borran los checks y el estado de este día. ¿Querés reiniciarlo?", "Reiniciar", "danger");
  if (!ok) return;
  const r = await api.reiniciar(S.panel);
  aplicar(r.estado);
  toast("info", "Checklist reiniciado", "Empezá de nuevo por el Día 1.");
}

async function accionPdf(metodo) {
  const r = await api[metodo](S.panel);
  avisarResultado(r);
}

async function marcarXml() {
  const x = S.estado.xml;
  if (!x) return;
  const ok = await confirmar(`XML ${x.nombre}`, x.confirmacion, "Sí, ya lo subí", "ok");
  if (!ok) return;
  const caja = $("#xml-alert");
  caja.classList.add("saliendo");
  const r = await api.marcar_xml(x.fecha);
  setTimeout(() => {
    aplicar(r.estado);
    toast("ok", "XML marcado como subido", `${x.sigla} del ${x.fecha.slice(8, 10)}/${x.fecha.slice(5, 7)}`);
  }, 350);
}

// Login

function abrirLogin() {
  if (S.estado.admin) {
    confirmar("Sesión de administrador", "¿Querés cerrar la sesión de administrador?", "Cerrar sesión", "danger").then(async (ok) => {
      if (!ok) return;
      const r = await api.logout();
      aplicar(r.estado);
      if (S.calendario) renderCalendario();
      toast("info", "Sesión cerrada", "");
    });
    return;
  }
  abrirModal((modal, cerrar) => {
    modal.append(el("h3", "", "Login administrador"), el("p", "", "Necesario para modificar el calendario de hipódromos."));
    const usuario = campo(modal, "USUARIO", "text");
    const clave = campo(modal, "CLAVE", "password");
    const acciones = el("div", "modal-acciones");
    const cancelar = el("button", "btn", "Cancelar");
    const entrar = el("button", "btn ok", "Entrar");
    acciones.append(cancelar, entrar);
    modal.append(acciones);

    const enviar = async () => {
      const r = await api.login(usuario.value, clave.value);
      avisarResultado(r.resultado);
      if (r.resultado.ok) {
        cerrar();
        aplicar(r.estado);
        if (S.calendario) renderCalendario();
      } else {
        clave.select();
      }
    };
    cancelar.onclick = cerrar;
    entrar.onclick = enviar;
    usuario.onkeydown = (e) => e.key === "Enter" && clave.focus();
    clave.onkeydown = (e) => e.key === "Enter" && enviar();
    setTimeout(() => usuario.focus(), 50);
  });
}

function campo(padre, etiqueta, tipo) {
  const c = el("div", "campo");
  const input = el("input");
  input.type = tipo;
  input.autocomplete = "off";
  c.append(el("label", "", etiqueta), input);
  padre.append(c);
  return input;
}

// Calendario

async function abrirCalendario() {
  const hoy = new Date(`${S.estado.hoy}T12:00:00`);
  S.calAnio = hoy.getFullYear();
  S.calMes = hoy.getMonth() + 1;
  await cargarCalendario();
  $("#drawer").classList.add("open");
  $("#drawer").setAttribute("aria-hidden", "false");
  $("#backdrop").classList.add("visible");
}

function cerrarCalendario() {
  cerrarPopover();
  $("#drawer").classList.remove("open");
  $("#drawer").setAttribute("aria-hidden", "true");
  $("#backdrop").classList.remove("visible");
  S.calendario = null;
}

async function moverMes(delta) {
  S.calMes += delta;
  if (S.calMes < 1) {
    S.calMes = 12;
    S.calAnio -= 1;
  } else if (S.calMes > 12) {
    S.calMes = 1;
    S.calAnio += 1;
  }
  await cargarCalendario();
}

async function cargarCalendario() {
  S.calendario = await api.calendario(S.calAnio, S.calMes);
  renderCalendario();
}

function renderCalendario() {
  const cal = S.calendario;
  $("#cal-title").textContent = cal.titulo;
  const grid = $("#cal-grid");
  grid.replaceChildren();
  for (let i = 0; i < cal.offset; i++) grid.append(el("div", "day vacio"));
  cal.dias.forEach((d, i) => {
    const celda = el("button", `day${d.hipo ? " con-hipo" : ""}${d.hoy ? " hoy" : ""}`, String(d.dia));
    celda.style.setProperty("--i", i);
    if (d.hipo) {
      celda.style.setProperty("--dia", d.color);
      celda.style.setProperty("--dia-fg", d.fg);
      celda.title = d.hipo;
    }
    celda.onclick = (e) => clickDia(d, e.currentTarget);
    grid.append(celda);
  });

  const leyenda = $("#cal-legend");
  leyenda.replaceChildren();
  for (const h of S.estado.hipodromos) {
    const item = el("span");
    const color = el("i");
    color.style.setProperty("--c", h.color);
    item.append(color, document.createTextNode(h.nombre));
    leyenda.append(item);
  }
  const hint = $("#cal-hint");
  hint.textContent = S.estado.admin ? "Modo admin: tocá un día para asignarle hipódromo." : "Iniciá sesión para modificar el calendario.";
  hint.classList.toggle("admin", S.estado.admin);
}

function clickDia(dia, celda) {
  if (!S.estado.admin) {
    toast("warn", "Bloqueado", "Iniciá sesión para modificar el calendario");
    return;
  }
  const pop = $("#popover");
  pop.replaceChildren(el("div", "popover-title", `${dia.fecha.slice(8, 10)}/${dia.fecha.slice(5, 7)}/${dia.fecha.slice(0, 4)}`));
  for (const h of S.estado.hipodromos) {
    const b = el("button", "", h.nombre);
    b.style.setProperty("--c", h.color);
    b.style.setProperty("--cf", h.fg);
    b.onclick = () => editarDia(() => api.asignar(dia.fecha, h.id));
    pop.append(b);
  }
  const borrar = el("button", "", "BORRAR");
  borrar.style.setProperty("--c", "#475569");
  borrar.style.setProperty("--cf", "#fff");
  borrar.onclick = () => editarDia(() => api.borrar(dia.fecha));
  pop.append(borrar);

  const drawer = $("#drawer").getBoundingClientRect();
  const r = celda.getBoundingClientRect();
  pop.classList.remove("hidden");
  const alto = pop.offsetHeight;
  const left = Math.min(Math.max(r.left - drawer.left + r.width / 2 - 80, 8), drawer.width - 168);
  let top = r.bottom - drawer.top + 6;
  if (top + alto > drawer.height - 8) top = r.top - drawer.top - alto - 6;
  pop.style.left = `${left}px`;
  pop.style.top = `${Math.max(top, 8)}px`;
}

function cerrarPopover() {
  $("#popover").classList.add("hidden");
}

async function editarDia(llamada) {
  cerrarPopover();
  const r = await llamada();
  if (!r.resultado.ok) avisarResultado(r.resultado);
  aplicar(r.estado);
  await cargarCalendario();
}

// Eventos

function conectarEventos() {
  document.querySelectorAll("#tabs .tab").forEach((b) => {
    b.onclick = () => {
      if (S.panel === b.dataset.panel) return;
      S.panel = b.dataset.panel;
      render();
    };
  });
  document.querySelectorAll("#mode-seg .seg-btn").forEach((b) => {
    b.onclick = () => cambiarModo(b.dataset.modo);
  });
  $("#btn-guardar").onclick = guardar;
  $("#xml-listo").onclick = marcarXml;
  $("#btn-calendario").onclick = abrirCalendario;
  $("#btn-login").onclick = abrirLogin;
  $("#cal-close").onclick = cerrarCalendario;
  $("#cal-prev").onclick = () => moverMes(-1);
  $("#cal-next").onclick = () => moverMes(1);
  $("#backdrop").onclick = cerrarCalendario;
  $("#drawer").addEventListener("click", (e) => {
    if (!e.target.closest(".popover") && !e.target.closest(".day")) cerrarPopover();
  });
  document.addEventListener("keydown", (e) => {
    if (e.key !== "Escape") return;
    if (modalAbierto()) $("#modal-layer").classList.add("hidden");
    else if (!$("#popover").classList.contains("hidden")) cerrarPopover();
    else if ($("#drawer").classList.contains("open")) cerrarCalendario();
  });
}

// Conexión con Python o API simulada

function obtenerApi() {
  if (window.pywebview && window.pywebview.api) return Promise.resolve(window.pywebview.api);
  return new Promise((resolve) => {
    let listo = false;
    window.addEventListener("pywebviewready", () => {
      listo = true;
      resolve(window.pywebview.api);
    });
    setTimeout(() => {
      if (!listo) resolve(crearApiSimulada());
    }, 900);
  });
}

function crearApiSimulada() {
  const HIPOS = {
    "San isidro": { nombre: "SAN ISIDRO", color: "#2E7D32", claro: "#4CAF50", fg: "#FFFFFF", d2: ["SETEAR CATEGORIA", "VOLVER A REVISAR EL PROGRAMA Y POSTING", "VER SI HAY BORRADOS AGREGADOS", "BLOQUEAR / DESBLOQUEAR AGENTES", "PONER TIPS EN SERVICIO", "PONER TERMINALES EN SERVICIO", "RESETEAR TERMINALES", "TELLER VOUCHER LIMIT $500,000", "ABRIR LA VENTA A LA HORA INDICADA", "CANAL 26 ASIGNACION 29", "GENERAR DETALLE", "CARGAR EL VIDEO EN LA APP MOBILE"] },
    "La plata": { nombre: "LA PLATA", color: "#1565C0", claro: "#42A5F5", fg: "#FFFFFF", d2: ["SETEAR CATEGORIA", "VOLVER A REVISAR EL PROGRAMA Y POSTING", "CAMBIAR EN LAS VENTANILLAS LOS AGENTES", "BLOQUEAR / DESBLOQUEAR AGENTES", "PONER TIPS EN SERVICIO", "PONER TERMINALES EN SERVICIO", "RESETEAR TERMINALES", "ABRIR LA VENTA A LA HORA INDICADA", "CARGAR EL VIDEO EN LA APP MOBILE", "SETEAR VIDEOS POR MEET"] },
    "Palermo": { nombre: "PALERMO", color: "#F9A825", claro: "#FDD835", fg: "#000000", d2: ["SETEAR CATEGORIA", "VOLVER A REVISAR EL PROGRAMA", "BLOQUEAR / DESBLOQUEAR AGENTES", "PONER TIPS EN SERVICIO", "PONER TERMINALES EN SERVICIO", "RESETEAR TERMINALES", "SETEAR VIDEOS POR MEET"] },
    "Sin hipodromo": { nombre: "SIN HIPODROMO", color: "#C62828", claro: "#EF4444", fg: "#FFFFFF", d2: [] },
  };
  const D1 = ["FECHA Y ESTADO", "MEET Y PERFORMANCE", "CALC PRICES", "REGLA DE CALCULO POR CARRERA", "CABALLOS Y APUESTAS POR CARRERA", "TABLA DE COMISIONES POR CARRERA", "MONTOS MINIMOS POR APUESTA Y CARRERA", "DEFAULT MINIMOS ARG USD PER", "TIM BETTING CONTROL POR ASOCIACION", "IMPORT BETTING CONTROL", "LOCAL ASSOC BETTING CONTROL", "SALES TAX ASSOCIATION", "PRINTERS", "STATE BETTING CONTROL"];
  const XML = { "San isidro": "SI", "La plata": "LP" };
  const MESES = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];
  const iso = (d) => `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
  const hoyD = new Date();
  hoyD.setHours(12, 0, 0, 0);
  const masDias = (n) => new Date(hoyD.getTime() + n * 86400000);
  const ciclo = ["San isidro", "La plata", "Palermo"];
  const data = { calendario: {}, checklist: {}, estado: {}, xml: {} };
  for (let n = -40; n < 70; n++) data.calendario[iso(masDias(n))] = ciclo[(n % 3 + 3) % 3];
  const modos = { hoy: "dia1", manana: "dia1" };
  let admin = false;
  const r = (ok, tipo, titulo = "", mensaje = "") => ({ ok, tipo, titulo, mensaje });
  const fechaPanel = (p) => iso(masDias(p === "hoy" ? 0 : 1));
  const d1Hecho = (f) => ["dia1_completado", "completo"].includes(data.estado[f]);
  const items = (f, m) => (m === "dia1" ? D1 : (HIPOS[data.calendario[f]] || HIPOS["San isidro"]).d2);
  const pendiente = () => Object.keys(data.calendario).sort().find((f) => XML[data.calendario[f]] && !data.xml[f] && masDias(-2) <= new Date(`${f}T12:00:00`) && new Date(`${f}T12:00:00`) <= hoyD);
  const panel = (p) => {
    const f = fechaPanel(p);
    const h = HIPOS[data.calendario[f]];
    if (!d1Hecho(f)) modos[p] = "dia1";
    const lista = items(f, modos[p]);
    const checks = data.checklist[f] || {};
    const estado = data.estado[f] || "";
    const vista = estado === "completo" ? "completo" : modos[p] === "dia1" && d1Hecho(f) ? "d1_hecho" : lista.length ? "checks" : "sin_items";
    return {
      panel: p, fecha: f, fecha_display: `${f.slice(8, 10)}/${f.slice(5, 7)}/${f.slice(0, 4)}`,
      hipo: data.calendario[f] || "", nombre: h ? h.nombre : "Sin carrera", color: h ? h.color : "#38BDF8", claro: h ? h.claro : "#7DD3FC", fg: h ? h.fg : "#FFFFFF",
      estado, d1_hecho: d1Hecho(f), modo: modos[p], vista,
      items: lista.map((n) => ({ nombre: n, checked: !!checks[n], setear: modos[p] === "dia2" && n === "SETEAR CATEGORIA" })),
      hechos: lista.filter((n) => checks[n]).length, total: lista.length,
    };
  };
  const estado = () => {
    const f = pendiente();
    const h = f && data.calendario[f];
    return {
      hoy: iso(hoyD), admin,
      paneles: { hoy: panel("hoy"), manana: panel("manana") },
      xml: f ? { fecha: f, hipo: h, sigla: XML[h], nombre: HIPOS[h].nombre, color: HIPOS[h].color, claro: HIPOS[h].claro, texto: `SUBIR EL XML DE ${XML[h]} (${f.slice(8, 10)}/${f.slice(5, 7)})`, confirmacion: `¿Confirmás que subiste el XML de ${XML[h]} del ${f.slice(8, 10)}/${f.slice(5, 7)}?` } : null,
      hipodromos: Object.entries(HIPOS).map(([id, h2]) => ({ id, nombre: h2.nombre, color: h2.color, fg: h2.fg })),
    };
  };
  const conEstado = (res) => Promise.resolve({ resultado: res, estado: estado() });
  window.__mock = data;
  return {
    estado: () => Promise.resolve(estado()),
    toggle_check: (p, item, v) => {
      const f = fechaPanel(p);
      (data.checklist[f] = data.checklist[f] || {})[item] = v;
      return conEstado(r(true, "ok"));
    },
    set_modo: (p, m) => {
      if (m === "dia2" && !d1Hecho(fechaPanel(p))) return conEstado(r(false, "d1_pendiente", "Día 1 pendiente", "Todavía no se completó el Día 1. Completá y guardá el Día 1 para poder pasar al Día 2."));
      modos[p] = m;
      return conEstado(r(true, "ok"));
    },
    guardar: (p) => {
      const f = fechaPanel(p);
      const lista = items(f, modos[p]);
      const hechos = lista.filter((n) => (data.checklist[f] || {})[n]).length;
      if (hechos < lista.length) return conEstado(r(false, "incompleto", "Incompleto", `Completá todos los items (${hechos}/${lista.length})`));
      if (modos[p] === "dia1") {
        data.estado[f] = "dia1_completado";
        modos[p] = "dia2";
        return conEstado(r(true, "dia1_completado", "Día 1 completado", `(${hechos}/${lista.length}) Ahora completá el Día 2.`));
      }
      data.estado[f] = "completo";
      return conEstado(r(true, "completo", "Checklist completo", "Guardá el PDF, imprimilo o reiniciá."));
    },
    reiniciar: (p) => {
      const f = fechaPanel(p);
      delete data.checklist[f];
      delete data.estado[f];
      modos[p] = "dia1";
      return conEstado(r(true, "ok"));
    },
    marcar_xml: (f) => {
      data.xml[f] = true;
      return conEstado(r(true, "ok"));
    },
    calendario: (anio, mes) => {
      const total = new Date(anio, mes, 0).getDate();
      const dias = [];
      for (let d = 1; d <= total; d++) {
        const f = `${anio}-${String(mes).padStart(2, "0")}-${String(d).padStart(2, "0")}`;
        const h = HIPOS[data.calendario[f]];
        dias.push({ dia: d, fecha: f, hipo: h ? data.calendario[f] : "", color: h ? h.color : "", fg: h ? h.fg : "", hoy: f === iso(hoyD) });
      }
      return Promise.resolve({ anio, mes, titulo: `${MESES[mes - 1]} ${anio}`, offset: new Date(anio, mes - 1, 1).getDay(), dias });
    },
    login: (u, c) => {
      admin = u.trim() === "admin" && c.trim() === "eze1";
      return conEstado(admin ? r(true, "ok", "Sesión iniciada", "Ya podés modificar el calendario.") : r(false, "error", "Error", "Usuario o clave incorrectos"));
    },
    logout: () => {
      admin = false;
      return conEstado(r(true, "ok"));
    },
    asignar: (f, h) => {
      data.calendario[f] = h;
      return conEstado(r(true, "ok"));
    },
    borrar: (f) => {
      delete data.calendario[f];
      return conEstado(r(true, "ok"));
    },
    guardar_pdf: () => Promise.resolve(r(true, "ok", "PDF guardado", "(simulado)")),
    imprimir: () => Promise.resolve(r(true, "ok", "Vista previa", "(simulado)")),
  };
}

async function iniciar() {
  api = await obtenerApi();
  conectarEventos();
  aplicar(await api.estado());
  setInterval(async () => aplicar(await api.estado()), 60000);
}

document.addEventListener("DOMContentLoaded", iniciar);
