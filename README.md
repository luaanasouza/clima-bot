Trabalho Prático Final: Automação e Programabilidade em Redes
Treinador do Dia: bot de corrida e pedal no Telegram
Automação em Python que, todo dia de manhã, consulta a previsão do tempo, lê o meu plano de treinos e me manda no Telegram o treino do dia, a rota e se o tempo está bom. Se ainda estiver escuro, ele também avisa e indica a rota mais segura.

1. Sobre o Projeto e Problema Resolvido
Eu corro e pedalo na rua, saio cedo (por volta das 5h30) e sigo um plano de treinos que muda todo dia: corrida curta, tiros em subida, pedal, treino longo. Antes de sair, eu precisava:
lembrar qual era o treino do dia;
decidir por onde ir (cada treino pede um tipo de percurso: plano, com subidas, perto de casa);
abrir o app do tempo para ver chuva, vento e temperatura;
pensar se ainda estaria escuro, porque no inverno o dia demora a clarear e a rota precisa ser segura.
Este bot junta tudo isso numa única mensagem, enviada sozinha todo dia às 5h30, sem eu precisar abrir nada e sem o meu computador ligado.
Veredito do tempo (olhando só as horas do treino, das 5h às 8h):
Veredito
Quando acontece
🟢 Ótimo dia
Nenhum problema no tempo
🟡 Dá para ir, com atenção
Um problema (chuva, vento, frio ou calor)
🔴 Melhor evitar
Dois ou mais problemas ao mesmo tempo

Limites usados (podem ser mudados no início do clima_bot.py): chuva acima de 40%, vento acima de 25 km/h, temperatura acima de 28 °C ou abaixo de 8 °C.
Segurança: o bot compara o horário em que eu saio com o nascer do sol. Se o dia ainda não clareou, ele avisa e destaca as rotas que eu marquei como mais seguras no escuro.

2. Arquitetura e Fluxo de Funcionamento



Etapas do funcionamento:
1. Início automático: o GitHub Actions executa o programa todos os dias às 5h30, considerando o horário de Brasília. Também é possível executar o programa manualmente pelo computador.
2. Consulta dos treinos: o Python abre o arquivo treinos.json para verificar qual atividade está programada para aquele dia. Depois, consulta o arquivo rotas.json para encontrar as opções de percurso.
3. Consulta do tempo: o programa acessa a API Open-Meteo, que fornece informações sobre temperatura, chuva, vento e horário do nascer do sol.
4. Análise das informações: o Python compara a previsão do tempo com os limites definidos no código e verifica se ainda estará escuro no horário do treino.
5. Envio da mensagem: depois de organizar todas as informações, o programa envia um resumo pelo Telegram.
Requisitos do trabalho e onde estão atendidos:
Requisito
Como foi atendido
Python
clima_bot.py
Duas ou mais integrações
API Open-Meteo (tempo) e API de Bots do Telegram
Tratamento de JSON
resposta da API Open-Meteo, treinos.json e rotas.json
Credenciais fora do código
arquivo .env (local) e GitHub Secrets (nuvem)
Gatilho automático
GitHub Actions com agendamento diário (cron)
Tratamento de erros
try/except, timeout, raise_for_status() e arquivos JSON ausentes ou inválidos


3. Tecnologias e APIs Utilizadas 

Para desenvolver o projeto, foram utilizadas as seguintes ferramentas:
Python 3: linguagem utilizada para desenvolver o programa.
Requests: biblioteca que permite buscar informações em serviços externos pela internet.
Python-dotenv: utilizada para carregar as informações de acesso que ficam no arquivo .env.
Schedule: permite programar o horário de execução quando o programa está rodando no computador.
JSON: formato utilizado para organizar os dados dos treinos, das rotas e das respostas da API.
GitHub Actions: permite executar o programa automaticamente pela internet, sem precisar deixar meu computador ligado.
GitHub Secrets: utilizado para guardar as informações de acesso de forma protegida.
API Open-Meteo: fornece a previsão do tempo e o horário do nascer do sol.
API do Telegram: permite que o programa envie mensagens diretamente para o meu celular.

Organização dos arquivos:

O projeto foi organizado da seguinte maneira:
clima-bot/
├── clima_bot.py            # o programa
├── treinos.json            # plano de treinos por data
├── rotas.json              # fichas das rotas (relevo, segurança)
├── requirements.txt        # bibliotecas necessárias
├── .env.example            # modelo das credenciais (valores de mentira)
├── .gitignore              # impede o .env de subir
└── .github/workflows/
    └── clima.yml           # agendamento no GitHub Actions
 Cada arquivo possui uma função:
clima_bot.py: contém o código principal do programa.
treinos.json: guarda os treinos organizados por data.
rotas.json: contém os nomes das rotas e suas características.
requirements.txt: lista as bibliotecas necessárias para executar o projeto.
.env.example: apresenta um modelo das informações de acesso.
.gitignore: impede que arquivos com informações privadas sejam enviados ao GitHub.
clima.yml: configura o horário de execução automática.
Exemplo dos arquivos de dados:

