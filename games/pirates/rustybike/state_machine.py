import logging
import math

from games.pirates.rustybike.fuzzy_logic import FuzzyVariable, grade

def find_path(start, goal, unit):
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

        if inspect is not None:
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


class StateMachine:
    def __init__(self, name, initial_state):
        print("state_machine.{0}".format(name))
        self.logger = logging.getLogger("state_machine.{0}".format(name))
        self.logger.debug("Initializing state machine with a default state of {1}".format(name, initial_state.name))

        self.name = name
        self.state = initial_state
        self.state.entering()

    def update(self, data):
        self.logger.debug("Updating current state")
        self.state.update(self, data)

    def change_state(self, state):

        self.logger.debug("{0}: Changing state".format(self.name))

        self.logger.debug("{0}: {1} state is exiting".format(self.name, self.state.name))
        self.state.exiting()
        self.state = state

        self.logger.debug("{0}: {1} state is entering".format(self.name, self.state.name))
        self.state.entering()

def dist(left_tile, right_tile):
    a = left_tile.x
    b = left_tile.y
    c = right_tile.x
    d = right_tile.y

    return math.fabs(a - c) + math.fabs(b - d)


class BuildingUpGameState:
    def __init__(self):
        self.name = "BuildingUpGameState"

    def entering(self):
        pass

    def exiting(self):
        pass

    def try_to_spawn_ship(self, game_data):
        logging.debug("Trying to spawn a crew")
        if game_data.player.gold >= game_data.game.ship_cost:
            logging.debug("We have the money(${0}, spawning a new ship".format(game_data.player.gold))
            game_data.player.port.spawn("ship")
        else:
            logging.debug(
                "We did not have the money(Required: {0}, Have: {1}".format(game_data.game.ship_cost, game_data.player.gold))

    def try_to_spawn_crew(self, game_data):
        logging.debug("Trying to spawn a crew")
        if game_data.player.gold >= game_data.game.crew_cost:
            logging.debug("We have the money(${0}, spawning a crew".format(game_data.player.gold))
            game_data.player.port.spawn("crew")
        else:
            logging.debug(
                "We did not have the money(Required: {0}, Have: {1}".format(game_data.game.crew_cost, game_data.player.gold))




    def update(self, fsm, game_data):

        if game_data.player.port.tile.unit == None:
            self.try_to_spawn_crew(game_data)
        else:
            self.try_to_spawn_ship(game_data)

        logging.debug("Processing units")
        for idx,unit in zip(range(0, len(game_data.player.units)), game_data.player.units):
            logging.debug("Processing unit {0} of {1}".format(idx, len(game_data.player.units)))

            health = FuzzyVariable("", 0.0, 0.0, 0.0,0.0)

            grade(unit.ship_health, 0.0, game_data.game._ship_health, health)

            if (unit._ship_health < game_data.game._ship_health / 2.0) or (unit.gold > 100):
                logging.debug("Gold is {0}".format(unit.gold))
                logging.debug("Health is {0}".format(unit.ship_health))
                logging.debug("Health is low, heading back")

                # Find a path to our port so we can heal
                path = find_path(unit.tile, game_data.player.port.tile, unit)
                if len(path) > 0:
                    idx = 0
                    moves = unit.moves
                    # Move along the path if there is one
                    while moves > 0:
                        if len(path) > idx:
                            unit.move(path[idx])

                        idx = idx + 1
                        moves = moves - 1
                else:
                    # Try to deposit any gold we have while we're here

                    if unit.gold > 0:
                        unit.deposit()

                    # Try to rest
                    unit.rest()
            else:
                print("searching for a ship to attack")


                # Look for a merchant ship
                merchant = None
                min_dist = 10000

                for u in game_data.game.units:
                    if u._target_port is not None and (u.tile is not None):
                        # Found one
                        if dist(unit.tile, u.tile) < min_dist:
                            min_dist = dist(unit.tile, u.tile)

                            merchant = u
                        break

                # If we found a merchant, move to it, then attack it
                if merchant is not None:

                    merchant_health = FuzzyVariable("Merchant health",0.0, 0.0, 0.0, 0.0)
                    merchant_gold = FuzzyVariable("Merchant gold", 0.0, 0.0, 0.0, 0.0)

                    grade(merchant.ship_health, 0, game_data.game._ship_health, merchant_health )
                    grade(merchant.gold, 0, 1000, merchant_gold)
                    fuzzy_merchant_health_bad = merchant_health.get_low()
                    unit_health_good = health.get_high().fuzzyOr(health.get_med())

                    should_attack = fuzzy_merchant_health_bad.fuzzyOr(unit_health_good).fuzzyOr(merchant_gold.get_high()).value

                    if should_attack > 0.5:

                        print("We have decided to attack")
                        # Find a path to this merchant

                        path = find_path(unit.tile, merchant.tile, unit)
                        if len(path) > game_data.game._ship_range:
                            # Move until we're within firing range of the merchant
                            # Note: Range is *circular* in pirates, so this can be improved on
                            print("Not in range yet, heading closer to the ship")
                            idx = 0
                            # Move along the path if there is one

                            moves = unit.moves

                            while moves > 0:
                                if len(path) > idx:
                                    unit.move(path[idx])

                                idx = idx + 1
                                moves = moves - 1
                        else:
                            print("We are in range, attacking the ship!")
                            # Try to attack the merchant's ship
                            unit.attack(merchant.tile, "ship")


                else:
                    print("No merchant ship was found :-(")

class StartingGameState:
    def __init__(self):
        self.name = "StartingGameState"
        self.ship_has_spawned = False

    def entering(self):
        pass

    def exiting(self):
        pass

    def update(self, fsm, game_data):

        if game_data.player_info.has_units :
            fsm.change_state(BuildingUpGameState())
        else:
            if not game_data.player_info.has_units:
                logging.debug("We have no units, attempting to spawn a crew")
                # Spawn a crew if we have no units
                game_data.player.port.spawn("crew")
            elif game_data.player._units[0]._ship_health == 0:
                # Spawn a ship so our crew can sail
                logging.debug("Attempting to spawn a ship")
                game_data.player.port.spawn("ship")





