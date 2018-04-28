# This is where you build your AI for the Pirates game.
from games.pirates.rustybike.state_machine import StateMachine, StartingGameState
from joueur.base_ai import BaseAI
from games.pirates.rustybike.fuzzy_logic import *
import math
import logging

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>



class GameData:
    def __init__(self, player_info, enemy_info):
        logging.debug("Initializing GameData")
        self.player_info = player_info
        self.enemy_info = enemy_info
        self.game = None
        self.player = None

    def update(self, game):
        logging.debug("Updating GameData")
        self.game = game
        self.player = game.current_player

        self.player_info.update(self)
        self.enemy_info.update(self)

class PlayerInfo:
    def __init__(self):
        self.has_units = False
        self.gold = 0

    def update(self, game_data):
        logging.debug("Updating PlayerInfo")
        logging.debug("game_data.player.units: {0}".format(game_data.player.units))
        self.has_units = (len(game_data.player.units) > 0)
        logging.debug("has_units: {0}".format(self.has_units))
        self.gold = game_data.player.gold

class EnemyInfo:
    def __init__(self):
        self.enemy_ships = []
        self.enemy_crew = []
        self.weakest_unit = None
        self.ship_count = 0

    def update(self, game_data):
        logging.debug("Updating EnemyInfo")
        self.unit_count = 0
        self.enemy_units = []
        self.weakest_unit = None

        player = game_data.player
        enemy = player.opponent

        self.ship_count = len(enemy.units)

        min_ship_health = 10000

        logging.debug("Finding the weakest enemy unit")
        for unit in enemy.units:

            self.enemy_units.append(unit)

            if unit.ship_health < min_ship_health:
                min_ship_health = unit.ship_health
                self.weakest_unit = unit

        self.unit_count = len(self.enemy_ships)


first_run = True

class AI(BaseAI):
    """ The basic AI functions that are the sx`ame between games. """

    def get_name(self):
        """ This is the name you send to the server so your AI will control the player named this string.

        Returns
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "RustyBike" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self):
        global first_run
        if first_run:
            import logging

            logging.basicConfig(level=logging.DEBUG)
            logging.debug("Starting AI!")

            self.game_data = GameData(PlayerInfo(), EnemyInfo())
            self.game_strategy = StateMachine("game_manager", StartingGameState())
            first_run = False

        """ This is called once the game starts and your AI knows its playerID and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your start logic
        # <<-- /Creer-Merge: start -->>

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your game updated logic
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # replace with your end logic
        # <<-- /Creer-Merge: end -->>
    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your turn, False means to keep your turn going and re-call this function.
        """
        # <<-- Creer-Merge: runTurn -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for runTurn

        logging.debug("Starting Game turn {0}".format(self.game.current_turn))

        self.game_data.update(self.game)
        self.game_strategy.update(self.game_data)


        return True
        # <<-- /Creer-Merge: runTurn -->>



    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    # <<-- /Creer-Merge: functions -->>
