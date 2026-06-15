import csv
import copy
import random
from pathlib import Path
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

app = FastAPI()

STARTING_BALANCE = 300
BOARD_CSV = Path(__file__).parent / "board.csv"

class Property:
    def __init__(self, position: int, cost: int, rent: int):
        self.position = position
        self.cost = cost
        self.rent = rent
        self.owner: "Player | None" = None


class Player:
    def __init__(self, name: str, behavior: str):
        self.name = name
        self.behavior = behavior
        self.balance = STARTING_BALANCE
        self.position = 0
        self.properties: list[Property] = []
        self.active = True

    def wants_to_buy(self, prop: Property) -> bool:
        if self.behavior == "impulsivo":
            return True
        if self.behavior == "exigente":
            return prop.rent > 50
        if self.behavior == "cauteloso":
            return self.balance - prop.cost >= 80
        if self.behavior == "aleatorio":
            return random.random() < 0.5
        return False

    def release_properties(self):
        for prop in self.properties:
            prop.owner = None
        self.properties.clear()

def _load_board_from_csv(path: Path) -> list[Property]:
    board: list[Property] = []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            board.append(Property(
                position=int(row["posicao"]),
                cost=int(row["custo"]),
                rent=int(row["aluguel"]),
            ))
    if len(board) != BOARD_SIZE:
        raise ValueError(f"O tabuleiro deve ter {BOARD_SIZE} propriedades, mas o CSV contém {len(board)}.")
    return board

def _save_board_to_csv(board: list[Property], path: Path) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["posicao", "custo", "aluguel"])
        writer.writeheader()
        for prop in board:
            writer.writerow({"posicao": prop.position, "custo": prop.cost, "aluguel": prop.rent})

def _count_board_size(path: Path) -> int:
    with open(path, newline="", encoding="utf-8") as f:
        return sum(1 for _ in csv.DictReader(f))

BOARD_SIZE = _count_board_size(BOARD_CSV)

_current_board: list[Property] = _load_board_from_csv(BOARD_CSV)


class PropertySchema(BaseModel):
    posicao: int = Field(..., ge=0, lt=BOARD_SIZE)
    custo: int = Field(..., gt=0)
    aluguel: int = Field(..., gt=0)

class BoardSchema(BaseModel):
    propriedades: list[PropertySchema]

def simulate_game() -> dict:
    board = [copy.copy(p) for p in _current_board]
    for prop in board:
        prop.owner = None

    players = [
        Player("impulsivo", "impulsivo"),
        Player("exigente", "exigente"),
        Player("cauteloso", "cauteloso"),
        Player("aleatorio", "aleatorio"),
    ]
    random.shuffle(players)

    winner: Player | None = None

    for _ in range(1, 1001):
        for player in players:
            if not player.active:
                continue

            dice = random.randint(1, 6)
            new_pos = player.position + dice

            if new_pos >= BOARD_SIZE:
                player.balance += 100

            player.position = new_pos % BOARD_SIZE
            prop = board[player.position]

            if prop.owner is None:
                if player.balance >= prop.cost and player.wants_to_buy(prop):
                    player.balance -= prop.cost
                    prop.owner = player
                    player.properties.append(prop)
            elif prop.owner is not player:
                player.balance -= prop.rent
                prop.owner.balance += prop.rent

                if player.balance < 0:
                    player.active = False
                    player.release_properties()

            active = [p for p in players if p.active]
            if len(active) == 1:
                winner = active[0]
                break

        if winner:
            break

        active = [p for p in players if p.active]
        if len(active) == 1:
            winner = active[0]
            break
    else:
        active = [p for p in players if p.active]
        max_balance = max(p.balance for p in active)
        for p in players:
            if p.active and p.balance == max_balance:
                winner = p
                break

    sorted_players = sorted(players, key=lambda p: p.balance, reverse=True)

    return {
        "vencedor": winner.name,
        "jogadores": [p.name for p in sorted_players],
    }

# Endpoints

@app.get("/jogo/simular")
def simular():
    return simulate_game()


@app.get("/tabuleiro")
def get_tabuleiro():
    return {
        "propriedades": [
            {"posicao": p.position, "custo": p.cost, "aluguel": p.rent}
            for p in _current_board
        ]
    }


@app.post("/tabuleiro", status_code=201)
def post_tabuleiro(body: BoardSchema):
    global _current_board

    if len(body.propriedades) != 20:
        raise HTTPException(
            status_code=422,
            detail=f"O tabuleiro deve ter exatamente 20 propriedades.",
        )

    new_board = sorted(
        [Property(p.posicao, p.custo, p.aluguel) for p in body.propriedades],
        key=lambda p: p.position,
    )

    _save_board_to_csv(new_board, BOARD_CSV)
    _current_board = new_board

    return {
        "mensagem": "Tabuleiro atualizado com sucesso.",
        "propriedades": [
            {"posicao": p.position, "custo": p.cost, "aluguel": p.rent}
            for p in _current_board
        ],
    }
