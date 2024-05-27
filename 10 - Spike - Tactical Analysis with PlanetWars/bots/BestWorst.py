class BestWorst(object):
    
    def update(self, gameinfo):
        
        # Only send one fleet at a time
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

            # Find the target planet with the minimum number of ships
            dest = None
            min_ships = float('inf')  # Initialize with a massive value: + infinity
            for planet in gameinfo.not_my_planets.values():
                if planet.num_ships < min_ships:
                    dest = planet
                    min_ships = planet.num_ships

            # Launch a new fleet if there are enough ships
            if src is not None and src.num_ships > 10:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.75))