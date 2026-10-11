
from collections import Counter

MOVES = ("R", "P", "S")

# The move that defeats each possible move.
COUNTER = {
    "R": "P",
    "P": "S",
    "S": "R"
}

MODELS = ("quincy", "kris", "mrugesh", "abbey")

# Quincy's repeating pattern.
QUINCY_PATTERN = ("R", "R", "P", "P", "S")

# Memory for bots that retain their history between matches.
memory = {
    "quincy_calls": 0,
    "mrugesh_history": [],
    "abbey_history": []
}

# State for the current match.
game = {
    "active": False,
    "my_history": [],
    "possible": set(MODELS),
    "last_predictions": {},
    "matches": {name: 0 for name in MODELS},
    "mismatches": {name: 0 for name in MODELS}
}


def predict_all(my_history):
    """Predict each bot's next move using our previous moves."""

    turn = len(my_history)
    predictions = {}

    # 1. Quincy: repeats R, R, P, P, S.
    index = (memory["quincy_calls"] + turn + 1) % 5
    predictions["quincy"] = QUINCY_PATTERN[index]

    # 2. Kris: counters our previous move.
    previous_move = my_history[-1] if my_history else "R"
    predictions["kris"] = COUNTER[previous_move]

    # 3. Mrugesh: counters our most frequent recent move.
    history = memory["mrugesh_history"] + [""] + my_history
    last_ten = history[-10:]

    most_frequent = max(
        set(last_ten),
        key=last_ten.count
    )

    if most_frequent == "":
        most_frequent = "S"

    predictions["mrugesh"] = COUNTER[most_frequent]

    # 4. Abbey: predicts our next move using move-pair
    # frequencies, then chooses the counter to its prediction.
    abbey_history = memory["abbey_history"] + ["R"] + my_history

    play_order = Counter(
        first + second
        for first, second in zip(
            abbey_history,
            abbey_history[1:]
        )
    )

    last_move = abbey_history[-1]

    possible_pairs = [
        last_move + move for move in MOVES
    ]

    best_pair = max(
        possible_pairs,
        key=lambda pair: play_order[pair]
    )

    predictions["abbey"] = COUNTER[best_pair[-1]]

    return predictions


def finish_previous_match():
    """Save the history of the bot from the completed match."""

    if not game["active"]:
        return

    possible = game["possible"]

    if len(possible) == 1:
        identity = next(iter(possible))
    else:
        candidates = possible if possible else MODELS
        identity = max(
            candidates,
            key=lambda name: (
                game["matches"][name]
                - game["mismatches"][name]
            )
        )

    history = game["my_history"]

    if identity == "quincy":
        memory["quincy_calls"] += len(history)

    elif identity == "mrugesh":
        # The bot has not yet received our final move.
        memory["mrugesh_history"].extend(
            [""] + history[:-1]
        )

    elif identity == "abbey":
        memory["abbey_history"].extend(
            ["R"] + history[:-1]
        )


def player(prev_play, opponent_history=[]):
    """Choose the next move in Rock Paper Scissors."""

    # An empty previous play marks the beginning of a match.
    if prev_play == "":
        finish_previous_match()

        game["active"] = True
        game["my_history"] = []
        game["possible"] = set(MODELS)
        game["last_predictions"] = {}
        game["matches"] = {name: 0 for name in MODELS}
        game["mismatches"] = {name: 0 for name in MODELS}

    else:
        # Eliminate models whose predictions do not match
        # the opponent's observed move.
        for name, prediction in game["last_predictions"].items():
            if prediction == prev_play:
                game["matches"][name] += 1
            else:
                game["mismatches"][name] += 1
                game["possible"].discard(name)

    predictions = predict_all(game["my_history"])

    # Use all four models until the opponent is identified.
    candidates = game["possible"] or set(MODELS)

    # Choose the move that defeats the largest number of
    # moves predicted by the remaining candidate models.
    def score(move):
        return sum(
            1
            for name in candidates
            if COUNTER[predictions[name]] == move
        )

    choice = max(MOVES, key=score)

    game["last_predictions"] = predictions
    game["my_history"].append(choice)

    return choice
