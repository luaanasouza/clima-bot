import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

import requests
import schedule
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

# Horas do treino e limites (mude à vontade)
HORA_INICIO = 5
HORA_FIM = 8
CHUVA_MAX = 40
VENTO_MAX = 25
TEMP_MIN = 8
TEMP_MAX = 28
HORARIO_ENVIO = "21:00"
SAIDA = "05:30"  # horário em que você costuma sair para treinar

# Pasta onde está este arquivo (os JSON ficam ao lado dele)
PASTA = os.path.dirname(os.path.abspath(__file__))

# Horário de Brasília (UTC-3). O GitHub roda em UTC, então fixamos o fuso aqui
# para o cálculo do dia ser sempre o horário de Pelotas.
FUSO_BRASIL = timezone(timedelta(hours=-3))


def data_alvo():
    # Para testar um dia específico: no terminal, set DATA_TESTE=2026-11-22
    teste = os.getenv("DATA_TESTE")
    if teste:
        return teste
    # Como o envio é à noite (21h), buscamos o treino do dia seguinte (amanhã)
    amanha = datetime.now(FUSO_BRASIL) + timedelta(days=1)
    return amanha.strftime("%Y-%m-%d")


def carregar_json(nome_arquivo):
    """Abre um arquivo .json. Se não existir ou estiver quebrado, devolve None."""
    caminho = os.path.join(PASTA, nome_arquivo)
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            return json.load(arquivo)
    except FileNotFoundError:
        print(f"Aviso: não encontrei o arquivo {nome_arquivo}.")
    except json.JSONDecodeError:
        print(f"Aviso: o arquivo {nome_arquivo} está com erro de escrita (JSON inválido).")
    return None


def esta_escuro(dados, dia_alvo):
    """Compara o horário de saída com o nascer do sol do dia alvo."""
    try:
        for nascer in dados["daily"]["sunrise"]:
            if nascer.startswith(dia_alvo):
                hora_nascer = nascer[11:16]  # fica só "05:34"
                return SAIDA < hora_nascer, hora_nascer
    except (KeyError, IndexError, TypeError):
        pass
    return False, None


def montar_bloco_treino(dia_alvo=None, escuro=False):
    """Procura o treino de amanhã no treinos.json e monta o texto com treino e rota."""
    if dia_alvo is None:
        dia_alvo = data_alvo()

    treinos = carregar_json("treinos.json")
    if not isinstance(treinos, list):
        return ""  # sem plano: o bot manda só a previsão do tempo

    rotas = carregar_json("rotas.json")
    if not isinstance(rotas, dict):
        rotas = {}

    for treino in treinos:
        if treino.get("data") == dia_alvo:
            icone = treino.get("icone", "🏃")
            linhas = [f"{icone} Treino de amanhã: {treino.get('treino', 'Treino')}"]

            fichas = [rotas[r] for r in treino.get("rotas", []) if r in rotas]
            if len(fichas) == 1:
                linhas.append("🗺️ Rota: " + texto_da_rota(fichas[0], escuro))
            elif len(fichas) > 1:
                linhas.append("🗺️ Opções de rota:")
                for ficha in fichas:
                    linhas.append("• " + texto_da_rota(ficha, escuro))

            # Está escuro e nenhuma rota de amanhã é a mais segura: avisa
            if escuro and fichas and not any(f.get("seguro_no_escuro") for f in fichas):
                linhas.append("⚠️ Nenhuma rota de amanhã está marcada como segura no escuro. Considere fazer no Una.")

            return "\n".join(linhas) + "\n\n"

    return "😴 Amanhã não há treino no plano.\n\n"


def texto_da_rota(ficha, escuro=False):
    texto = ficha.get("nome", "Rota")
    if ficha.get("relevo"):
        texto += f" ({ficha['relevo']})"
    if escuro and ficha.get("seguro_no_escuro"):
        texto += " 🌙✅ mais segura no escuro"
    return texto


