import random
from typing import Optional
from schnapsen.bots import AlphaBetaBot
from schnapsen.game import (
    Bot,
    Move,
    PlayerPerspective,
    GamePhase,
)
from schnapsen.deck import Card, Rank

class PU_FRO(Bot):
    """
    This bot is designed for Phase 1 of the game, where three strategies work together.
    In cases where the bot is the leader, two strategies are activated.
    The first is the risk factor strategy (referred to as R), which adjusts the value of the utility heuristic based on the game state.
    The second strategy is the opponent's known card strategy (O), which prioritizes playing a marriage move or exchange move first.
    In addition, this strategy utilizes the opponent's known cards to maximize the accuracy of the probability calculation that there is no higher
    card of the same suit in the opponent's hand.
    If the bot is the follower, the follower strategy (F) is activated. This strategy is coded to minimize the loss of high-ranked cards
    and attempts to win the trick when a high-ranked card is led by the opponent.
    """
    def __init__(
        self, rand: random.Random, name: Optional[str] = "PU_FRO"
    ) -> None:
        super().__init__(name)
        self.rng = rand

    def calculate_risk_factor(self, perspective: PlayerPerspective) -> float:
        """Calculate risk factor based on game state.
        
        Args:
            perspective: The player's perspective of the game.
        
        Returns:
            float: The calculated risk factor.
        """
        my_score = perspective.get_my_score().direct_points
        opponent_score = perspective.get_opponent_score().direct_points
        total_my_score = my_score + perspective.get_my_score().pending_points
        total_opponent_score = opponent_score + perspective.get_opponent_score().pending_points
        score_difference = total_my_score - total_opponent_score

        # Base risk factor starts at 1.0
        risk_factor = 1.0

        # Adjust risk based on score difference and nearing endgame
        if total_opponent_score >= 50:  # Opponent close to winning
            if score_difference <= -20:
                risk_factor = 1.8  # High risk-taking if far behind
            else:
                risk_factor = 1.3
        elif total_my_score >= 50:  # We're close to winning
            if score_difference >= 20:
                risk_factor = 0.5  # Low risk when far ahead
            else:
                risk_factor = 0.8
        else:  # General cases based on score difference
            if score_difference >= 20:  # Significantly ahead
                risk_factor = 0.7
            elif score_difference >= 10:  # Moderately ahead
                risk_factor = 0.85
            elif score_difference <= -20:  # Significantly behind
                risk_factor = 1.5
            elif score_difference <= -10:  # Moderately behind
                risk_factor = 1.25

        return risk_factor

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

        probability = (   #Calculate the probability that the opponent has a card that would win our move  
            (u - d) / u *
            (u - d - 1) / (u - 1) *
            (u - d - 2) / (u - 2) *
            (u - d - 3) / (u - 3) *
            (u - d - 4) / (u - 4)
        )
        return probability

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        #get opponent knowen cards 
        opponent_known_cards = perspective.get_known_cards_of_opponent_hand()
        scorer = perspective.get_engine().trick_scorer
        valid_moves = perspective.valid_moves()

        # Leader Role
        if leader_move is None:  # Bot is the leader
            for move in valid_moves:
                if move.is_marriage() or move.is_trump_exchange:
                    return move  # Prioritize marriages or trump exchanges
            #Get the unseen cards so far and exclude the cards that we already konw that the opponent have in their hand
            unseen_cards = [
                card for card in perspective.get_engine().deck_generator.get_initial_deck()
                if card not in perspective.seen_cards(leader_move=None)
                and card not in perspective.get_known_cards_of_opponent_hand()
            ]
            
            risk_factor = self.calculate_risk_factor(perspective) #calculate the risk factor

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
                utility_heuristics = base_utility * risk_factor#Multiply by the risk factor
                # find the move that has the highest probability to win the trick
                if utility_heuristics > max_utility_heuristics:
                    max_utility_heuristics = utility_heuristics
                    chosen_move = move

            return chosen_move or valid_moves[0]  # Fallback to first move

        # Follower Role
        else:
            #handel the case where the leader playes a marriage move
            if leader_move.is_marriage():
                leader_card = leader_move.cards[1]
            else: #not a marriage move
                leader_card = leader_move.card
            leader_card_suit = leader_card.suit

            # Find cards with the same suit, trump cards, and non-trump cards
            same_suit_cards = [move for move in valid_moves if move.card.suit == leader_card_suit]
            trump_cards = [move for move in valid_moves if move.card.suit == perspective.get_trump_suit()]
            non_trump_cards = [move for move in valid_moves if move.card.suit != perspective.get_trump_suit()]

            # When the trick is led by a trump card
            if leader_card.suit == perspective.get_trump_suit():
                for move in valid_moves:
                    #if the move is non-trump jack
                    if move.card.rank == Rank.JACK and move.card.suit != perspective.get_trump_suit():
                        return move  # Play a non-trump jack
                    
                for move in valid_moves:
                    #else the move is non-trump Queen or King
                    if move.card.rank in [Rank.QUEEN, Rank.KING] and move.card.suit != perspective.get_trump_suit():
                        return move  # Play non-trump Q/K with no marriage potential
                for move in trump_cards:
                    #else win the trick if the move rank is higher than the leader move
                    if scorer.rank_to_points(move.card.rank) > scorer.rank_to_points(leader_card.rank):
                        return move  # Play to win
                return min(non_trump_cards, key=lambda move: scorer.rank_to_points(move.card.rank))  # Lose lowest value

            # When the trick is led by a non-trump card
            else:
                for move in same_suit_cards:
                    if scorer.rank_to_points(move.card.rank) > scorer.rank_to_points(leader_card.rank):
                        return move  # Win with lowest non-trump card that isn't marriage potential
                for move in trump_cards:
                    #If the opponent led with a non-trump Ace or ten 
                    if leader_card.rank in [Rank.ACE, Rank.TEN] and leader_card_suit != perspective.get_trump_suit() and trump_cards:
                        return min(trump_cards, key=lambda move: scorer.rank_to_points(move.card.rank)) # Play lowest trump 
                    
                return min(non_trump_cards, key=lambda move: scorer.rank_to_points(move.card.rank))  # Lose lowest value


class PU_AFRO(Bot):
    """
    This is a two-stage bot. In the first stage, it applies PU_FRO bot. In the second stage, it uses Alphbeta Bot.

    Args:
        perspective: An object representing the perspective of the player.
        leader_move: The move of the leader. If this is None, we are the leader.

    Returns:
        A Move object
    """
    def __init__(self, rand: random.Random, name: Optional[str] = "PU_AFRO") -> None:
        super().__init__(name)
        self.rng = rand
        self.bot_phase1: Bot = PU_FRO(rand=self.rng, name="ProbabilityUtilityBot")
        self.bot_phase2: Bot = AlphaBetaBot(name="AlphaBetaBot")

    def get_move(self, perspective: PlayerPerspective, leader_move: Optional[Move]) -> Move:
        if perspective.get_phase() == GamePhase.ONE:
            return self.bot_phase1.get_move(perspective, leader_move)
        elif perspective.get_phase() == GamePhase.TWO:
            return self.bot_phase2.get_move(perspective, leader_move)
        else:
            raise AssertionError("Invalid game phase.")