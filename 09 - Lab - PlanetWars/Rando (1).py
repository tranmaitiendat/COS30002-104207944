import random

class Rando:
    
    # Restrict to one fleet at a time  
    if game_state.my_fleets:
        return
    
    # Determine if an attack is feasible
    if game_state.my_planets and game_state.enemy_planets:
        
        # Randomly select source and target planets
        source_planet = random.choice(list(game_state.my_planets.values()))
        target_planet = random.choice(list(game_state.enemy_planets.values()))

        # Send fleet if source has sufficient ships  
        if source_planet.num_ships > 10:  
            game_state.send_fleet(source_planet, target_planet, int(source_planet.num_ships * 0.75))