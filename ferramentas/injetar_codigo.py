#!/usr/bin/env python3
"""Põe o código de cada etapa DENTRO do guia (PT/EN/ES): uma linha curl para baixar o bot.py pronto
da etapa e um <details> com o arquivo inteiro. Lê sempre de etapas/NN-*/bot.py (fonte única).

uso: python3 ferramentas/injetar_codigo.py   (na raiz do repo; pode rodar de novo: refaz os blocos)
"""
import html, os, re

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RAW = "https://raw.githubusercontent.com/inematds/telegram-vps-passo-a-passo/main/etapas/{}/bot.py"
BLOB = "https://github.com/inematds/telegram-vps-passo-a-passo/blob/main/etapas/{}/bot.py"
TXT = {
    "index.html": ("Quer pular a digitação? Baixe o <code>bot.py</code> pronto desta etapa (substitui o seu):",
                   "Código desta etapa (bot.py completo)", "ver no GitHub"),
    "en/index.html": ("Want to skip the typing? Download this step's finished <code>bot.py</code> (it replaces yours):",
                      "Code for this step (full bot.py)", "view on GitHub"),
    "es/index.html": ("¿Quieres saltarte la escritura? Descarga el <code>bot.py</code> listo de esta etapa (reemplaza el tuyo):",
                      "Código de esta etapa (bot.py completo)", "ver en GitHub"),
}
VELHO = re.compile(r'<p class="gab">[^<]*<a href="' + re.escape(BLOB.format("X")).replace("X", r"(\d\d-[^/\"]+)")
                   + r'"[^>]*>[^<]*</a></p>')
BLOCO = re.compile(r'<!-- codigo:(\d\d-[^ ]+) -->.*?<!-- /codigo -->', re.S)


def bloco(etapa, txt):
    codigo = open(os.path.join(RAIZ, "etapas", etapa, "bot.py")).read()
    return (f'<!-- codigo:{etapa} -->\n    <p class="gab">{txt[0]}</p>\n'
            f'<pre>curl -fsSLo bot.py {RAW.format(etapa)}</pre>\n'
            f'    <details class="cod"><summary>{txt[1]}</summary>'
            f'<pre>{html.escape(codigo, quote=False)}</pre>'
            f'<p class="gab"><a href="{BLOB.format(etapa)}" target="_blank" rel="noopener">{txt[2]}</a></p></details>\n'
            f'    <!-- /codigo -->')


for arq, txt in TXT.items():
    p = os.path.join(RAIZ, "guia", arq)
    s = open(p).read()
    s, n1 = VELHO.subn(lambda m: bloco(m.group(1), txt), s)
    s, n2 = BLOCO.subn(lambda m: bloco(m.group(1), txt), s)
    open(p, "w").write(s)
    print(arq, "blocos novos:", n1, "refeitos:", n2)
