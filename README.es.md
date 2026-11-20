# Telegram VPS remoto — paso a paso

[![Bot en tu VPS — paso a paso](guia/assets/banner-es.jpg)](https://inematds.github.io/telegram-vps-passo-a-passo/guia/es/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## Qué es

Una guía paso a paso para que montes, con tus propias manos y en tu VPS, un bot de Telegram que transmite tus pedidos a Claude Code mediante tu suscripción. Es para quienes tienen una VPS y quieren administrarla desde el celular sin darle a la IA la llave de casa: solo tú hablas con el bot, la IA solo lee y cualquier cambio espera tu «sí». Son 9 etapas, cada una con el comando, el resultado esperado y un Telegram falso para probar sin un bot real. Necesitas una VPS Linux con Python 3, Claude Code con la sesión iniciada mediante tu suscripción y una cuenta de Telegram.

## 📖 Guía

Guía completa (landing + paso a paso): **https://inematds.github.io/telegram-vps-passo-a-passo/guia/es/**

- El texto completo, con todo el código de cada etapa: [`PASSO-A-PASSO.md`](PASSO-A-PASSO.md) (en portugués)
- El `bot.py` listo de cada etapa (solución): [`etapas/`](etapas/)
- El Telegram falso para probar sin un bot real: [`ferramentas/telegram_falso.py`](ferramentas/telegram_falso.py)

## ¿Quieres que la IA lo monte contigo?

Abre Claude Code (o Codex) en tu VPS y pega:

```
Lee https://github.com/inematds/telegram-vps-passo-a-passo (el archivo PASSO-A-PASSO.md, en portugués). Vamos a montar el bot
juntos, etapa por etapa, en la carpeta ~/kits/telegram-vps-remoto. En cada etapa: explícame en lenguaje
sencillo qué cambia, ejecuta la prueba con el Telegram falso y muéstrame el resultado comparado con el esperado.
No conectes nada a systemd ni uses mi token real antes de que te diga que sí.
```

---

## El proceso, de principio a fin

Quién lo hace: 🧠 tú (en la VPS) · ⚙️ script/servicio · 🤖 Claude Code (`claude -p`, llamado por el bot)

| # | Paso | Comando | Quién |
|---|---|---|---|
| 1 | Comprobar Python y que Claude Code haya iniciado sesión con la suscripción | `python3 --version` · `claude -p "responda só: ok" --model haiku` | 🧠 |
| 2 | Crear el bot en @BotFather y guardar el token en `.env` (600) | `chmod 600 .env` | 🧠 |
| 3 | Iniciar el Telegram falso para probar | `python3 ferramentas/telegram_falso.py servidor` | ⚙️ |
| 4 | Armar el `bot.py` etapa por etapa y probar cada una | `TELEGRAM_API=http://127.0.0.1:8081 TELEGRAM_BOT_TOKEN=123:falso DONOS=111 python3 bot.py` · `python3 ferramentas/telegram_falso.py fala --de 111 "oi"` | 🧠 |
| 5 | En cada pedido, la IA solo lee y propone | (el bot llama a `claude -p` con `--allowedTools` de lectura, `--disallowedTools`, `--permission-mode dontAsk`, `--setting-sources ""`) | 🤖 |
| 6 | El bot comprueba la propuesta y pregunta «¿Confirmas?» | `validar()` en `bot.py` | ⚙️ |
| 7 | Tú dices «sí»; el bot ejecuta lo que mostró y lo registra | `auditoria.jsonl` | 🧠 + ⚙️ |
| 8 | Ejecutar las pruebas de las restricciones | `python3 testes/testar_travas.py` → `TUDO OK` | 🧠 |
| 9 | Poner en marcha el bot definitivamente | `systemctl --user enable --now telegram-vps-remoto` · `loginctl enable-linger "$USER"` | 🧠 + ⚙️ |

## Instalación técnica

**Requisitos previos:** VPS Linux (probado en Ubuntu 24.04), usuario normal (no root), Python 3.10+, Claude Code con sesión iniciada mediante la suscripción (Pro/Max, sin `ANTHROPIC_API_KEY`), una cuenta de Telegram. Solo usa la biblioteca estándar de Python.

**Archivos**

| Archivo | Qué es |
|---|---|
| `PASSO-A-PASSO.md` | el texto de las 9 etapas, con el código que se incorpora en cada una (en portugués) |
| `etapas/NN-*/bot.py` | el `bot.py` completo al final de cada etapa |
| `etapas/09-systemd-e-testes/testes/testar_travas.py` | pruebas de las restricciones (5 llamadas cortas a Claude Code) |
| `etapas/09-systemd-e-testes/systemd/telegram-vps-remoto.service` | unidad systemd de usuario |
| `ferramentas/telegram_falso.py` | imita `getMe`, `getUpdates`, `sendMessage`, `sendChatAction`; `fala` envía un mensaje como alguien |
| `validacao/` | informes del agente nuevo que siguió el texto desde cero |

**Las restricciones (en el código):**

1. Si `DONOS` está vacío, se rechazan todos; el bot registra el `from.id` de quien lo intentó.
2. La IA se ejecuta con `--allowedTools Read Glob Grep Bash(df/du/ls/free/uptime/wc)`, `--disallowedTools` para claves, SSH, inicios de sesión, `.env`, escritura, `sudo`, `curl`…, `--permission-mode dontAsk`, confinada en `area/`.
3. `--setting-sources ""` y `--strict-mcp-config`: sin esto, las reglas «allow» de tu `~/.claude/settings.json` se suman y rompen la restricción (medido: «borra la carpeta logs» la borró).
4. La acción se entrega en un JSON fijo (`--json-schema`); `validar()` acepta solo `rm mv cp mkdir touch gzip gunzip tar`, solo opciones de la lista corta, sin `| ; $ \` < > ~ ..`, y todas las rutas (con `realpath`) deben estar dentro de `area/`.
5. Solo `sim`/`s`/`confirmo`/`confirma`/`yes` (o `pode`/`ok`/`manda`/`faz` por sí solos) confirman; si hay un `?`, nunca. Es válido durante 10 min. Quien ejecuta es el bot, sin shell. `tar -x` se enumera antes (rechaza `/`, `..`, enlaces).
6. `auditoria.jsonl` guarda cada evento, sin el token. Ninguna clave `ANTHROPIC_*`/`OPENAI_*`/`OPENROUTER_*`/`TELEGRAM_*` pasa al proceso de Claude.

**Pruebas:** `python3 etapas/09-systemd-e-testes/testes/testar_travas.py` usa un área y una auditoría temporales, y coloca un `settings.json` trampa que permite `rm`; resultado: `TUDO OK`.

**Prueba:** la validación está en [`validacao/`](validacao/): un agente nuevo (Claude Code, modelo Sonnet) recibió solo el texto, montó el bot desde cero con el Telegram falso y ejecutó las pruebas.

## Lessons

Ver [CLAUDE.md](CLAUDE.md).

---

Hecho en [INEMA.CLUB](https://inema.club) — contenido abierto y gratuito.