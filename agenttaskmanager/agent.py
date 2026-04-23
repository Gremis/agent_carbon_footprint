import os
from datetime import datetime
from pathlib import Path
import unicodedata

from dotenv import load_dotenv
from google.adk.agents.llm_agent import Agent
from trello import TrelloClient


load_dotenv(Path(__file__).with_name(".env"))


STATUS_LIST_MAP = {
    "a fazer": ["A FAZER", "TO DO", "TODO"],
    "em andamento": ["EM ANDAMENTO", "DOING"],
    "concluido": ["CONCLUIDO", "CONCLUÍDO", "DONE"],
    "todas": [],
}


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise ValueError(f"Missing required environment variable: {name}")
    return value


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.strip())
    without_accents = "".join(
        char for char in normalized if not unicodedata.combining(char)
    )
    return without_accents.casefold()


def _get_trello_client() -> TrelloClient:
    return TrelloClient(
        api_key=_require_env("TRELLO_API_KEY"),
        api_secret=_require_env("TRELLO_API_SECRET"),
        token=_require_env("TRELLO_TOKEN"),
    )


def _get_board():
    board_name = os.getenv("TRELLO_BOARD_NAME", "DIO")
    client = _get_trello_client()

    for board in client.list_boards():
        if _normalize(board.name) == _normalize(board_name):
            return board

    raise ValueError(
        f'Trello board "{board_name}" was not found for the configured account.'
    )


def _get_lists():
    return _get_board().list_lists()


def _find_list_by_name(list_name: str):
    for trello_list in _get_lists():
        if _normalize(trello_list.name) == _normalize(list_name):
            return trello_list
    return None


def _find_list_by_candidates(candidates: list[str]):
    normalized = {_normalize(name) for name in candidates}
    for trello_list in _get_lists():
        if _normalize(trello_list.name) in normalized:
            return trello_list
    return None


def _find_card_by_name(card_name: str):
    for trello_list in _get_lists():
        for card in trello_list.list_cards(card_filter="open"):
            if _normalize(card.name) == _normalize(card_name):
                return card, trello_list
    return None, None


def _resolve_status_candidates(status: str | None) -> list[str]:
    if not status:
        return []

    normalized_status = _normalize(status)
    return STATUS_LIST_MAP.get(normalized_status, [status])


def _get_default_task_list():
    preferred_names = [
        os.getenv("TRELLO_DEFAULT_LIST_NAME", "A Fazer"),
        "TO DO",
        "A FAZER",
    ]
    return _find_list_by_candidates(preferred_names)


def get_temporal_context() -> str:
    now = datetime.now()
    return now.strftime("%Y/%m/%d %H:%M:%S")


def adicionar_tarefa(
    nome_da_task: str,
    descricao_da_task: str,
    due_date: str = "",
) -> str:
    try:
        lista_destino = _get_default_task_list()
        if not lista_destino:
            return 'Lista "TO DO" ou "A Fazer" nao encontrada.'

        card = lista_destino.add_card(
            name=nome_da_task,
            desc=descricao_da_task,
            due=due_date or "null",
        )
        return (
            f'Tarefa "{card.name}" criada na lista "{lista_destino.name}" '
            f'com id "{card.id}".'
        )
    except Exception as exc:
        return f"Erro ao adicionar tarefa: {exc}"


def listar_tarefas(status: str = "todas") -> str:
    try:
        listas = _get_lists()
        candidatos = _resolve_status_candidates(status)

        if candidatos:
            nomes_filtrados = {_normalize(nome) for nome in candidatos}
            listas_filtradas = [
                lista for lista in listas if _normalize(lista.name) in nomes_filtrados
            ]
        else:
            listas_filtradas = listas

        linhas: list[str] = []
        for lista in listas_filtradas:
            cards = lista.list_cards(card_filter="open")
            if not cards:
                linhas.append(f"- {lista.name}: sem cards abertos")
                continue

            linhas.append(f"- {lista.name}:")
            for card in cards:
                descricao = (card.description or "").strip() or "sem descricao"
                due = (
                    f" | vencimento: {card.due_date}"
                    if getattr(card, "due_date", None)
                    else ""
                )
                linhas.append(f"  - {card.name}: {descricao}{due}")

        if not linhas:
            return f'Nenhuma tarefa encontrada para o filtro "{status}".'

        return "\n".join(linhas)
    except Exception as exc:
        return f"Erro ao listar tarefas: {exc}"


