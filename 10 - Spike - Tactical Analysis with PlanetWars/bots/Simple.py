class Simple(object):
    
    def update(self, gameinfo):
        
        # Send up to two fleet at a time
        if gameinfo.my_fleets:
            return
        
        # Check if we should attack
        if gameinfo.my_planets and gameinfo.not_my_planets:
            # Find the source planet with the maximum number of ships
            src = None
            max_ships = 0             # Initialize with lowest possible value: 0
            for planet in gameinfo.my_planets.values():
                if planet.num_ships > max_ships:
                    src = planet
                    max_ships = planet.num_ships

            # Find the target planet with the maximum growth rate
            dest = None
            max_growth_rate = -float('inf')  # Initialize with lowest possible value: 0
            for planet in gameinfo.not_my_planets.values():
                if planet.growth_rate >= max_growth_rate:
                    dest = planet
                    max_growth_rate = planet.growth_rate

            # Launch a new fleet if there are enough ships, only 50% of the planet's ships are launched
            if src is not None and dest is not None and src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.5))