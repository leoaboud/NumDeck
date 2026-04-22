/**
 * app.js — NumDeck
 * Ponte entre a interface HTML e o backend Python (pywebview).
 * 
 * Comunicação:
 *   JS → Python:  await window.pywebview.api.metodo(args)
 *   Python → JS:  window.evaluate_js("funcaoJS(dados)")
 */

/* ════════════════════════════════════════════════════════
   ESTADO GLOBAL
════════════════════════════════════════════════════════ */
let state = {
  config:          null,   // config completa do backend
  selectedKeyId:   null,   // tecla selecionada no painel
  activeProfile:   "Dev Mode",
  deckEnabled:     true,
  pendingChanges:  {},     // mudanças não salvas ainda
};

const TYPE_HINTS = {
  open_app:       "Caminho do executável. Ex: C:\\Program Files\\...\\app.exe",
  open_url:       "URL completa. Ex: https://www.google.com",
  shortcut:       "Teclas separadas por +. Ex: ctrl+c  /  ctrl+shift+esc  /  f5",
  text:           "Texto que será digitado automaticamente.",
  terminal_admin: "Nenhum valor necessário — abre o Terminal como Admin.",
  screenshot:     "Nenhum valor necessário — ativa Win+Shift+S.",
  profile_switch: "Nenhum valor necessário — alterna para o próximo perfil.",
  toggle:         "Nenhum valor necessário — liga/desliga o deck.",
  none:           "",
};

/* ════════════════════════════════════════════════════════
   INICIALIZAÇÃO
════════════════════════════════════════════════════════ */
window.addEventListener("pywebviewready", async () => {
  await loadConfig();
  renderAllKeys();
  updateProfileSelector();
  updateFooter();
  document.getElementById("deviceStatus").querySelector(".status-dot").classList.add("connected");
  document.getElementById("deviceLabel").textContent = "Exbom USB · Conectado";

  // Seleciona primeira tecla automaticamente
  selectKey("KP_1");
});

// Fallback para desenvolvimento sem pywebview
window.addEventListener("DOMContentLoaded", () => {
  if (typeof window.pywebview === "undefined") {
    console.warn("[NumDeck] pywebview não disponível — modo preview.");
    loadMockConfig();
  }
});

/* ════════════════════════════════════════════════════════
   CONFIG
════════════════════════════════════════════════════════ */
async function loadConfig() {
  try {
    const raw = await window.pywebview.api.get_config();
    state.config = JSON.parse(raw);
    state.activeProfile = state.config.active_profile;
  } catch (e) {
    console.error("[loadConfig]", e);
  }
}

function getActiveProfileKeys() {
  return state.config?.profiles?.[state.activeProfile] || {};
}

function getKeyConfig(keyId) {
  return getActiveProfileKeys()[keyId] || null;
}

/* ════════════════════════════════════════════════════════
   RENDER KEYS — aplica cor, ícone e label no layout
════════════════════════════════════════════════════════ */
function renderAllKeys() {
  const keys = getActiveProfileKeys();
  document.querySelectorAll(".key").forEach(el => {
    const keyId = el.dataset.key;
    const cfg   = keys[keyId];
    applyKeyVisual(el, cfg);
  });
}

function applyKeyVisual(el, cfg) {
  // Remove todas as classes de cor existentes
  el.classList.remove("color-blue","color-green","color-orange","color-purple","color-cyan","color-red","color-gray");

  if (!cfg) {
    el.querySelector(".key-icon").textContent  = "·";
    el.querySelector(".key-label").textContent = "vazio";
    el.classList.add("color-gray");
    return;
  }

  el.querySelector(".key-icon").textContent  = cfg.icon  || "·";
  el.querySelector(".key-label").textContent = cfg.name  || "sem ação";
  el.classList.add("color-" + (cfg.color || "gray"));
}

/* ════════════════════════════════════════════════════════
   SELEÇÃO DE TECLA
════════════════════════════════════════════════════════ */
function selectKey(keyId) {
  // Remove seleção anterior
  document.querySelectorAll(".key.selected").forEach(k => k.classList.remove("selected"));

  // Seleciona nova
  const el = document.getElementById("key-" + keyId);
  if (el) el.classList.add("selected");

  state.selectedKeyId = keyId;
  state.pendingChanges = {};

  // Preenche o painel com os dados da tecla
  const cfg = getKeyConfig(keyId);
  fillPanel(keyId, cfg);
}

