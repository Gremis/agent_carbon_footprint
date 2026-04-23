# agent_carbon_footprint

Projeto com um agente `google-adk` integrado ao Trello, configurado para rodar no macOS.

## Estrutura final do projeto

```text
agent_carbon_footprint/
├── agenttaskmanager/
│   ├── __init__.py
│   ├── agent.py
│   ├── .env
│   └── .env.example
├── lab-agent/
├── requirements.txt
├── .gitignore
└── README.md
```

## O que este projeto usa

- `google-adk`
- `py-trello`
- `python-dotenv`
- `datetime` ja vem no Python, entao nao precisa instalar com `pip`

## Antes de comecar no Mac

1. Abra o Terminal.
2. Entre na pasta do projeto:

```bash
cd /Users/greto/agent_carbon_footprint
```

3. Confira se o Python 3.11 existe:

```bash
/opt/homebrew/bin/python3.11 --version
```

Se aparecer erro, instale com:

```bash
brew install python@3.11
```

## Como criar o ambiente virtual no macOS

Se ainda nao existir `lab-agent`, rode:

```bash
cd /Users/greto/agent_carbon_footprint
/opt/homebrew/bin/python3.11 -m venv lab-agent
```

Para ativar o ambiente virtual no Mac:

```bash
source lab-agent/bin/activate
```

Importante:

- no Windows o curso usa `Scripts/activate.ps1`
- no macOS com `zsh`, o correto e `source lab-agent/bin/activate`

Se quiser sair do ambiente virtual depois:

```bash
deactivate
```

## Como instalar as dependencias

Com o ambiente virtual ativado, rode:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para conferir se ficou certo:

```bash
python -m pip list | grep -E "google-adk|py-trello|python-dotenv"
```

## Como configurar as chaves

Este projeto usa um arquivo local chamado `agenttaskmanager/.env`.

Se voce precisar recriar esse arquivo:

```bash
cp agenttaskmanager/.env.example agenttaskmanager/.env
```

Depois edite `agenttaskmanager/.env` e preencha:

```env
GOOGLE_GENAI_USE_VERTEXAI=0
GOOGLE_API_KEY=sua_chave_google
TRELLO_API_KEY=sua_chave_trello
TRELLO_API_SECRET=seu_secret_trello
TRELLO_TOKEN=seu_token_trello
TRELLO_BOARD_NAME=nome_do_board_no_trello
TRELLO_DEFAULT_LIST_NAME=A Fazer
```

## Como conseguir a Google API key

1. Acesse o Google AI Studio.
2. Entre na area de API keys.
3. Crie uma chave nova.
4. Copie a chave.
5. Cole no campo `GOOGLE_API_KEY` do arquivo `agenttaskmanager/.env`.

Nao compartilhe essa chave no chat, em print ou no Git.

## Como conseguir as chaves do Trello

Voce vai precisar de:

- `TRELLO_API_KEY`
- `TRELLO_API_SECRET`
- `TRELLO_TOKEN`
- `TRELLO_BOARD_NAME`

O `TRELLO_BOARD_NAME` precisa ser exatamente o nome do board que o agente vai usar.

As listas esperadas pelo agente sao, por exemplo:

- `A Fazer` ou `TO DO`
- `Em Andamento` ou `Doing`
- `Concluido` ou `Done`

## Como rodar o agente

Na raiz do projeto:

```bash
cd /Users/greto/agent_carbon_footprint
source lab-agent/bin/activate
adk web
```

Depois abra a interface do ADK no navegador e selecione o agente `agenttaskmanager`.

## O que o agente faz hoje

- cria tarefas no Trello
- lista tarefas
- muda o status de uma tarefa
- conclui tarefas
- move tarefas entre listas
- remove tarefas
- gera contexto temporal com data e hora atual

## Como recriar tudo do zero

Se um dia quiser recriar o ambiente virtual do zero:

```bash
cd /Users/greto/agent_carbon_footprint
rm -rf lab-agent
/opt/homebrew/bin/python3.11 -m venv lab-agent
source lab-agent/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Problemas comuns

### `python: command not found`

Use:

```bash
python3 --version
```

ou crie o ambiente com:

```bash
/opt/homebrew/bin/python3.11 -m venv lab-agent
```

### `adk: command not found`

Ative o ambiente virtual primeiro:

```bash
source lab-agent/bin/activate
```

### O agente nao encontra o board do Trello

Confira se `TRELLO_BOARD_NAME` esta exatamente igual ao nome do board.

### O agente nao encontra a lista

Confira se no seu board existem listas como:

- `A Fazer`
- `TO DO`
- `Em Andamento`
- `Doing`
- `Concluido`
- `Done`

## Seguranca das chaves

Se voce mostrou alguma chave em print, chat ou commit:

1. delete ou revogue a chave antiga no servico original
2. crie uma chave nova
3. atualize o arquivo `agenttaskmanager/.env`

Nao suba o arquivo `.env` para o Git.

## Resumo do passo a passo que fizemos no Mac

1. Confirmamos que no Mac o certo e usar `python3.11`, nao `python`.
2. Criamos o ambiente virtual `lab-agent`.
3. Ativamos com `source lab-agent/bin/activate`.
4. Instalamos as dependencias com `pip install -r requirements.txt`.
5. Ajustamos o projeto para usar a pasta existente `agenttaskmanager/`.
6. Criamos o `agent.py` do agente com integracao ao Trello.
7. Mantivemos as chaves em `agenttaskmanager/.env`.
8. Deixamos um `agenttaskmanager/.env.example` como modelo.
9. Limpamos arquivos temporarios e pastas desnecessarias.
