# Simple Lichess bot using the berserk library.
# Requires a Lichess API token with the 'bot' scope.
# Install dependencies with:
#   pip install berserk

import berserk
import os
import random


def main():
    token = os.getenv('LICHESS_TOKEN')
    if not token:
        raise RuntimeError("Please set the LICHESS_TOKEN environment variable with your API access token.")

    session = berserk.TokenSession(token)
    client = berserk.Client(session=session)

    # Stream incoming events such as challenges and game moves
    for event in client.bots.stream_incoming_events():
        if event['type'] == 'challenge':
            handle_challenge(client, event['challenge'])
        elif event['type'] == 'gameStart':
            play_game(client, event['game']['id'])


def handle_challenge(client: berserk.Client, challenge: dict):
    """Accept incoming challenges automatically."""
    challenge_id = challenge['id']
    if challenge['variant']['key'] == 'standard':
        client.challenges.accept(challenge_id)
    else:
        client.challenges.decline(challenge_id)


def play_game(client: berserk.Client, game_id: str):
    """Play a game by making random legal moves."""
    board = client.games.export(game_id, as_pgn=False)
    color = board['players']['white']['user']['name'] == client.account.get()['username']

    for event in client.bots.stream_board_state(game_id):
        if event['type'] == 'gameFull':
            continue
        elif event['type'] == 'chatLine':
            continue
        elif event['type'] == 'gameState':
            if event.get('status') in {'mate', 'resign', 'timeout'}:
                break
            if event.get('moves'):
                moves = event['moves'].split()
            else:
                moves = []
            # Determine side to move by counting moves
            side_to_move = 'white' if len(moves) % 2 == 0 else 'black'
            if (color and side_to_move == 'white') or (not color and side_to_move == 'black'):
                # Choose a random legal move
                legal_moves = client.board.get_legal_moves(game_id)
                if not legal_moves:
                    client.board.resign(game_id)
                    break
                move = random.choice(legal_moves)
                client.board.make_move(game_id, move)


if __name__ == '__main__':
    main()