/* ════════════════════════════════════════════════════════
   PAINEL DE CONFIGURAÇÃO
════════════════════════════════════════════════════════ */
function fillPanel(keyId, cfg) {
  document.getElementById("panelKeyBadge").textContent = keyId.replace("KP_", "");

  if (!cfg) {
    document.getElementById("fieldName").value  = "";
    document.getElementById("fieldValue").value = "";
    document.getElementById("fieldIcon").value  = "";
    setTypeUI("none");
    setColorUI("gray");
    return;
  }

  document.getElementById("fieldName").value  = cfg.name  || "";
  document.getElementById("fieldValue").value = cfg.value || "";
  document.getElementById("fieldIcon").value  = cfg.icon  || "";

  setTypeUI(cfg.type  || "none");
  setColorUI(cfg.color || "gray");
  highlightIconPicker(cfg.icon);
  updateValueHint(cfg.type);
}

/* ── Tipo ────────────────────────────────────────────── */
function setType(btn) {
  document.querySelectorAll(".type-btn").forEach(b => b.classList.remove("active"));
  btn.classList.add("active");

  const type = btn.dataset.type;
  state.pendingChanges.type = type;
  updateValueHint(type);
}

function setTypeUI(type) {
  document.querySelectorAll(".type-btn").forEach(b => {
    b.classList.toggle("active", b.dataset.type === type);
  });
  updateValueHint(type);
}

function updateValueHint(type) {
  const hint = TYPE_HINTS[type] || "";
  document.getElementById("fieldHint").textContent = hint;

  // Esconde campo de valor para tipos que não precisam
  const noValueTypes = ["terminal_admin", "screenshot", "profile_switch", "toggle", "none"];
  document.getElementById("fieldValueGroup").style.opacity =
    noValueTypes.includes(type) ? "0.4" : "1";
}

/* ── Cor ─────────────────────────────────────────────── */
function setColor(dot) {
  document.querySelectorAll(".color-dot").forEach(d => d.classList.remove("active"));
  dot.classList.add("active");
  state.pendingChanges.color = dot.dataset.color;

  // Preview em tempo real na tecla
  if (state.selectedKeyId) {
    const el = document.getElementById("key-" + state.selectedKeyId);
    if (el) {
      el.classList.remove("color-blue","color-green","color-orange","color-purple","color-cyan","color-red","color-gray");
      el.classList.add("color-" + dot.dataset.color);
    }
  }
}

function setColorUI(color) {
  document.querySelectorAll(".color-dot").forEach(d => {
    d.classList.toggle("active", d.dataset.color === color);
  });
}

/* ── Ícone ───────────────────────────────────────────── */
function setIcon(span) {
  document.querySelectorAll(".icon-opt").forEach(i => i.classList.remove("active"));
  span.classList.add("active");

  const icon = span.textContent;
  document.getElementById("fieldIcon").value = icon;
  state.pendingChanges.icon = icon;

  // Preview em tempo real na tecla
  if (state.selectedKeyId) {
    const el = document.getElementById("key-" + state.selectedKeyId);
    if (el) el.querySelector(".key-icon").textContent = icon;
  }
}

function highlightIconPicker(icon) {
  document.querySelectorAll(".icon-opt").forEach(opt => {
    opt.classList.toggle("active", opt.textContent === icon);
  });
}

/* ── Salvar ──────────────────────────────────────────── */
async function saveKey() {
  if (!state.selectedKeyId) return;

  const type = document.querySelector(".type-btn.active")?.dataset.type || "none";
  const color = document.querySelector(".color-dot.active")?.dataset.color || "gray";
  const icon = document.getElementById("fieldIcon").value.trim()
             || document.querySelector(".icon-opt.active")?.textContent
             || "·";

  const actionData = {
    name:  document.getElementById("fieldName").value.trim() || "Sem nome",
    type:  type,
    value: document.getElementById("fieldValue").value.trim(),
    icon:  icon,
    color: color,
  };

  try {
    await window.pywebview.api.save_key(state.selectedKeyId, actionData);

    // Atualiza config local
    if (!state.config.profiles[state.activeProfile]) {
      state.config.profiles[state.activeProfile] = {};
    }
    state.config.profiles[state.activeProfile][state.selectedKeyId] = actionData;

    // Atualiza visual da tecla
    const el = document.getElementById("key-" + state.selectedKeyId);
    if (el) applyKeyVisual(el, actionData);

    showToast("✓ Salvo!", "success");
    addLog(actionData.name, "configurado");
  } catch (e) {
    console.error("[saveKey]", e);
    showToast("Erro ao salvar", "error");
  }
}

/* ── Limpar ──────────────────────────────────────────── */
async function clearKey() {
  if (!state.selectedKeyId) return;

  const empty = { name: "Sem ação", type: "none", value: "", icon: "·", color: "gray" };

  try {
    await window.pywebview.api.save_key(state.selectedKeyId, empty);

    if (state.config?.profiles?.[state.activeProfile]) {
      delete state.config.profiles[state.activeProfile][state.selectedKeyId];
    }

    const el = document.getElementById("key-" + state.selectedKeyId);
    if (el) applyKeyVisual(el, null);

    fillPanel(state.selectedKeyId, null);
    showToast("Tecla limpa", "success");
  } catch (e) {
    showToast("Erro ao limpar", "error");
  }
}

