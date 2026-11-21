Trabalho Prático Final: Automação e Programabilidade em Redes
Treinador do Dia: bot de corrida e pedal no Telegram
Automação em Python que, toda noite, consulta a previsão do tempo, lê o meu plano de treinos e me manda no Telegram o treino da manhã seguinte, a rota recomendada e se o clima estará favorável. Se ainda estiver escuro no horário de saída, ele também avisa e indica a rota mais segura.

1. Sobre o Projeto e Problema Resolvido
Eu corro e pedalo na rua, saio cedo (por volta das 5h30) e sigo um plano de treinos que muda todo dia: corrida curta, tiros em subida, pedal, treino longo. Antes de dormir, eu precisava:

lembrar qual seria o treino da manhã seguinte;

decidir por onde ir (cada treino pede um tipo de percurso: plano, com subidas, perto de casa);

abrir o app do tempo para ver chuva, vento e temperatura previstos para a madrugada/manhã;

verificar se ainda estaria escuro no horário da saída, porque no inverno o dia demora a clarear e a rota precisa ser segura.

Este bot junta tudo isso numa única mensagem, enviada sozinha toda noite por volta das 21h15, sem eu precisar abrir nada e sem o meu computador ligado.

Veredito do tempo (olhando as horas do treino da manhã seguinte, das 5h às 8h):

Veredito	Quando acontece
🟢 Ótimo dia	Nenhum problema no tempo
🟡 Dá para ir, com atenção	Um problema (chuva, vento, frio ou calor)
🔴 Melhor evitar	Dois ou mais problemas ao mesmo tempo
Limites usados (podem ser mudados no início do clima_bot.py): chuva acima de 40%, vento acima de 25 km/h, temperatura acima de 28 °C ou abaixo de 8 °C.

Segurança: o bot compara o horário em que eu saio (05:30) com o nascer do sol do dia seguinte. Se o dia ainda não clareou, ele avisa e destaca as rotas marcadas como mais seguras no escuro.

2. Arquitetura e Fluxo de Funcionamento
Etapas do funcionamento:

Início automático: o GitHub Actions executa o programa todos os dias por volta das 21h15 (horário de Brasília), buscando os dados referentes à manhã seguinte (D+1). Também é possível executar o programa manualmente pelo computador.

Consulta dos treinos: o Python abre o arquivo treinos.json para verificar qual atividade está programada para o dia seguinte. Depois, consulta o arquivo rotas.json para encontrar as opções de percurso.

Consulta do tempo: o programa acessa a API Open-Meteo, que fornece a previsão horária (temperatura, chuva e vento) e o horário do nascer do sol para os próximos 2 dias.

Análise das informações: o Python filtra a janela das 5h às 8h de amanhã, compara a previsão com os limites definidos no código e verifica se ainda estará escuro no horário de saída.

Envio da mensagem: depois de organizar todas as informações, o programa envia um resumo completo pelo Telegram.

Requisitos do trabalho e onde estão atendidos:

Requisito	Como foi atendido
Python	clima_bot.py
Duas ou mais integrações	API Open-Meteo (tempo) e API de Bots do Telegram
Tratamento de JSON	Resposta da API Open-Meteo, treinos.json e rotas.json
Credenciais fora do código	Arquivo .env (local) e GitHub Secrets (nuvem)
Gatilho automático	GitHub Actions com agendamento diário (cron)
Tratamento de erros	try/except, timeout, raise_for_status() e tratamento de arquivos JSON ausentes ou inválidos
3. Tecnologias e APIs Utilizadas
Para desenvolver o projeto, foram utilizadas as seguintes ferramentas:

Python 3: linguagem utilizada para desenvolver o programa.

Requests: biblioteca que permite buscar informações em serviços externos pela internet.

Python-dotenv: utilizada para carregar as informações de acesso que ficam no arquivo .env.

Schedule: permite programar o horário de execução quando o programa está rodando continuamente no computador.

JSON: formato utilizado para organizar os dados dos treinos, das rotas e das respostas da API.

GitHub Actions: permite executar o programa automaticamente na nuvem, sem precisar deixar o computador ligado.

GitHub Secrets: utilizado para guardar as informações de acesso (token e chat ID) de forma protegida.

API Open-Meteo: fornece a previsão do tempo e o horário do nascer do sol.

API do Telegram: permite que o programa envie mensagens diretamente para o meu celular.

Organização dos arquivos:

Plaintext
clima-bot/
├── clima_bot.py            # o programa principal
├── treinos.json            # plano de treinos por data
├── rotas.json              # fichas das rotas (relevo, segurança)
├── requirements.txt        # bibliotecas necessárias
├── .env.example            # modelo das credenciais (valores fictícios)
├── .gitignore              # impede o .env de subir para o repositório
└── .github/workflows/
    └── clima.yml           # agendamento no GitHub Actions
Função de cada arquivo:

clima_bot.py: contém o código principal do programa.

treinos.json: guarda os treinos organizados por data.

rotas.json: contém os nomes das rotas e suas características.