No arquivo treinos.json, ficam registrados os treinos de cada dia:
{
  "data": "2026-11-20",
  "treino": "Tiros: 2 km de aquecimento + 10x100 m em subida + 2 km de desaquecimento",
  "icone": "⚡",
  "rotas": ["sprints_quartier", "sprints_una"]
}
Já no arquivo rotas.json, ficam as informações sobre os percursos: 
"sprints_una": {
  "nome": "Região do Una",
  "relevo": "percurso com subidinhas",
  "seguro_no_escuro": true
}
Uma vantagem dessa organização é que posso alterar os treinos e as rotas diretamente nos arquivos JSON, sem precisar modificar o código principal do programa. 

4. Pré-requisitos e Como Executar
Para utilizar o projeto, é necessário ter o Python 3.9 ou superior instalado e possuir uma conta no Telegram.
Passo 1 – Criar o bot no Telegram
Primeiro, é necessário criar um bot que será responsável por enviar as mensagens.
Abrir o Telegram e procurar por @BotFather.
Enviar o comando /newbot.
Escolher um nome e um usuário para o bot.
Após a criação, o Telegram fornecerá um token de acesso.
Abrir a conversa com o bot criado e enviar uma mensagem, como "oi".
Consultar o endereço abaixo no navegador, substituindo pelo token recebido:
https://api.telegram.org/botSEU_TOKEN/getUpdates
Nessa consulta, é possível encontrar o número chamado chat id, que identifica a conversa que receberá as mensagens. 
Passo 2: Baixar e configurar
Nessa consulta, é possível encontrar o número chamado chat id, que identifica a conversa que receberá as mensagens. 

git clone https://github.com/SEU_USUARIO/clima-bot.git
cd clima-bot

python -m venv venv

Ativar o ambiente virtual: 

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

Instalar as bibliotecas: 

pip install -r requirements.txt

Depois, criar o arquivo .env a partir do modelo .env.example: 


# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env

Abrir o arquivo .env e preencher as informações do token e do chat id. 



Passo 3: Executar no computador

Para testar o funcionamento uma única vez, utilizar:


python clima_bot.py --agora

Para deixar o programa executando e enviando as mensagens diariamente:

python clima_bot.py

Também é possível testar o treino de uma data específica no Windows: 

set DATA_TESTE=2026-11-20
python clima_bot.py --agora


Passo 4 – Configurar a execução automática pelo GitHub
Para que o bot funcione mesmo com o computador desligado, foi utilizada a ferramenta GitHub Actions.
Primeiro, é necessário enviar os arquivos do projeto para um repositório no GitHub, sem incluir o arquivo .env.
Depois, acessar:
Settings > Secrets and variables > Actions
Criar duas informações de acesso:
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
O arquivo clima.yml já contém a configuração para executar o programa diariamente.
O horário configurado é 30 8 * * *, que corresponde às 5h30 no horário de Brasília, pois o GitHub utiliza o horário UTC.
Também é possível iniciar uma execução manualmente pela opção:
Actions > Clima Bot > Run workflow
Segurança das informações:
O token do Telegram e o chat id são informações que precisam ser protegidas. Por isso, ficam armazenados no arquivo .env durante os testes locais e no GitHub Secrets quando o programa é executado na nuvem.
O arquivo .env não é enviado ao repositório, evitando que outras pessoas tenham acesso às informações.

5. Demonstração (Resultados)
Nesta etapa, serão apresentados os resultados do funcionamento do projeto por meio de capturas de tela.
Capturas de tela que devem ser inseridas:
Mensagem recebida no Telegram;
Execução automática pelo GitHub Actions;
Exemplo de mensagem com treino programado e aviso de que ainda está escuro.
Exemplo de mensagem enviada pelo bot:


Quando não existe treino cadastrado para determinada data, o bot envia a mensagem:
"😴 Hoje não há treino no plano."
Dessa forma, o projeto consegue reunir as informações necessárias para organizar a atividade física logo no início da manhã.

6. Melhorias Futuras e Limitações
Durante o desenvolvimento, também foram identificadas algumas possibilidades de melhorias para o projeto.
Melhorias futuras:
Consultar uma API de elevação para identificar melhor as subidas e descidas de cada rota.
Criar um histórico em arquivo CSV para acompanhar as condições do tempo nos dias de treino.
Adicionar informações sobre novos episódios das séries que acompanho, utilizando a API do TMDB.
Permitir que os treinos sejam cadastrados em uma planilha, facilitando a atualização do planejamento.
Limitações atuais:
Os treinos e as informações de segurança das rotas precisam ser cadastrados manualmente.
O GitHub Actions pode apresentar pequenos atrasos no horário programado.
Caso o repositório fique 60 dias sem alterações, o GitHub pode suspender o agendamento automático, sendo necessário reativá-lo.