def buscar_previsao():
    url = "https://api.open-meteo.com/v1/forecast"
    parametros = {
        "latitude": -31.7654,
        "longitude": -52.3376,
        "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
        "timezone": "America/Sao_Paulo",
        "daily": "sunrise",  # hora do nascer do sol
        "forecast_days": 2,  # hoje e amanhã
    }
    resposta = requests.get(url, params=parametros, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def pegar_horas_do_treino(dados, dia_alvo):
    horas = dados["hourly"]["time"]
    temps = dados["hourly"]["temperature_2m"]
    chuvas = dados["hourly"]["precipitation_probability"]
    ventos = dados["hourly"]["wind_speed_10m"]

    temps_treino = []
    chuvas_treino = []
    ventos_treino = []

    for i in range(len(horas)):
        if horas[i].startswith(dia_alvo):
            hora = int(horas[i][11:13])
            if HORA_INICIO <= hora <= HORA_FIM:
                temps_treino.append(temps[i])
                chuvas_treino.append(chuvas[i])
                ventos_treino.append(ventos[i])

    return min(temps_treino), max(temps_treino), max(chuvas_treino), max(ventos_treino)


def decidir(temp_min, temp_max, chuva_max, vento_max):
    problemas = []

    if chuva_max > CHUVA_MAX:
        problemas.append(f"chance de chuva de {chuva_max:.0f}%")
    if vento_max > VENTO_MAX:
        problemas.append(f"vento de até {vento_max:.0f} km/h")
    if temp_max > TEMP_MAX:
        problemas.append(f"calor de até {temp_max:.0f}°C")
    if temp_min < TEMP_MIN:
        problemas.append(f"frio de {temp_min:.0f}°C")

    if len(problemas) == 0:
        veredito = "🟢 Ótimo dia para correr ou pedalar amanhã!"
    elif len(problemas) == 1:
        veredito = "🟡 Dá para ir amanhã, mas com atenção."
    else:
        veredito = "🔴 Melhor evitar o treino na rua amanhã."

    return veredito, problemas


def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    resposta = requests.post(url, json={"chat_id": CHAT_ID, "text": texto}, timeout=10)
    resposta.raise_for_status()


def rodar():
    dia_alvo = data_alvo()
    try:
        dados = buscar_previsao()
        temp_min, temp_max, chuva_max, vento_max = pegar_horas_do_treino(dados, dia_alvo)
        veredito, problemas = decidir(temp_min, temp_max, chuva_max, vento_max)

        escuro, hora_nascer = esta_escuro(dados, dia_alvo)
        aviso_escuro = ""
        if escuro:
            aviso_escuro = (
                f"🌙 Amanhã você sai às {SAIDA} e o sol nasce às {hora_nascer}: "
                f"o dia ainda não clareou. Prefira o Una, que é mais seguro.\n\n"
            )

        texto = (
            f"{veredito}\n\n"
            f"{montar_bloco_treino(dia_alvo=dia_alvo, escuro=escuro)}"
            f"{aviso_escuro}"
            f"📍 Amanhã em Pelotas, das {HORA_INICIO}h às {HORA_FIM}h\n"
            f"🌡️ Temperatura: {temp_min:.0f}°C a {temp_max:.0f}°C\n"
            f"🌧️ Chance de chuva: até {chuva_max:.0f}%\n"
            f"💨 Vento: até {vento_max:.0f} km/h"
        )
        if problemas:
            texto = texto + "\n\n⚠️ Atenção: " + ", ".join(problemas) + "."

    except requests.exceptions.RequestException:
        # Mesmo sem a previsão, o treino de amanhã ainda pode ser avisado
        texto = (
            "⚠️ Não consegui buscar a previsão do tempo para amanhã.\n\n"
            + montar_bloco_treino(dia_alvo=dia_alvo).rstrip()
        ).rstrip()

    try:
        enviar_telegram(texto)
        print("Mensagem enviada!")
    except requests.exceptions.RequestException:
        print("Erro ao enviar para o Telegram.")


if len(sys.argv) > 1 and sys.argv[1] == "--agora":
    rodar()
else:
    schedule.every().day.at(HORARIO_ENVIO).do(rodar)
    print("Bot ligado! Vou enviar todo dia às", HORARIO_ENVIO)
    while True:
        schedule.run_pending()
        time.sleep(30)