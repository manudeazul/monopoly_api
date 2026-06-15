# Monopoly API — Guia de uso

## Problema proposto

Considere o seguinte jogo hipotético muito semelhante a Banco Imobiliário, onde várias de suas mecânicas foram simplificadas. Numa partida desse jogo, os jogadores se alteram em rodadas, numa ordem definida aleatoriamente no começo da partida. Os jogadores sempre começam uma partida com saldo de 300 para cada um.

Nesse jogo, o tabuleiro é composto por 20 propriedades em sequência. Cada propriedade tem um custo de venda, um valor de aluguel, um proprietário caso já estejam compradas, e seguem uma determinada ordem no tabuleiro. Não é possível construir hotéis e nenhuma outra melhoria sobre as propriedades do tabuleiro, por simplicidade do problema.

No começo da sua vez, o jogador joga um dado equiprovável de 6 faces que determina quantas espaços no tabuleiro o jogador vai andar.

Ao cair em uma propriedade sem proprietário, o jogador pode escolher entre comprar ou não a propriedade. Esse é a única forma pela qual uma propriedade pode ser comprada.

Ao cair em uma propriedade que tem proprietário, ele deve pagar ao proprietário o valor do aluguel da propriedade.

Ao completar uma volta no tabuleiro, o jogador ganha 100 de saldo.

Jogadores só podem comprar propriedades caso ela não tenha dono e o jogador tenha o dinheiro da venda. Ao comprar uma propriedade, o jogador perde o dinheiro e ganha a posse da propriedade.

Cada um dos jogadores tem uma implementação de comportamento diferente, que dita as ações que eles vão tomar ao longo do jogo.

Um jogador que fica com saldo negativo perde o jogo, e não joga mais. Perde suas propriedades e portanto podem ser compradas por qualquer outro jogador.

Termina quando restar somente um jogador com saldo positivo, a qualquer momento da partida. Esse jogador é declarado o vencedor.

Desejamos rodar uma simulação para decidir qual a melhor estratégia. Para isso, idealizamos uma partida com 4 diferentes tipos de possíveis jogadores. Os comportamentos definidos são:

- O jogador um é **impulsivo** — compra qualquer propriedade sobre a qual ele parar.
- O jogador dois é **exigente** — compra qualquer propriedade, desde que o valor do aluguel dela seja maior do que 50.
- O jogador três é **cauteloso** — compra qualquer propriedade desde que ele tenha uma reserva de 80 saldo sobrando depois de realizada a compra.
- O jogador quatro é **aleatório** — compra a propriedade que ele parar em cima com probabilidade de 50%.

Caso o jogo demore muito, como é de costume em jogos dessa natureza, o jogo termina na milésima rodada com a vitória do jogador com mais saldo. O critério de desempate é a ordem de turno dos jogadores nesta partida.

---

## Pré-requisitos

- Python 3.10+
- pip

## Instalação

```bash
pip install -r requirements.txt
```

## Rodando a aplicação

```bash
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

A API ficará disponível em `http://localhost:8080`.

A documentação interativa (Swagger) fica em `http://localhost:8080/docs`.

---

## Endpoints

### `GET /jogo/simular`

Executa uma simulação completa do jogo e retorna o vencedor.

**Resposta 200**

```json
{
  "vencedor": "cauteloso",
  "jogadores": ["cauteloso", "aleatorio", "exigente", "impulsivo"]
}
```

- `vencedor` — nome do jogador que ganhou a partida
- `jogadores` — todos os quatro jogadores ordenados por saldo final (maior para menor)

---

### `GET /tabuleiro`

Retorna as 20 propriedades do tabuleiro atual (lidas do `board.csv`).

**Resposta 200**

```json
{
  "propriedades": [
    { "posicao": 0, "custo": 60,  "aluguel": 20 },
    { "posicao": 1, "custo": 100, "aluguel": 60 },
    { "posicao": 2, "custo": 120, "aluguel": 70 },
    { "posicao": 3, "custo": 80,  "aluguel": 30 },
    { "posicao": 4, "custo": 90,  "aluguel": 40 },
    { "posicao": 5, "custo": 150, "aluguel": 80 },
    { "posicao": 6, "custo": 110, "aluguel": 55 },
    { "posicao": 7, "custo": 70,  "aluguel": 25 },
    { "posicao": 8, "custo": 130, "aluguel": 65 },
    { "posicao": 9, "custo": 140, "aluguel": 75 },
    { "posicao": 10, "custo": 100, "aluguel": 50 },
    { "posicao": 11, "custo": 160, "aluguel": 90 },
    { "posicao": 12, "custo": 95,  "aluguel": 45 },
    { "posicao": 13, "custo": 85,  "aluguel": 35 },
    { "posicao": 14, "custo": 170, "aluguel": 95 },
    { "posicao": 15, "custo": 115, "aluguel": 60 },
    { "posicao": 16, "custo": 75,  "aluguel": 30 },
    { "posicao": 17, "custo": 125, "aluguel": 70 },
    { "posicao": 18, "custo": 135, "aluguel": 85 },
    { "posicao": 19, "custo": 145, "aluguel": 90 }
  ]
}
```

- `posicao` — índice da casa no tabuleiro (0 a 19)
- `custo` — valor para comprar a propriedade
- `aluguel` — valor cobrado de quem cair na propriedade

---

### `POST /tabuleiro`

Substitui o tabuleiro atual e persiste as alterações no arquivo `board.csv`. O tamanho do tabuleiro é derivado automaticamente do número de linhas do CSV atual.

**Body (JSON)**

```json
{
  "propriedades": [
    { "posicao": 0, "custo": 150, "aluguel": 30 },
    { "posicao": 1, "custo": 200, "aluguel": 50 },
    ...
  ]
}
```

Regras de validação:
- Deve conter exatamente **20 propriedades** (igual ao tamanho atual do tabuleiro)
- As posições devem ser únicas e cobrir de **0 a 19**
- `custo` e `aluguel` devem ser maiores que zero

**Resposta 201**

```json
{
  "mensagem": "Tabuleiro atualizado com sucesso.",
  "propriedades": [
    { "posicao": 0, "custo": 150, "aluguel": 30 },
    { "posicao": 1, "custo": 200, "aluguel": 50 },
    ...
  ]
}
```

**Erros possíveis**

| Código | Motivo |
|---|---|
| 422 | Número de propriedades diferente de 20 |
| 422 | Posições duplicadas ou fora do intervalo 0–19 |
| 422 | `custo` ou `aluguel` com valor zero ou negativo |

---

## Rodando os testes

```bash
pytest test_main.py -v
```

**Testes existentes — classe `Tests_simulacao`**

| Teste | O que verifica |
|---|---|
| `test_impulsivo_compra` | Jogador impulsivo sempre compra qualquer propriedade |
| `test_exigite_acima_50` | Jogador exigente compra quando aluguel > 50 |
| `test_exigente_abaixo_50` | Jogador exigente não compra quando aluguel ≤ 50 |
| `test_cauteloso_com_saldo` | Jogador cauteloso compra quando sobram ≥ 80 após a compra |
| `test_cauteloso_sem_saldo` | Jogador cauteloso não compra quando reserva fica abaixo de 80 |
| `test_carrega_tabuleiro` | CSV é lido corretamente e retorna 20 propriedades |
| `test_vencedor` | `simulate_game()` retorna a chave `vencedor` |
| `test_deu_a_volta` | Jogador ganha 100 ao ultrapassar a posição 19 |
