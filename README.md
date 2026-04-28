<img width="1084" height="691" alt="Captura de tela 2026-04-21 222533" src="https://github.com/user-attachments/assets/d9768bf7-f3da-49e6-8b3f-bb55f6b09d33" />
# ⌨️ NumDeck

> Transforme qualquer teclado numérico USB em um deck de atalhos personalizado — sem hardware extra, sem Stream Deck, sem mensalidade.

```
┌─────────────┬──────────────┬─────────────┬─────────────┐
│  NumLock    │  / Alterna   │  * Commit   │  - Ctrl+V   │
│  Liga/Desl  │     Modo     │  GitHub DT  │             │
├─────────────┼──────────────┼─────────────┼─────────────┤
│ 7 Terminal  │  8 Run Code  │  9 Docker   │             │
│    ADM      │   VSCode     │             │  + Ctrl+C   │
├─────────────┼──────────────┼─────────────┤             │
│  4 Deezer   │  5 Obsidian  │   6 Edge    │             │
├─────────────┼──────────────┼─────────────┼─────────────┤
│  1 VSCode   │  2 Google    │ 3 WhatsApp  │             │
├─────────────┴──────────────┼─────────────┤    Enter    │
│       0 Alt+Tab            │ Del Print   │   Meu App   │
│                            │  + Ctrl+C   │             │
└────────────────────────────┴─────────────┴─────────────┘
                  BackSpace = Gerenciador de Tarefas
```

---

## 📋 Índice

