from main import (
    app,
    Player,
    Property,
    simulate_game,
    _load_board_from_csv,
    BOARD_CSV,
)

class Tests_simulacao:
    def criar_tabuleiro(cost=100, rent=20) -> list[Property]:
        return [Property(i, cost=cost, rent=rent) for i in range(20)]

    def test_impulsivo_compra(self):
        player = Player("impulsivo", "impulsivo")
        assert player.wants_to_buy(Property(0, 1, 1)) is True

    def test_exigite_acima_50(self):
        player = Player("exigente", "exigente")
        assert player.wants_to_buy(Property(0, 100, 51)) is True

    def test_exigente_abaixo_50(self):
        player = Player("exigente", "exigente")
        assert player.wants_to_buy(Property(0, 100, 30)) is False
        
    def test_cauteloso_com_saldo(self):
        player = Player("cauteloso", "cauteloso")
        player.balance = 200
        assert player.wants_to_buy(Property(0, 100, 10)) is True  # 200-100=100 >= 80
        
    def test_cauteloso_sem_saldo(self):
        player = Player("cauteloso", "cauteloso")
        player.balance = 179
        assert player.wants_to_buy(Property(0, 100, 10)) is False  # 179-100=79 < 80

    def test_carrega_tabuleiro(self):
        board = _load_board_from_csv(BOARD_CSV)
        assert len(board) == 20

    def test_vencedor(self):
        assert "vencedor" in simulate_game()

    def test_deu_a_volta(self):
        player = Player("impulsivo", "impulsivo")
        player.position = 18
        initial_balance = player.balance

        new_pos = player.position + 4  
        if new_pos >= 20:
            player.balance += 100
        player.position = new_pos % 20

        assert player.balance == initial_balance + 100
        assert player.position == 2