def mudar_status_tarefa(nome_da_task: str, novo_status: str) -> str:
    try:
        listas = _get_lists()
        candidatos = _resolve_status_candidates(novo_status)

        if not candidatos or _normalize(novo_status) == "todas":
            return "Status invalido. Use: 'a fazer', 'em andamento' ou 'concluido'."

        nomes_destino = {_normalize(nome) for nome in candidatos}
        lista_destino = next(
            (lista for lista in listas if _normalize(lista.name) in nomes_destino),
            None,
        )
        if not lista_destino:
            return f'Lista "{novo_status}" nao encontrada no board.'

        card_encontrado = None
        lista_origem = None

        for lista in listas:
            cards = lista.list_cards(card_filter="open")
            card_encontrado = next(
                (
                    card
                    for card in cards
                    if _normalize(card.name) == _normalize(nome_da_task)
                ),
                None,
            )
            if card_encontrado:
                lista_origem = lista
                break

        if not card_encontrado or not lista_origem:
            return f'Card "{nome_da_task}" nao encontrado.'

        if lista_origem.id == lista_destino.id:
            return f'A tarefa "{nome_da_task}" ja esta em "{lista_destino.name}".'

        card_encontrado.change_list(lista_destino.id)
        return (
            f'Tarefa "{nome_da_task}" movida de "{lista_origem.name}" '
            f'para "{lista_destino.name}" com sucesso.'
        )
    except Exception as exc:
        return f"Erro ao mudar status da tarefa: {exc}"


def concluir_tarefa(nome_da_task: str) -> str:
    return mudar_status_tarefa(nome_da_task, "concluido")


def mover_tarefa(nome_da_task: str, nome_da_lista: str) -> str:
    try:
        card, lista_origem = _find_card_by_name(nome_da_task)
        if not card or not lista_origem:
            return f'Card "{nome_da_task}" nao encontrado.'

        lista_destino = _find_list_by_name(nome_da_lista)
        if not lista_destino:
            return f'Lista "{nome_da_lista}" nao encontrada no board.'

        if lista_origem.id == lista_destino.id:
            return f'A tarefa "{nome_da_task}" ja esta em "{lista_destino.name}".'

        card.change_list(lista_destino.id)
        return (
            f'Tarefa "{nome_da_task}" movida de "{lista_origem.name}" '
            f'para "{lista_destino.name}" com sucesso.'
        )
    except Exception as exc:
        return f"Erro ao mover tarefa: {exc}"


def remover_tarefa(nome_da_task: str) -> str:
    try:
        card, lista_origem = _find_card_by_name(nome_da_task)
        if not card or not lista_origem:
            return f'Card "{nome_da_task}" nao encontrado.'

        card.delete()
        return f'Card "{nome_da_task}" removido da lista "{lista_origem.name}".'
    except Exception as exc:
        return f"Erro ao remover tarefa: {exc}"


root_agent = Agent(
    model="gemini-2.5-flash",
    name="root_agent",
    description="Agente de organizacao de tarefas",
    instruction="""
        Voce e um agente de organizacao de tarefas integrado ao Trello.
        Sempre inicie perguntando quais sao as tarefas do dia e use
        get_temporal_context para informar a data e a hora atual.

        Regras:
        - Use adicionar_tarefa para criar tarefas novas.
        - Use listar_tarefas para exibir tarefas por status ou todas.
        - Use mudar_status_tarefa para mover uma tarefa entre status.
        - Use concluir_tarefa para mandar uma tarefa para concluido.
        - Use mover_tarefa para mover diretamente para uma lista especifica.
        - Use remover_tarefa quando o usuario pedir exclusao.
        - Responda em portugues e confirme claramente o resultado.
    """,
    tools=[
        get_temporal_context,
        adicionar_tarefa,
        listar_tarefas,
        mudar_status_tarefa,
        concluir_tarefa,
        mover_tarefa,
        remover_tarefa,
    ],
)
