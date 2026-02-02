import random
from typing import Optional
from schnapsen.bots import RandBot, AlphaBetaBot
from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase, Card
)


class PU_O(Bot):
    """
    This bot is designed for Phase 1 of the game, where it uses the opponent known cards strategy.
    In cases where the bot is the leader,
    The opponent's known card strategy (O), which prioritizes playing a marriage move or exchange move first.
    In addition, this strategy utilizes the opponent's known cards to maximize the accuracy of the probability calculation that there is no higher
    card of the same suit in the opponent's hand.
    If the bot is the follower, it plays a random move.
    """
    def __init__(
        self, rand: random.Random, name: Optional[str] = "P_O"
    ) -> None:
        super().__init__(name)
        self.rng = rand
        
    def calculate_probability(self, unseen_cards: list[Card], dangerous_cards: list[Card]) -> float:
        """Calculate the probability of the opponent not having dangerous cards.
        
        Args:
            unseen_cards: List of cards not yet seen in the game.
            dangerous_cards: List of cards that could be dangerous if the opponent has them.
        
        Returns:
            float: The calculated probability.
        """
        u = len(unseen_cards)  # Total unseen cards
        d = len(dangerous_cards)  # Total dangerous cards

        if u < 5:
            return 0.0  # Avoid division by zero in edge cases

        probability = (
            (u - d) / u *
            (u - d - 1) / (u - 1) *
            (u - d - 2) / (u - 2) *
            (u - d - 3) / (u - 3) *
            (u - d - 4) / (u - 4)
        )
        return probability
    
    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:

        """
        Use probability to choose a move.

        Args:
            perspective: An object representing the perspective of the player.
            leader_move: The move of the leader. If this is None, we are the leader.

        Returns:
            A Move object
        """
        # get all valid moves
        valid_moves = perspective.valid_moves()
        opponent_known_cards = perspective.get_known_cards_of_opponent_hand() #get opponent knowen cards 
        scorer = perspective.get_engine().trick_scorer

        if leader_move is not None: #we are the leader
            for move in valid_moves:
                if move.is_marriage() or move.is_trump_exchange:
                    return move  # Prioritize marriages or trump exchanges
            #Get the unseen cards so far and exclude the cards that we already konw that the opponent have in their hand
            unseen_cards = [
                card for card in perspective.get_engine().deck_generator.get_initial_deck()
                if card not in perspective.seen_cards(leader_move=None)
                and card not in perspective.get_known_cards_of_opponent_hand()
            ]
            
            max_utility_heuristics = float('-inf') #set the max value for the heuristic for the coming comparison
            chosen_move = None

            for move in valid_moves:
                move_card = move.cards[1] if move.is_marriage() else move.card

                # Identify dangerous cards for this move
                dangerous_cards = [
                    card for card in unseen_cards
                    if card.suit == move_card.suit and scorer.rank_to_points(card.rank) > scorer.rank_to_points(move_card.rank)
                ]

                #Add known opponent cards that are dangerous
                dangerous_cards = [
                    card for card in opponent_known_cards
                    if card.suit == move_card.suit and scorer.rank_to_points(card.rank)> scorer.rank_to_points(move_card.rank)
                ]
                

                # Calculate probability and utility
                probability = self.calculate_probability(unseen_cards, dangerous_cards)
                points = scorer.rank_to_points(move_card.rank)
                base_utility = probability / points #Divide by the value of the move(11, 10, 4, 3, 2) so that high cards value would have less probability
                utility_heuristics = base_utility 
                # find the move that has the highest probability to win the trick
                if utility_heuristics > max_utility_heuristics:
                    max_utility_heuristics = utility_heuristics
                    chosen_move = move

            return chosen_move or valid_moves[0]  # Fallback to first move
            
        #we are the follower 
        else: 
            return self.rng.choice(valid_moves)# plays random move



class PU_AO(Bot):
    """
    This is a two-stage bot. In the first stage, it applies PU_O bot. In the second stage, it uses Alphbeta Bot.

    Args:
        perspective: An object representing the perspective of the player.
        leader_move: The move of the leader. If this is None, we are the leader.

    Returns:
        A Move object
    """

    def __init__(
        self, rand: random.Random, name: Optional[str] = "PU_AO"
    ) -> None:
        super().__init__(name)
        self.rng = rand
        self.bot_phase1: Bot = PU_O(
            rand=self.rng, name="PU_O"
        )
        self.bot_phase2: Bot =  AlphaBetaBot( name="AlphaBetaBot")

    def get_move(
        self, perspective: PlayerPerspective, leader_move: Optional[Move]
    ) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(perspective, leader_move)
        else:
            raise AssertionError("Phase ain't right.")