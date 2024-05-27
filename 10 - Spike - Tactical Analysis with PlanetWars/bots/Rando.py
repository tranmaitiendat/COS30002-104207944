import random

class Rando:
    
    def update(self, gameinfo):
        
        # Only send one fleet at a time
        if gameinfo.my_fleets:
            return
        
        # Check if we should attack
        if gameinfo.my_planets and gameinfo.not_my_planets:
            
            # Select random target and destination
            src = random.choice(list(gameinfo.my_planets.values()))
            dest = random.choice(list(gameinfo.not_my_planets.values()))

            # Launch new fleet if there are enough ships
            if src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))