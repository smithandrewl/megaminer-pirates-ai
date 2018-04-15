# This is where you build your AI for the Pirates game.

from joueur.base_ai import BaseAI
from games.pirates.fuzzy_logic import *
# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>

class EnemyInfo:
    def __init__(self):
        self.enemy_ships = []
        self.enemy_crew = []
        self.weakest_unit = None
        self.ship_count = 0


    def update(self, game):
        self.unit_count = 0
        self.enemy_units = []
        self.weakest_unit = None

        player = game.current_player
        enemy = player.opponent


        self.ship_count = len(enemy.units)

        min_ship_health = 10000


        for unit in enemy.units:
            print(unit.crew_health)

            self.enemy_units.append(unit)

            if unit.ship_health < min_ship_health:
                min_ship_health = unit.ship_health
                self.weakest_unit = unit

        self.unit_count = len(self.enemy_ships)

        print("Unit count: {0}".format(self.unit_count))

class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

    def get_name(self):
        """ This is the name you send to the server so your AI will control the player named this string.

        Returns
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "RustyBike" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self):
        self.enemy_info = EnemyInfo()

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

        game_turn = FuzzyVariable("Game turn", 0.0, 0.0, 0.0, 0.0)

        grade(self.game._current_turn, 0.0, 2000.0, game_turn)

        early_game = game_turn.get_low()


        self.enemy_info.update(self.game)

        if len(self.player._units) == 0:
            # Spawn a crew if we have no units
            self.player.port.spawn("crew")
        elif self.player._units[0]._ship_health == 0:
            # Spawn a ship so our crew can sail
            self.player.port.spawn("ship")

        for unit in self.player.units:
            health = FuzzyVariable("", 0.0, 0.0, 0.0,0.0)

            grade(unit.ship_health, 0.0, self.game._ship_health / 2.0, health)



            if unit._ship_health < self.game._ship_health / 2.0:
                # Heal our unit if the ship is almost dead
                # Note: Crew also have their own health. Maybe try adding a check to see if the crew need healing?


                # Find a path to our port so we can heal
                path = self.find_path(unit.tile, self.player.port.tile, unit)
                if len(path) > 0:
                    # Move along the path if there is one
                    unit.move(path[0])
                else:
                    # Try to deposit any gold we have while we're here
                    unit.deposit()

                    # Try to rest
                unit.rest()
            else:
                print("searching for a ship to attack")


                # Look for a merchant ship
                merchant = None
                for u in self.game.units:
                    if u._target_port is not None:
                        # Found one
                        merchant = u
                        break

                # If we found a merchant, move to it, then attack it
                if merchant is not None:
                    print('We found a merchant ship!')

                    merchant_health = FuzzyVariable("Merchant health",0.0, 0.0, 0.0, 0.0)

                    grade(merchant.ship_health, 0, self.game._ship_health / 2.0, merchant_health )

                    fuzzy_merchant_health_bad = merchant_health.get_med().fuzzyOr(merchant_health.get_low())
                    unit_health_good = health.get_high().fuzzyOr(health.get_med())

                    should_attack = fuzzy_merchant_health_bad.fuzzyAnd(unit_health_good).fuzzyOr(early_game).value


                    if should_attack > 0.5:
                        # Find a path to this merchant
                        path = self.find_path(unit.tile, merchant.tile, unit)
                        if len(path) > self.game._ship_range:
                            # Move until we're within firing range of the merchant
                            # Note: Range is *circular* in pirates, so this can be improved on
                            unit.move(path[0])
                        else:
                            # Try to attack the merchant's ship
                            unit.attack(merchant.tile, "ship")
                else:
                    print("No merchant ship was found :-(")

        return True
        # <<-- /Creer-Merge: runTurn -->>

    def find_path(self, start, goal, unit):
        """A very basic path finding algorithm (Breadth First Search) that when given a starting Tile, will return a valid path to the goal Tile.
        Args:
            start (Tile): the starting Tile
            goal (Tile): the goal Tile
            unit (Unit): the Unit that will move
        Returns:
            list[Tile]: A list of Tiles representing the path, the the first element being a valid adjacent Tile to the start, and the last element being the goal.
        """

        if start == goal:
            # no need to make a path to here...
            return []

        # queue of the tiles that will have their neighbors searched for 'goal'
        fringe = []

        # How we got to each tile that went into the fringe.
        came_from = {}

        # Enqueue start as the first tile to have its neighbors searched.
        fringe.append(start)

        # keep exploring neighbors of neighbors... until there are no more.
        while len(fringe) > 0:
            # the tile we are currently exploring.
            inspect = fringe.pop(0)

            # cycle through the tile's neighbors.
            for neighbor in inspect.get_neighbors():
                # if we found the goal, we have the path!
                if neighbor == goal:
                    # Follow the path backward to the start from the goal and return it.
                    path = [goal]

                    # Starting at the tile we are currently at, insert them retracing our steps till we get to the starting tile
                    while inspect != start:
                        path.insert(0, inspect)
                        inspect = came_from[inspect.id]
                    return path
                # else we did not find the goal, so enqueue this tile's neighbors to be inspected

                # if the tile exists, has not been explored or added to the fringe yet, and it is pathable
                if neighbor and neighbor.id not in came_from and neighbor.is_pathable(unit):
                    # add it to the tiles to be explored and add where it came from for path reconstruction.
                    fringe.append(neighbor)
                    came_from[neighbor.id] = inspect

        # if you're here, that means that there was not a path to get to where you want to go.
        #   in that case, we'll just return an empty path.
        return []

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    # <<-- /Creer-Merge: functions -->>
