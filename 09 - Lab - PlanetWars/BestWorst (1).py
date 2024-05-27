class BestWorst(object):
    
   def take_turn(self, game_state):
    
    # Limit to one fleet at a time
    if game_state.my_fleets:
        return

    # Check if attacking is possible
    if game_state.my_planets and game_state.enemy_planets:
        # Find the strongest controlled planet
        strongest_planet = None
        max_ship_count = 0
        for planet in game_state.my_planets.values():
            if planet.num_ships > max_ship_count:
                strongest_planet = planet
                max_ship_count = planet.num_ships

        # Find the weakest enemy planet  
        weakest_planet = None
        min_ship_count = float('inf')
        for planet in game_state.enemy_planets.values():
            if planet.num_ships < min_ship_count:
                weakest_planet = planet
                min_ship_count = planet.num_ships

        # Launch attack if viable
        if strongest_planet and strongest_planet.num_ships > 10:
            game_state.send_fleet(strongest_planet, weakest_planet, int(strongest_planet.num_ships * 0.75))