/* ── Testar tecla ────────────────────────────────────── */
async function testCurrentKey() {
  if (!state.selectedKeyId) return;
  try {
    await window.pywebview.api.test_key(state.selectedKeyId);
    flashKey(state.selectedKeyId);
    addLog(getKeyConfig(state.selectedKeyId)?.name || state.selectedKeyId, "testado");
  } catch (e) {
    showToast("Erro ao testar", "error");
  }
}

/* ════════════════════════════════════════════════════════
   PERFIS
════════════════════════════════════════════════════════ */
function openProfileMenu() {
  const dropdown = document.getElementById("profileDropdown");
  dropdown.classList.toggle("hidden");

  if (!dropdown.classList.contains("hidden")) {
    renderProfileList();
    document.addEventListener("click", closeProfileMenu, true);
  }
}

function closeProfileMenu(e) {
  const dropdown = document.getElementById("profileDropdown");
  const selector = document.getElementById("profileSelector");
  if (!selector.contains(e.target)) {
    dropdown.classList.add("hidden");
    document.removeEventListener("click", closeProfileMenu, true);
  }
}

async function renderProfileList() {
  const list = document.getElementById("profileList");
  list.innerHTML = "";

  try {
    const raw = await window.pywebview.api.get_profiles();
    const profiles = JSON.parse(raw);

    profiles.forEach(name => {
      const div = document.createElement("div");
      div.className = "dropdown-item" + (name === state.activeProfile ? " active" : "");
      div.textContent = name;
      div.onclick = () => switchProfile(name);
      list.appendChild(div);
    });
  } catch (e) {
    console.error("[renderProfileList]", e);
  }
}

async function switchProfile(name) {
  document.getElementById("profileDropdown").classList.add("hidden");

  try {
    const raw = await window.pywebview.api.switch_profile(name);
    state.config = JSON.parse(raw);
    state.activeProfile = name;
    renderAllKeys();
    updateProfileSelector();
    updateFooter();
    showToast("Perfil: " + name, "success");

    if (state.selectedKeyId) selectKey(state.selectedKeyId);
  } catch (e) {
    showToast("Erro ao trocar perfil", "error");
  }
}

async function promptNewProfile() {
  document.getElementById("profileDropdown").classList.add("hidden");
  const name = prompt("Nome do novo perfil:");
  if (!name || !name.trim()) return;

  try {
    await window.pywebview.api.create_profile(name.trim());
    await switchProfile(name.trim());
  } catch (e) {
    showToast("Erro ao criar perfil", "error");
  }
}

function updateProfileSelector() {
  document.getElementById("activeProfileLabel").textContent = state.activeProfile;
}

/* ════════════════════════════════════════════════════════
   CALLBACKS DO PYTHON → JS
   (chamados via window.evaluate_js)
════════════════════════════════════════════════════════ */

/** Tecla física pressionada — anima na interface */
function onKeyPressed(keyId) {
  flashKey(keyId);
  const cfg = getKeyConfig(keyId);
  if (cfg) addLog(cfg.name, "acionado");
}

/** Deck ligado/desligado */
function onDeckToggle(enabled) {
  state.deckEnabled = enabled;
  const frame = document.getElementById("numpadFrame");
  frame.classList.toggle("disabled", !enabled);

  const key = document.getElementById("key-KP_NUMLOCK");
  if (key) {
    key.querySelector(".key-label").textContent = enabled ? "Liga/Desl." : "DESLIGADO";
  }

  showToast(enabled ? "✓ Deck ligado" : "⏻ Deck desligado", enabled ? "success" : "error");
}

/** Perfil alternado pelo numpad físico */
function onProfileSwitch(newConfig) {
  state.config = newConfig;
  state.activeProfile = newConfig.active_profile;
  renderAllKeys();
  updateProfileSelector();
  updateFooter();
  showToast("Perfil: " + state.activeProfile, "success");
}

/* ════════════════════════════════════════════════════════
   UTILITÁRIOS
════════════════════════════════════════════════════════ */

/** Anima o flash de uma tecla */
function flashKey(keyId) {
  const el = document.getElementById("key-" + keyId);
  if (!el) return;
  el.classList.remove("pressed");
  void el.offsetWidth; // reflow
  el.classList.add("pressed");
  setTimeout(() => el.classList.remove("pressed"), 350);
}

