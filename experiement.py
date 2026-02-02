import random

from schnapsen.bots import PU_A, PU_AF, ProbabilityUtilityRandBot, PU_AFRO, PU_AFR, PU_AR, PU_AO, PU_AFO, PU_ARO, PU_O,BullyBot, PU_Ad, RdeepBot

from schnapsen.bots.example_bot import ExampleBot

from schnapsen.game import (Bot, GamePlayEngine, Move, PlayerPerspective,
                            SchnapsenGamePlayEngine, TrumpExchange)
from schnapsen.alternative_engines.twenty_four_card_schnapsen import TwentyFourSchnapsenGamePlayEngine

from schnapsen.bots.rdeep import RdeepBot




def play_games_and_return_stats(engine: GamePlayEngine, bot1: Bot, bot2: Bot, pairs_of_games: int) -> int:
    """
    Play 2 * pairs_of_games games between bot1 and bot2, using the SchnapsenGamePlayEngine, and return how often bot1 won.
    Prints progress. Each pair of games is the same original dealing of cards, but the roles of the bots are swapped.
    """
    bot1_wins: int = 0
    lead, follower = bot1, bot2
    for game_pair in range(pairs_of_games):
        for lead, follower in [(bot1, bot2), (bot2, bot1)]:
            winner, _, _ = engine.play_game(lead, follower, random.Random(game_pair))
            if winner == bot1:
                bot1_wins += 1
        if game_pair > 0 and (game_pair + 1) % 500 == 0:
            print(f"Progress: {game_pair + 1}/{pairs_of_games} game pairs played")
    return bot1_wins

def test_win_rate() -> None:
    engine = SchnapsenGamePlayEngine()
    bot1 = PU_AFRO(random.Random(2025))  # the bot that we are testing
    bot2 = PU_A(random.Random(2025))  # Basline bot
    
    # Play 1000 games (500 pairs where bots alternate positions)
    number_of_games = 1000
    pairs_of_games = number_of_games // 2
    
    bot_1 = play_games_and_return_stats(engine=engine, bot1=bot1, bot2=bot2, pairs_of_games=pairs_of_games)
    
    # Calculate and print statistics
    win_rate = (bot_1 / number_of_games) * 100
    print(f"Results of {number_of_games} games:")
    print(f"the {bot1} wins: {bot_1}")
    print(f"the {bot2} wins: {number_of_games - bot_1}")
    print(f"the {bot1} win rate: {win_rate:.2f}%")

test_win_rate()






