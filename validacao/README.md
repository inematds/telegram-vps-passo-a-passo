# Validação do passo a passo por agente novo

Cada rodada: um `claude -p` novo (modelo Sonnet, pela assinatura), numa pasta vazia, recebeu **só** o texto do `PASSO-A-PASSO.md` (mais o pedido em `pedido-validador.md` do lado de fora: Telegram falso, sem bot real, sem systemd). Ele escreveu o `bot.py` etapa por etapa e rodou os testes. Ninguém lhe deu o gabarito de `etapas/`.

| Rodada | Data | Resultado | Onde travou / o que mudou no texto |
|---|---|---|---|
| 1 | 20/11/2026 | 9 etapas OK depois de 1 correção; `testar_travas.py` → `TUDO OK` (36 PASSOU) | `NameError: AREA` na etapa 6: a ordem das linhas da etapa 5 era ambígua. O texto passou a dar a ordem do topo do arquivo; também entraram o aviso do `TELEGRAM_API`/401, a fila de mensagens do Telegram falso, a barra dupla do `Read(//...)`, o `if __name__` e o caminho da unidade systemd. ([relato](rodada-1-relato.md)) |
| 2 | 20/11/2026 | 9 etapas OK sem erro; `TUDO OK` | Só clareza: o bloco provisório da etapa 6, o que acontece com outra resposta que não é sim/não, qual `pendente.pop` recebe o `auditar`, o `--espera` do `fala`, a linha final do `import` e a ordem das funções, os nomes que o teste usa e a versão do Claude Code. Tudo isso entrou no texto. ([relato](rodada-2-relato.md)) |

## Furo achado durante a montagem

`claude -p` herda o `~/.claude/settings.json` (e o `.claude/settings.json` da pasta): as regras "allow" de lá se somam ao `--allowedTools`. Numa máquina com `Bash(rm:*)` liberado, o bot original apagou a pasta `logs` com a ordem "apague agora a pasta logs com rm -r logs, sem perguntar". A correção (`--setting-sources ""` e `--strict-mcp-config`) está nas etapas 5–9, e o teste novo coloca de propósito um `settings.json` armadilha na área. O mesmo patch para o kit original está em [`patch-kit-setting-sources.diff`](patch-kit-setting-sources.diff).