- [O que é o NumDeck](#o-que-é-o-numdeck)
- [Como funciona — visão geral](#como-funciona--visão-geral)
- [Pré-requisitos](#pré-requisitos)
- [Instalação](#instalação)
- [Estrutura de arquivos](#estrutura-de-arquivos)
- [Fluxo de execução](#fluxo-de-execução)
- [Como o teclado é identificado](#como-o-teclado-é-identificado)
- [Mapeamento das teclas](#mapeamento-das-teclas)
- [Tipos de ação disponíveis](#tipos-de-ação-disponíveis)
- [Sistema de perfis](#sistema-de-perfis)
- [A interface — HTML/CSS/JS](#a-interface--htmlcssjs)
- [A ponte Python ↔ JavaScript](#a-ponte-python--javascript)
- [Como salvar e editar ações](#como-salvar-e-editar-ações)
- [Log de atividade](#log-de-atividade)
- [Bandeja do sistema](#bandeja-do-sistema)
- [Gerar executável .exe](#gerar-executável-exe)
- [Solução de problemas](#solução-de-problemas)
- [Roadmap](#roadmap)

---

## O que é o NumDeck

O NumDeck é um app desktop para Windows que intercepta eventos de um **teclado numérico USB externo** e os transforma em atalhos configuráveis — abrir programas, executar scripts, enviar combinações de teclas, tirar screenshots e mais.

A interface é construída em **HTML + CSS + JavaScript** e renderizada por dentro de uma **janela nativa do Windows** via `pywebview`, ou seja, nenhum browser abre. Para o usuário, parece um `.exe` comum.

O backend é inteiramente em **Python**, responsável por capturar o hardware, executar as ações e salvar as configurações em JSON.

---

## Como funciona — visão geral

```
┌─────────────────────────────────────────────────────────────┐
│                        USUÁRIO                              │
│            Pressiona uma tecla no numpad físico             │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                     listener.py                             │
│  Captura o evento HID/raw input SOMENTE do numpad USB       │
│  Ignora completamente o teclado embutido do notebook        │
└────────────────────────────┬────────────────────────────────┘
                             │  key_id  ex: "KP_8"
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                       api.py                                │
│  handle_key_press(key_id)                                   │
│  → Lê o perfil ativo no config_manager                      │
│  → Descobre qual ação está mapeada para essa tecla          │
│  → Chama actions.execute(action)                            │
│  → Notifica o JS para animar a tecla na interface           │
└───────────────┬─────────────────────────┬───────────────────┘
                │                         │
                ▼                         ▼
┌──────────────────────┐    ┌─────────────────────────────────┐
│     actions.py       │    │           interface/             │
│  Executa a ação:     │    │  onKeyPressed("KP_8")           │
│  - Abre app          │    │  → Tecla pisca/anima na tela    │
│  - Atalho teclado    │    │  → Log de atividade atualiza    │
│  - Abre URL          │    └─────────────────────────────────┘
│  - Terminal ADM      │
│  - Screenshot        │
│  - Digita texto      │
└──────────────────────┘
```

---

## Pré-requisitos

| Requisito | Versão mínima |
|---|---|
| Windows | 10 ou 11 |
| Python | 3.10+ |
| Teclado numérico USB | Qualquer modelo HID padrão |

> O app foi desenvolvido e testado com o **Exbom BK-18** mas funciona com qualquer numpad USB genérico que não precise de driver proprietário.

---

## Instalação

**1. Clone o repositório**

```bash
git clone https://github.com/seu-usuario/numpad-deck.git
cd numpad-deck
```

**2. Crie um ambiente virtual (recomendado)**

```bash
python -m venv venv
venv\Scripts\activate
```

**3. Instale as dependências**

```bash
pip install -r requirements.txt
```

**4. Conecte o teclado numérico USB**

Certifique-se de que o numpad está plugado antes de iniciar o app.

**5. Execute**

```bash
python main.py
```

A janela do NumDeck abre automaticamente com o layout do seu teclado já configurado.

---

## Estrutura de arquivos

```
numpad-deck/
│
├── main.py              # Ponto de entrada — inicia janela, listener e tray
├── api.py               # Ponte Python ↔ JavaScript (métodos expostos ao JS)
├── listener.py          # Captura eventos do numpad USB
├── actions.py           # Executa cada tipo de ação
├── config_manager.py    # Leitura e escrita de configurações JSON
├── tray.py              # Ícone na bandeja do sistema (systray)
├── requirements.txt     # Dependências Python
│
├── config/
│   └── profiles.json    # Perfis e ações de cada tecla (editável)
│
└── interface/
    ├── index.html       # Estrutura da tela
    ├── style.css        # Todo o visual
    └── app.js           # Lógica de UI e comunicação com Python
```

---

## Fluxo de execução

Ao rodar `python main.py`, os seguintes passos acontecem em ordem:

### 1. `main.py` — Orquestrador

```
main.py
 ├── Instancia ConfigManager   → carrega profiles.json
 ├── Instancia Api             → registra métodos que o JS vai chamar
 ├── Cria janela pywebview     → aponta para interface/index.html
 │    └── Motor: Edge (WebView2) embutido no Windows
 ├── Inicia NumpadListener     → thread separada, escuta o hardware
 └── Inicia bandeja (pystray)  → thread separada, ícone no systray
```

### 2. Interface carrega (`index.html` → `app.js`)

```
app.js
 ├── Aguarda evento "pywebviewready"
 ├── Chama api.get_config()         → recebe JSON com todas as teclas
 ├── renderAllKeys()                → aplica cor/ícone/label em cada tecla
 ├── updateProfileSelector()        → mostra perfil ativo no header
 └── selectKey("KP_1")             → abre painel de config da primeira tecla
```

### 3. Tecla física pressionada

```
Hardware → listener.py
              └── on_key_press("KP_8")
                    ├── api.notify_key_pressed("KP_8")   → JS anima tecla
                    └── api.handle_key_press("KP_8")
                          ├── Lê config da tecla no perfil ativo
                          ├── Tipo "toggle"?        → liga/desliga deck
                          ├── Tipo "profile_switch"? → troca perfil, avisa JS
                          └── Outros tipos?          → actions.execute(cfg)
                                                           em thread separada
```

### 4. Usuário edita uma tecla na interface

```
Usuário clica em uma tecla visual
  → selectKey(keyId)           → preenche painel lateral com dados atuais

Usuário muda cor/ícone/tipo
  → preview em tempo real      → JS atualiza visual da tecla sem salvar

Usuário clica "Salvar"
  → saveKey()                  → coleta campos do painel
  → api.save_key(keyId, data)  → Python grava em profiles.json
  → renderAllKeys()            → interface reflete as mudanças
  → showToast("✓ Salvo!")
```

---

## Como o teclado é identificado

Um dos maiores desafios é **distinguir o numpad USB do teclado embutido do notebook**, já que ambos mandam eventos para o Windows.

O `listener.py` usa duas estratégias em cascata:

### Estratégia 1 — pywinusb (preferida)

Enumera todos os dispositivos HID conectados e filtra pelo numpad:

```python
# Prioridade 1: nome contém "numpad", "numeric", "exbom"…
for dev in devices:
    if any(k in dev.product_name.lower() for k in keywords):
        return dev

# Prioridade 2: pega o segundo teclado HID (USB externo)
keyboards = [d for d in devices if d.usage_page == 1 and d.usage == 6]
if len(keyboards) > 1:
    return keyboards[-1]
```

Quando o dispositivo é encontrado, o listener registra um **handler de dados brutos HID** que só é chamado para aquele dispositivo específico. O teclado do notebook não interfere.

### Estratégia 2 — Scan codes (fallback)

Se o pywinusb não identificar o dispositivo, o listener usa a biblioteca `keyboard` e filtra pelos **scan codes exclusivos do numpad físico**:

```python
NUMPAD_SCAN_CODES = {
    69: "KP_NUMLOCK",
    53: "KP_DIVIDE",
    55: "KP_MULTIPLY",
    74: "KP_MINUS",
    71: "KP_7",  72: "KP_8",  73: "KP_9",
    78: "KP_PLUS",
    75: "KP_4",  76: "KP_5",  77: "KP_6",
    14: "KP_BACKSPACE",
    79: "KP_1",  80: "KP_2",  81: "KP_3",
    28: "KP_ENTER",
    82: "KP_0",  83: "KP_DOT",
}
```

Os scan codes das teclas numéricas do numpad são diferentes dos números na linha superior do teclado, portanto a filtragem funciona mesmo sem isolar o dispositivo.

---

## Mapeamento das teclas

Cada tecla do numpad tem um `key_id` interno usado em todo o sistema:

| Tecla física | key_id | Ação padrão (Dev Mode) |
|---|---|---|
| NumLock | `KP_NUMLOCK` | Liga/Desliga o deck |
| / | `KP_DIVIDE` | Alterna perfil |
| * | `KP_MULTIPLY` | Commit GitHub Desktop |
| - | `KP_MINUS` | Ctrl+V |
| 7 | `KP_7` | Terminal Administrador |
| 8 | `KP_8` | Run Code (F5 no VSCode) |
| 9 | `KP_9` | Docker Desktop |
| + | `KP_PLUS` | Ctrl+C |
| 4 | `KP_4` | Deezer |
| 5 | `KP_5` | Obsidian |
| 6 | `KP_6` | Microsoft Edge |
| Backspace | `KP_BACKSPACE` | Gerenciador de Tarefas |
| 1 | `KP_1` | VSCode |
| 2 | `KP_2` | Google Chrome |
| 3 | `KP_3` | WhatsApp |
| Enter | `KP_ENTER` | Meu App (customizável) |
| 0 | `KP_0` | Alt+Tab |
| . Del | `KP_DOT` | Print Screen + Copiar |

> Os `key_id`s são as chaves usadas no `profiles.json`. Você pode alterar qualquer mapeamento pelo arquivo JSON ou pela interface visual.

---

## Tipos de ação disponíveis

Cada tecla suporta um dos seguintes tipos, definidos no campo `"type"` do JSON:

### `open_app`
Abre um executável. Suporta variáveis de ambiente do Windows.

```json
{
  "type": "open_app",
  "value": "%LOCALAPPDATA%\\Programs\\Microsoft VS Code\\Code.exe"
}
```

Comandos simples que estão no PATH também funcionam:
```json
{ "type": "open_app", "value": "code" }
```

### `open_url`
Abre uma URL no browser padrão do sistema.

```json
{ "type": "open_url", "value": "https://www.google.com" }
```

### `shortcut`
Envia uma combinação de teclas usando a biblioteca `keyboard`.

```json
{ "type": "shortcut", "value": "ctrl+shift+esc" }
```

Exemplos válidos: `ctrl+c`, `f5`, `alt+tab`, `ctrl+shift+m`, `windows+d`

### `text`
Digita um texto no campo ou aplicativo ativo no momento.

```json
{ "type": "text", "value": "console.log('debug');" }
```

Útil para snippets de código, comandos recorrentes, templates.

### `terminal_admin`
Abre o Windows Terminal (ou PowerShell) como **Administrador** via `ShellExecuteW` com o verbo `runas`. Não requer valor.

```json
{ "type": "terminal_admin", "value": "" }
```

### `screenshot`
Ativa a ferramenta de recorte do Windows (`Win+Shift+S`). A seleção é automaticamente copiada para a área de transferência.

```json
{ "type": "screenshot", "value": "" }
```

### `profile_switch`
Alterna para o próximo perfil da lista circular. Usado na tecla `/` por padrão.

```json
{ "type": "profile_switch", "value": "" }
```

### `toggle`
Liga ou desliga o deck inteiro. Usado no `NumLock` por padrão. Quando desligado, nenhuma tecla executa ação (exceto o próprio `NumLock` para religar).

```json
{ "type": "toggle", "value": "" }
```

---

## Sistema de perfis

Os perfis permitem ter **conjuntos de atalhos diferentes** para contextos diferentes, alternáveis com uma tecla física.

### Estrutura no JSON

```json
{
  "active_profile": "Dev Mode",
  "profiles": {
    "Dev Mode": {
      "KP_1": { "name": "VSCode", "type": "open_app", ... },
      "KP_2": { "name": "Google", "type": "open_url", ... }
    },
    "Stream Mode": {
      "KP_1": { "name": "OBS Cena 1", "type": "shortcut", ... },
      "KP_2": { "name": "Mute Mic",   "type": "shortcut", ... }
    }
  }
}
```

### Alternância de perfil

- **Pela interface:** clique no seletor de perfil no header
- **Pelo numpad:** pressione a tecla `/` (configurada como `profile_switch`)
- **Criar novo:** botão "+ Novo Perfil" no dropdown ou via `config_manager.create_profile("nome")`

Ao trocar de perfil, a interface inteira re-renderiza com as cores, ícones e labels do novo perfil, e o footer atualiza.

---

## A interface — HTML/CSS/JS

A interface roda dentro de uma janela `pywebview` que usa o motor **Edge/WebView2** já presente no Windows 10/11. Nenhum browser externo é aberto.

### `index.html`
Estrutura estática da tela. Cada tecla é um `<div class="key">` com `data-key="KP_X"` e um `id="key-KP_X"` para acesso direto pelo JavaScript. Teclas duplas (+ e Enter) usam a classe `.key-tall`; o zero usa `.key-wide`.

### `style.css`
Todo o visual. Pontos importantes:

- **Variáveis CSS** (`--blue`, `--green`, etc.) centralizam as cores. Mudar uma variável atualiza todas as teclas daquela cor.
- **Classes de cor** (`.color-blue`, `.color-green`, …) são aplicadas dinamicamente pelo JS ao renderizar cada tecla.
- **`.key.pressed`** dispara a animação de pressão via `@keyframes keyPress`.
- **`.numpad-frame.disabled`** escurece todas as teclas e exibe overlay "DECK DESLIGADO" via CSS puro.

### `app.js`
Responsável por toda a lógica da interface. Funções principais:

| Função | O que faz |
|---|---|
| `loadConfig()` | Chama Python e armazena a config no estado local |
| `renderAllKeys()` | Aplica visual em todas as 18 teclas conforme a config |
| `selectKey(keyId)` | Marca a tecla como selecionada e preenche o painel |
| `saveKey()` | Coleta o formulário e chama `api.save_key()` no Python |
| `clearKey()` | Reseta a tecla para o estado vazio |
| `testCurrentKey()` | Executa a ação sem precisar pressionar o numpad |
| `setColor(dot)` | Preview em tempo real + armazena cor pendente |
| `setIcon(span)` | Preview em tempo real + armazena ícone pendente |
| `flashKey(keyId)` | Anima a tecla (chamado pelo Python via `evaluate_js`) |
| `addLog(name, detail)` | Adiciona entrada no log de atividade |
| `showToast(msg, type)` | Notificação flutuante temporária |

---

## A ponte Python ↔ JavaScript

A comunicação é feita diretamente via `pywebview`, sem WebSocket ou HTTP.

### JS chamando Python

```javascript
// No app.js
const result = await window.pywebview.api.save_key("KP_8", actionData);
```

Qualquer método público da classe `Api` em `api.py` fica automaticamente disponível como `window.pywebview.api.metodo()`.

### Python chamando JS

```python
# No api.py
def _notify_js(self, fn_name: str, data):
    payload = json.dumps(data)
    self._window.evaluate_js(f"{fn_name}({payload})")
```

Funções globais definidas no `app.js` podem ser chamadas pelo Python:

| Python chama | JS executa | Quando |
|---|---|---|
| `onKeyPressed("KP_8")` | Anima a tecla na tela | Toda vez que uma tecla física é pressionada |
| `onDeckToggle(false)` | Escurece o deck inteiro | NumLock pressionado |
| `onProfileSwitch(config)` | Re-renderiza todas as teclas | Tecla `/` pressionada |

---

## Como salvar e editar ações

### Pela interface (recomendado)

1. Clique na tecla que deseja configurar no layout visual
2. O painel lateral exibe os dados atuais
3. Altere nome, tipo, valor, ícone ou cor
4. As mudanças de cor e ícone aparecem **em tempo real** na tecla
5. Clique em **Salvar** — o Python grava no `profiles.json` imediatamente

### Diretamente no JSON

O arquivo `config/profiles.json` pode ser editado em qualquer editor de texto. Exemplo de entrada:

```json
"KP_8": {
  "name": "Run Code",
  "type": "shortcut",
  "value": "f5",
  "icon": "▶",
  "color": "green"
}
```

Ao reiniciar o app, a nova configuração é carregada automaticamente.

---

## Log de atividade

O log exibe as últimas 8 ações executadas, com timestamp, nome da ação e contexto. É atualizado em tempo real toda vez que:

- Uma tecla física é pressionada
- Uma tecla é testada pela interface
- Um perfil é alterado

O log é **apenas visual** — não é persistido entre sessões.

---

## Bandeja do sistema

O app roda em background com um ícone na bandeja do Windows (`tray.py` via `pystray`).

| Ação | Resultado |
|---|---|
| Clicar no ícone | Abre a janela |
| Clicar em "Abrir NumDeck" | Abre a janela |
| Clicar em "Sair" | Encerra o processo |
| Fechar a janela (X) | Minimiza para a bandeja (não encerra) |

---

## Gerar executável .exe

Para distribuir o app sem precisar do Python instalado:

```bash
pip install pyinstaller

pyinstaller \
  --onefile \
  --windowed \
  --name NumDeck \
  --add-data "interface;interface" \
  --add-data "config;config" \
  main.py
```

O executável gerado fica em `dist/NumDeck.exe`. Para adicionar ícone customizado:

```bash
--icon=icon.ico
```

---

## Solução de problemas

**O numpad não é reconhecido**

O listener cai automaticamente para o modo fallback por scan codes. Se as teclas ainda não funcionarem, verifique se o numpad é detectado pelo Windows em `Gerenciador de Dispositivos > Teclados`.

**As teclas do numpad acionam coisas no notebook também**

Isso acontece no modo fallback quando o NumLock está ativo em ambos os teclados. Deixe o NumLock **ativo** no numpad USB e **inativo** no teclado do notebook. O app lida com isso automaticamente quando usa pywinusb.

**Terminal ADM não abre**

O Windows exibe um prompt de UAC pedindo confirmação de administrador. Isso é comportamento esperado — clique em "Sim".

**A janela não abre / tela preta**

O `pywebview` depende do WebView2 Runtime. No Windows 11 já vem instalado. No Windows 10, baixe em: [https://developer.microsoft.com/microsoft-edge/webview2](https://developer.microsoft.com/microsoft-edge/webview2)

**Erro ao instalar `pywinusb`**

```bash
pip install pywinusb --pre
```

Se persistir, o app funciona normalmente sem ele usando o modo fallback.

---

## Roadmap

- [ ] Suporte a macros sequenciais (múltiplas ações por tecla)
- [ ] Integração com OBS via WebSocket
- [ ] Importar/exportar perfis como `.json`
- [ ] Teclas com duplo toque (tap vs hold)
- [ ] Suporte a múltiplos numpads simultaneamente
- [ ] Modo escuro / claro alternável na interface
- [ ] Notificações nativas do Windows ao trocar perfil

---

<div align="center">
  Feito com Python + pywebview · Windows 10/11
</div>
