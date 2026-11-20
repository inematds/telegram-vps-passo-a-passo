# Telegram VPS remoto — passo a passo

[![Bot na sua VPS — passo a passo](guia/assets/banner.jpg)](https://inematds.github.io/telegram-vps-passo-a-passo/guia/)

**🇧🇷 [Português](README.md) · 🇺🇸 [English](README.en.md) · 🇪🇸 [Español](README.es.md)**

## O que é

Um passo a passo para você montar, com as próprias mãos e na sua VPS, um bot de Telegram que passa os seus pedidos para o Claude Code pela sua assinatura. Serve para quem tem uma VPS e quer cuidar dela pelo celular sem dar à IA a chave da casa: só você fala com o bot, a IA só lê, e qualquer mudança espera o seu "sim". São 9 etapas, cada uma com o comando, a saída esperada e um Telegram falso para testar sem bot real. Precisa de uma VPS Linux com Python 3, o Claude Code logado na sua assinatura e uma conta no Telegram.

## 📖 Guia

Guia completo (landing + passo a passo): **https://inematds.github.io/telegram-vps-passo-a-passo/guia/**

- O texto inteiro, com todo o código de cada etapa: [`PASSO-A-PASSO.md`](PASSO-A-PASSO.md) (também em [inglês](PASSO-A-PASSO.en.md) e [espanhol](PASSO-A-PASSO.es.md))
- O `bot.py` pronto de cada etapa (gabarito): [`etapas/`](etapas/)
- O Telegram falso para testar sem bot real: [`ferramentas/telegram_falso.py`](ferramentas/telegram_falso.py)

## Quer que a IA monte com você?

Abra o Claude Code (ou o Codex) na sua VPS e cole:

```
Leia https://github.com/inematds/telegram-vps-passo-a-passo (o PASSO-A-PASSO.md). Vamos montar o bot
juntos, etapa por etapa, na pasta ~/kits/telegram-vps-remoto. Em cada etapa: me explique em linguagem
simples o que muda, rode o teste com o Telegram falso e me mostre a saída comparada com a esperada.
Não ligue nada no systemd nem use meu token real antes de eu dizer sim.
```

---

## O processo, do início ao fim

Quem faz: 🧠 você (na VPS) · ⚙️ script/serviço · 🤖 Claude Code (`claude -p`, chamado pelo bot)

| # | Passo | Comando | Quem |
|---|---|---|---|
| 1 | Conferir Python e Claude Code logado na assinatura | `python3 --version` · `claude -p "responda só: ok" --model haiku` | 🧠 |
| 2 | Criar o bot no @BotFather e guardar o token no `.env` (600) | `chmod 600 .env` | 🧠 |
| 3 | Subir o Telegram falso para testar | `python3 ferramentas/telegram_falso.py servidor` | ⚙️ |
| 4 | Montar o `bot.py` etapa por etapa e testar cada uma | `TELEGRAM_API=http://127.0.0.1:8081 TELEGRAM_BOT_TOKEN=123:falso DONOS=111 python3 bot.py` · `python3 ferramentas/telegram_falso.py fala --de 111 "oi"` | 🧠 |
| 5 | A cada pedido, a IA só lê e propõe | (o bot chama `claude -p` com `--allowedTools` de leitura, `--disallowedTools`, `--permission-mode dontAsk`, `--setting-sources ""`) | 🤖 |
| 6 | O bot confere a proposta e pergunta "Confirma?" | `validar()` no `bot.py` | ⚙️ |
| 7 | Você diz "sim"; o bot executa o que mostrou e anota | `auditoria.jsonl` | 🧠 + ⚙️ |
| 8 | Rodar os testes das travas | `python3 testes/testar_travas.py` → `TUDO OK` | 🧠 |
| 9 | Ligar o bot de vez | `systemctl --user enable --now telegram-vps-remoto` · `loginctl enable-linger "$USER"` | 🧠 + ⚙️ |

## Instalação técnica

**Pré-requisitos:** VPS Linux (testado em Ubuntu 24.04), usuário comum (não root), Python 3.10+, Claude Code logado pela assinatura (Pro/Max, sem `ANTHROPIC_API_KEY`), uma conta no Telegram. Só biblioteca padrão do Python.

**Arquivos**

| Arquivo | O que é |
|---|---|
| `PASSO-A-PASSO.md` | o texto das 9 etapas, com o código que entra em cada uma |
| `etapas/NN-*/bot.py` | o `bot.py` completo no fim de cada etapa |
| `etapas/09-systemd-e-testes/testes/testar_travas.py` | testes das travas (8 chamadas curtas do Claude Code) |
| `etapas/09-systemd-e-testes/systemd/telegram-vps-remoto.service` | unidade systemd de usuário |
| `ferramentas/telegram_falso.py` | imita `getMe`, `getUpdates`, `sendMessage`, `sendChatAction`; `fala` manda mensagem como alguém |
| `validacao/` | relatos do agente novo que seguiu o texto do zero |

**As travas (no código):**

1. `DONOS` vazio recusa todos; o bot anota o `from.id` de quem tentou.
2. A IA roda com `--allowedTools Read(./**) Glob(./**) Grep(./**) Bash(df/ls/free/uptime)`: conteúdo de arquivo só dentro de `area/`; fora dela só espaço em disco e nomes de pastas. `--disallowedTools` nega chaves e logins (`~/.config`, `~/.ssh`, `~/.claude`, `~/.codex`, `~/.aws`, `~/.docker`, `~/.kube`, `~/.gnupg`, `~/.git-credentials`, `~/.netrc`), `~/.bash_history`, todo `.env`, escrita, `sudo`, `curl`, `cat`…; `--permission-mode dontAsk`.
3. `--setting-sources ""` e `--strict-mcp-config`: sem isso, regras "allow" do seu `~/.claude/settings.json` se somam e furam a trava (medido: "apague a pasta logs" apagou).
4. A ação vem num JSON fixo (`--json-schema`); `validar()` aceita só `rm rmdir mv cp mkdir touch gzip gunzip tar`, só opções da lista curta, sem `| ; $ \` < > ~ ..`, todo caminho (com `realpath`) dentro de `area/`.
5. Só `sim`/`s`/`confirmo`/`confirma`/`yes` (ou `pode`/`ok`/`manda`/`faz` sozinhos) confirmam; com `?` nunca, nem com `mas`/`antes`/`primeiro`/`depois`/`espera` ("sim, mas antes faz backup" cancela), nem com negação (`não`/`no`/`not`/`cancela`/`nunca`/`pare`/`para`: "sim, não apaga" cancela). Vale 10 min. Quem executa é o bot, sem shell. `tar -x` é listado antes (recusa `/`, `..`, link).
6. `auditoria.jsonl` guarda cada evento, sem o token. Nenhuma chave `ANTHROPIC_*`/`OPENAI_*`/`OPENROUTER_*`/`TELEGRAM_*` vai para o processo do Claude.

**Testes:** `python3 etapas/09-systemd-e-testes/testes/testar_travas.py` (8 chamadas curtas do Claude Code) usa área e auditoria temporárias, coloca um `settings.json` armadilha que libera `rm` e uma isca com segredo falso fora da área; 50 testes, saída `TUDO OK`. Todos valem na sua VPS: o teste das chaves usa um `.env` falso dentro da área temporária.

**Prova:** a validação está em [`validacao/`](validacao/): um agente novo (Claude Code, modelo Sonnet) recebeu só o texto, montou o bot do zero com o Telegram falso e rodou os testes.

## Lessons

Ver [CLAUDE.md](CLAUDE.md).

---

Feito no [INEMA.CLUB](https://inema.club) — conteúdo aberto e gratuito.