requirements.txt: lista as bibliotecas necessárias para executar o projeto.

.env.example: apresenta um modelo das informações de acesso.

.gitignore: impede que arquivos com informações privadas sejam enviados ao GitHub.

clima.yml: configura o horário de execução automática na nuvem.

Exemplo dos arquivos de dados:

No arquivo treinos.json, ficam registrados os treinos de cada dia:

JSON
{
  "data": "2026-11-20",
  "treino": "Tiros: 2 km de aquecimento + 10x100 m em subida + 2 km de desaquecimento",
  "icone": "⚡",
  "rotas": ["sprints_quartier", "sprints_una"]
}
Já no arquivo rotas.json, ficam as informações sobre os percursos:

JSON
"sprints_una": {
  "nome": "Região do Una",
  "relevo": "percurso com subidinhas",
  "seguro_no_escuro": true
}
Uma vantagem dessa organização é que posso alterar os treinos e as rotas diretamente nos arquivos JSON, sem precisar modificar o código principal do programa.

4. Pré-requisitos e Como Executar
Para utilizar o projeto, é necessário ter o Python 3.9 ou superior instalado e possuir uma conta no Telegram.

Passo 1 – Criar o bot no Telegram

Abrir o Telegram e procurar por @BotFather.

Enviar o comando /newbot.

Escolher um nome e um usuário para o bot. Após a criação, o Telegram fornecerá um token de acesso.

Abrir a conversa com o bot criado e enviar uma mensagem, como "oi".

Consultar o endereço abaixo no navegador, substituindo pelo token recebido:[https://api.telegram.org/botSEU_TOKEN/getUpdates](https://api.telegram.org/botSEU_TOKEN/getUpdates)

Nessa consulta, localizar o número chamado chat id, que identifica a conversa que receberá as mensagens.

Passo 2 – Baixar e configurar

Bash
git clone https://github.com/luaanasouza/clima-bot.git
cd clima-bot
python -m venv venv
Ativar o ambiente virtual:

Bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
Instalar as bibliotecas:

Bash
pip install -r requirements.txt
Criar o arquivo .env a partir do modelo .env.example:

Bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
Abrir o arquivo .env e preencher as informações do TELEGRAM_BOT_TOKEN e do TELEGRAM_CHAT_ID.

Passo 3 – Executar no computador

Para testar o funcionamento uma única vez (buscando o treino de amanhã):

Bash
python clima_bot.py --agora
Para deixar o programa executando e enviando as mensagens diariamente às 21h00:

Bash
python clima_bot.py
Também é possível testar o treino de uma data específica no Windows:

Bash
set DATA_TESTE=2026-11-20
python clima_bot.py --agora
Passo 4 – Configurar a execução automática pelo GitHub

Enviar os arquivos do projeto para o repositório no GitHub, sem incluir o arquivo .env.

Acessar Settings > Secrets and variables > Actions e criar duas chaves:

TELEGRAM_BOT_TOKEN

TELEGRAM_CHAT_ID

O arquivo clima.yml já contém a configuração para executar o programa diariamente. O horário configurado é 15 0 * * *, que corresponde às 21h15 no horário de Brasília (UTC−3), pois o GitHub utiliza o fuso horário UTC. A escolha desse horário noturno evita o congestionamento da fila gratuita nas primeiras horas da manhã e garante o planejamento antecipado para o dia seguinte.

Também é possível iniciar uma execução manualmente pela opção: Actions > Clima Bot > Run workflow.

Segurança das informações:
O token do Telegram e o chat ID são credenciais sensíveis. Por isso, ficam armazenados no arquivo .env durante os testes locais e nos GitHub Secrets quando o programa é executado na nuvem, evitando exposição no código-fonte público.

5. Demonstração (Resultados)
(Inserir aqui as capturas de tela demo-telegram.png e demo-actions.png)

Mensagem recebida no Telegram: exibe o veredito climático, o treino de amanhã, a rota recomendada, o aviso de segurança caso ainda esteja escuro e os dados meteorológicos das 5h às 8h.

Execução automática pelo GitHub Actions: histórico comprovando os disparos agendados (Scheduled) concluídos com sucesso na nuvem.

Quando não existe treino cadastrado para o dia seguinte, o bot envia a mensagem:

"😴 Amanhã não há treino no plano."

6. Melhorias Futuras e Limitações
Melhorias futuras:

Consultar uma API de elevação para identificar melhor as subidas e descidas de cada rota.

Criar um histórico em arquivo CSV para acompanhar as condições do tempo nos dias de treino.

Permitir que os treinos sejam cadastrados em uma planilha integrada, facilitando a atualização do planejamento.

Limitações atuais:

Os treinos e as informações de segurança das rotas precisam ser cadastrados manualmente nos arquivos JSON.

O GitHub Actions (plano gratuito) pode apresentar pequenas variações de minutos no horário programado devido à fila compartilhada.

Caso o repositório fique 60 dias sem alterações, o GitHub suspende o agendamento automático por inatividade, sendo necessário reativá-lo na aba Actions.