/** Adiciona entrada no log de atividade */
function addLog(actionName, detail) {
  const log = document.getElementById("logArea");
  const empty = log.querySelector(".log-empty");
  if (empty) empty.remove();

  const now = new Date();
  const time = now.toTimeString().slice(0, 8);

  const entry = document.createElement("div");
  entry.className = "log-entry";
  entry.innerHTML = `
    <span class="log-time">${time}</span>
    <span class="log-action">${actionName}</span>
    <span class="log-detail">${detail}</span>
  `;

  log.prepend(entry);

  // Mantém apenas os últimos 8 registros
  while (log.children.length > 8) {
    log.removeChild(log.lastChild);
  }
}

/** Toast notification */
let toastTimer = null;
function showToast(msg, type = "") {
  const toast = document.getElementById("toast");
  toast.textContent = msg;
  toast.className = "toast" + (type ? " " + type : "");
  toast.classList.remove("hidden");

  if (toastTimer) clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.add("hidden"), 2200);
}

/** Minimizar para bandeja */
async function minimizeToTray() {
  try {
    await window.pywebview.api.minimize_to_tray();
  } catch (e) {
    console.warn("minimize_to_tray não disponível");
  }
}

/** Footer */
function updateFooter() {
  document.getElementById("footerProfile").textContent = state.activeProfile;
}

/* ════════════════════════════════════════════════════════
   MODO PREVIEW (sem pywebview)
   Carrega a config padrão diretamente no JS para testar o visual
════════════════════════════════════════════════════════ */
function loadMockConfig() {
  state.config = {
    active_profile: "Dev Mode",
    profiles: {
      "Dev Mode": {
        "KP_NUMLOCK":   { name:"Liga/Desl.",     type:"toggle",         value:"",                 icon:"⏻", color:"red"    },
        "KP_DIVIDE":    { name:"Alt. Modo",       type:"profile_switch", value:"",                 icon:"⇄", color:"cyan"   },
        "KP_MULTIPLY":  { name:"Git Commit",      type:"shortcut",       value:"ctrl+alt+k",       icon:"⬆", color:"orange" },
        "KP_MINUS":     { name:"Ctrl+V",          type:"shortcut",       value:"ctrl+v",           icon:"📋",color:"blue"   },
        "KP_7":         { name:"Terminal ADM",    type:"terminal_admin", value:"",                 icon:"⚡", color:"purple" },
        "KP_8":         { name:"Run Code",        type:"shortcut",       value:"f5",               icon:"▶", color:"green"  },
        "KP_9":         { name:"Docker",          type:"open_app",       value:"Docker Desktop",   icon:"🐳",color:"blue"   },
        "KP_PLUS":      { name:"Ctrl+C",          type:"shortcut",       value:"ctrl+c",           icon:"©", color:"green"  },
        "KP_4":         { name:"Deezer",          type:"open_url",       value:"https://deezer.com",icon:"♫",color:"orange" },
        "KP_5":         { name:"Obsidian",        type:"open_app",       value:"Obsidian",         icon:"🌑",color:"purple" },
        "KP_6":         { name:"Edge",            type:"open_app",       value:"msedge.exe",       icon:"🌐",color:"blue"   },
        "KP_BACKSPACE": { name:"Task Manager",    type:"shortcut",       value:"ctrl+shift+esc",   icon:"📊",color:"red"    },
        "KP_1":         { name:"VSCode",          type:"open_app",       value:"code",             icon:"{}",color:"blue"   },
        "KP_2":         { name:"Google",          type:"open_url",       value:"https://google.com",icon:"🔍",color:"cyan"  },
        "KP_3":         { name:"WhatsApp",        type:"open_app",       value:"WhatsApp",         icon:"💬",color:"green"  },
        "KP_ENTER":     { name:"Meu App",         type:"open_app",       value:"meuapp.exe",       icon:"⚙", color:"orange" },
        "KP_0":         { name:"Alt+Tab",         type:"shortcut",       value:"alt+tab",          icon:"⇥", color:"cyan"   },
        "KP_DOT":       { name:"Print+Copy",      type:"screenshot",     value:"",                 icon:"✂", color:"red"    },
      }
    }
  };

  state.activeProfile = "Dev Mode";
  renderAllKeys();
  updateProfileSelector();
  updateFooter();
  selectKey("KP_1");

  // Sobrescreve pywebview.api com mocks para testar na interface sem Python
  window.pywebview = {
    api: {
      get_config:        async () => JSON.stringify(state.config),
      save_key:          async (id, data) => {
        state.config.profiles[state.activeProfile][id] = data;
        return { success: true };
      },
      get_profiles:      async () => JSON.stringify(Object.keys(state.config.profiles)),
      switch_profile:    async (name) => {
        state.activeProfile = name;
        state.config.active_profile = name;
        return JSON.stringify(state.config);
      },
      create_profile:    async (name) => {
        state.config.profiles[name] = {};
        return JSON.stringify(Object.keys(state.config.profiles));
      },
      test_key:          async (id) => ({ success: true }),
      minimize_to_tray:  async () => {},
    }
  };
}
