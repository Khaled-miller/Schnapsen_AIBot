# Schnapsen AI Bot

This repository contains various AI bot implementations for the Schnapsen card game. The bots use different strategies including probability-based decisions, utility calculations, and various heuristics to play the game effectively.

## Available Bots

The repository includes several bot variants with different strategic approaches:

- **PU.py** - `ProbabilityUtilityBot`: Basic probability-based bot for Phase 1 gameplay
- **PU_A.py** - PU with Additional strategies
- **PU_AF.py** - PU with Additional and Folding strategies
- **PU_AFO.py** - PU with Additional, Folding, and Optimization strategies
- **PU_AFR.py** - PU with Additional, Folding, and Risk assessment
- **PU_AFRO_1.py** - PU with Additional, Folding, Risk, and Optimization (advanced version)
- **PU_AO.py** - PU with Additional and Optimization strategies
- **PU_AR.py** - PU with Additional and Risk assessment
- **PU_ARO.py** - PU with Additional, Risk, and Optimization strategies

## How to Implement the Bots in Your Game

### Prerequisites

Make sure you have the Schnapsen game engine installed https://github.com/intelligent-systems-course/schnapsen. These bots are designed to work with the `schnapsen` Python package.

### Step 1: Import the Bot

To use any of these bots in your Schnapsen game, first import the bot class you want to use:

```python
import random
from schnapsen.bots import PU_AFRO  # or any other bot variant
from schnapsen.game import SchnapsenGamePlayEngine
```

Alternatively, if the bots are in separate files in your project:

```python
import random
from PU_AFRO_1 import PU_AFRO  # Import from the local file
from schnapsen.game import SchnapsenGamePlayEngine
```

### Step 2: Initialize the Bot

Create an instance of the bot with a random seed:

```python
# Create a random number generator with a seed for reproducibility
rng = random.Random(2025)

# Initialize the bot
my_bot = PU_AFRO(rng, name="MyAIBot")
```

### Step 3: Set Up the Game Engine

Initialize the Schnapsen game engine:

```python
engine = SchnapsenGamePlayEngine()
```

### Step 4: Play a Game

You can play a game between two bots or between your bot and another:

```python
# Create two bots
bot1 = PU_AFRO(random.Random(2025), name="Bot1")
bot2 = PU_A(random.Random(2026), name="Bot2")

# Play a single game
winner, points, score = engine.play_game(bot1, bot2, random.Random(100))

print(f"Winner: {winner}")
print(f"Points: {points}")
print(f"Score: {score}")
```

## Complete Example

Here's a complete example that plays multiple games and calculates win rates:

```python
import random
from schnapsen.bots import PU_AFRO, PU_A
from schnapsen.game import SchnapsenGamePlayEngine

def play_games_and_return_stats(engine, bot1, bot2, pairs_of_games):
    """
    Play 2 * pairs_of_games games between bot1 and bot2.
    Each pair swaps the roles of leader and follower.
    """
    bot1_wins = 0
    
    for game_pair in range(pairs_of_games):
        for lead, follower in [(bot1, bot2), (bot2, bot1)]:
            winner, _, _ = engine.play_game(lead, follower, random.Random(game_pair))
            if winner == bot1:
                bot1_wins += 1
                
        if game_pair > 0 and (game_pair + 1) % 500 == 0:
            print(f"Progress: {game_pair + 1}/{pairs_of_games} game pairs played")
            
    return bot1_wins

# Set up the game
engine = SchnapsenGamePlayEngine()
bot1 = PU_AFRO(random.Random(2025), name="Advanced Bot")
bot2 = PU_A(random.Random(2025), name="Basic Bot")

# Play 1000 games (500 pairs)
number_of_games = 1000
pairs_of_games = number_of_games // 2

bot1_wins = play_games_and_return_stats(engine, bot1, bot2, pairs_of_games)

# Print results
win_rate = (bot1_wins / number_of_games) * 100
print(f"\nResults of {number_of_games} games:")
print(f"{bot1.name} wins: {bot1_wins}")
print(f"{bot2.name} wins: {number_of_games - bot1_wins}")
print(f"{bot1.name} win rate: {win_rate:.2f}%")
```

## Bot Strategy Overview

### ProbabilityUtilityBot (PU.py)
The base bot implements a probabilistic strategy:
* **Phase 1:** Calculates the probability that the opponent has a higher card of the same suit
* **Phase 2:** Plays randomly
* **Goal:** Aims to avoid playing cards that could result in easy wins for the opponent

### Advanced Variants
The other bot variants (PU_A, PU_AF, PU_AFO, etc.) extend the base strategy with additional features:
* **A (Additional):** Additional strategic considerations
* **F (Folding):** Smart folding strategies
* **R (Risk):** Risk assessment and management
* **O (Optimization):** Optimized decision-making algorithms

## Testing and Experimentation
Use the `experiement.py` file as a template to test different bots against each other and compare their performance. You can modify the bots being tested and the number of games to suit your needs.

## Requirements
* Python 3.x
* schnapsen game engine package
* Standard library: `random`, `typing`

## License
See LICENSE file for details.

## Contributing
Feel free to experiment with different strategies and create your own bot variants based on the existing implementations!
