from math import hypot

class TacticalAnalysis(object):
    
    def __init__(self):
        
        self.mode = 'attack'
        
    def update(self, gameinfo):
        
        if gameinfo.my_fleets:
            return
        
        if self.mode == 'defend':
            self.defend(gameinfo)
        elif self.mode == 'attack':
            self.attack(gameinfo)
            
    def my_weakest_planet(self, gameinfo):
        return min([planet for planet in gameinfo.my_planets.values()], key=lambda p: p.num_ships, default=None)
    
    def my_strongest_planet(self, gameinfo):
        return max([planet for planet in gameinfo.my_planets.values()], key=lambda p: p.num_ships, default=None)
    
    # Wealth is determined by the growth rate
    def enemy_wealthiest_near_planet(self, gameinfo, my_src_planet):
        # Calculate the average value of distance from enemies planets to the source planet
        
        distancesToSrc = []
        for planet in gameinfo.neutral_planets.values():
            distancesToSrc.append(hypot(my_src_planet.x - planet.x, my_src_planet.y - planet.y))
            
        average_distance = float('inf')
        if len(distancesToSrc) != 0:
            average_distance = sum(distancesToSrc) / len(distancesToSrc)
        
        # Return the wealthiest planet amone the nearest one (<= avearage distance)
        return max([planet for planet in gameinfo.not_my_planets.values() if hypot(my_src_planet.x - planet.x, my_src_planet.y - planet.y) <= average_distance], key=lambda p: p.growth_rate, default=None)
    
    # My strongest planet that will support another
    def my_strongest_planet_to_support(self, gameinfo, need_to_support_planet):
        return max([planet for planet in gameinfo.my_planets.values() if planet != need_to_support_planet], key=lambda p: p.num_ships, default=None)
    
    def is_weak(self, planet):
        # Planet is weak if its nmber of ships < 15
        return planet.num_ships < 15
    
    def weak_rate(self, gameinfo):
        
        my_weak_planets = [planet for planet in gameinfo.my_planets.values() if self.is_weak(planet)]
    
        weak_rate = (float)(len(my_weak_planets)) / (len(gameinfo.my_planets.values()) + 1)
        
        return weak_rate
    
    # Defense: Find the bot's weakest planet, then use a strongest one to support it
    def defend(self, gameinfo):
        
        print("Tatical Analysis: Defend")
        
        # If more than 30% of the bot's planet is weak:
        # or the number of ships is > 1 
        if len(gameinfo.my_planets.values()) > 1 and self.weak_rate(gameinfo) >= 0.3:
            dest = self.my_weakest_planet(gameinfo)
            src = self.my_strongest_planet_to_support(gameinfo, dest)
            
            # Support by send half of the ships
            gameinfo.planet_order(src, dest, int(src.num_ships * 0.5))
            
            if src is not None:
                gameinfo.planet_order(src, dest, int(src.num_ships * 0.5))
        else:
            self.mode = 'attack'
            self.attack(gameinfo)
            
    def attack(self, gameinfo):
        
        print("Tatical Analysis: Attack")
        
        # If less than 30% of the bot's planet is weak:
        if self.weak_rate(gameinfo) < 0.3 or len(gameinfo.my_planets.values()) <= 1:
            
            src = self.my_strongest_planet(gameinfo)
        
            if src is not None:
                
                dest = self.enemy_wealthiest_near_planet(gameinfo, src)
                
                # Send half of the ships
                if dest is not None:
                    gameinfo.planet_order(src, dest, int(src.num_ships * 0.5))
            
        else:
            self.mode = 'defend'
            self.defend(gameinfo)
        