import os
import sys
import time
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
HORARIO_ENVIO = "05:30"

def buscar_previsao():
    url = "https://api.open-meteo.com/v1/forecast"
    parametros = {
        "latitude": -31.7654,
        "longitude": -52.3376,
        "hourly": "temperature_2m,precipitation_probability,wind_speed_10m",
        "timezone": "America/Sao_Paulo",
        "forecast_days": 1,
    }
    resposta = requests.get(url, params=parametros, timeout=10)
    resposta.raise_for_status()
    return resposta.json()


def pegar_horas_do_treino(dados):
    horas = dados["hourly"]["time"]
    temps = dados["hourly"]["temperature_2m"]
    chuvas = dados["hourly"]["precipitation_probability"]
    ventos = dados["hourly"]["wind_speed_10m"]

    temps_treino = []
    chuvas_treino = []
    ventos_treino = []

    for i in range(len(horas)):
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
        veredito = "🟢 Ótimo dia para correr ou pedalar!"
    elif len(problemas) == 1:
        veredito = "🟡 Dá para ir, mas com atenção."
    else:
        veredito = "🔴 Melhor evitar o treino na rua hoje."

    return veredito, problemas


def enviar_telegram(texto):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    resposta = requests.post(url, json={"chat_id": CHAT_ID, "text": texto}, timeout=10)
    resposta.raise_for_status()


def rodar():
    try:
        dados = buscar_previsao()
        temp_min, temp_max, chuva_max, vento_max = pegar_horas_do_treino(dados)
        veredito, problemas = decidir(temp_min, temp_max, chuva_max, vento_max)

        texto = (
            f"{veredito}\n\n"
            f"📍 Pelotas, das {HORA_INICIO}h às {HORA_FIM}h\n"
            f"🌡️ Temperatura: {temp_min:.0f}°C a {temp_max:.0f}°C\n"
            f"🌧️ Chance de chuva: até {chuva_max:.0f}%\n"
            f"💨 Vento: até {vento_max:.0f} km/h"
        )
        if problemas:
            texto = texto + "\n\n⚠️ Atenção: " + ", ".join(problemas) + "."

    except requests.exceptions.RequestException:
        texto = "⚠️ Não consegui buscar a previsão do tempo hoje."

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