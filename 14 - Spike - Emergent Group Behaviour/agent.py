import pyglet
from vector2d import Vector2D
from vector2d import Point2D
from math import sin, cos, radians, sqrt
from random import random, randrange, uniform
from graphics import COLOUR_NAMES, window

class Agent(object):
    
    def __init__(self, world=None, scale=10.0, mass=1.0, color='ORANGE', mode="Wandering"):
        
        self.world = world
        
        dir = radians(random()*360)
        
        self.pos = Vector2D(randrange(world.cx), randrange(world.cy))
        self.vel = Vector2D()
        
        self.heading = Vector2D(sin(dir), cos(dir))
        self.side = self.heading.perp()
        self.scale = Vector2D(scale, scale)  
        self.acceleration = Vector2D()  
        self.mass = mass
        
        self.max_speed = scale * 10
        
        self.color = color
        self.vehicle_shape = [
            Point2D((-sqrt(3) / 6) * 20,  5),
            Point2D((sqrt(3) / 3) * 20,  0),
            Point2D((-sqrt(3) / 6) * 20,  -5),
        ]
        
        self.vehicle = pyglet.shapes.Triangle(
            self.pos.x+self.vehicle_shape[1].x, self.pos.y+self.vehicle_shape[1].y,
            self.pos.x+self.vehicle_shape[0].x, self.pos.y+self.vehicle_shape[0].y,
            self.pos.x+self.vehicle_shape[2].x, self.pos.y+self.vehicle_shape[2].y,
            color= COLOUR_NAMES[self.color],
            batch=window.get_batch("main")
        )
        
        self.mode = mode

        ### wander details
        self.wander_target = Vector2D(1, 0)
        self.wander_dist = 1.0 * scale
        self.wander_radius = 1.0 * scale
        self.wander_jitter = 10.0 * scale
        self.bRadius = scale
        # Force and speed limiting code
        self.max_speed = 20.0 * scale
        self.max_force = 500.0
        
        self.nearRange = 75
        self.farRange = 150
        
        self.nearRangeCircle = pyglet.shapes.Arc(
            x=self.pos.x, y=self.pos.y,
            radius=self.nearRange,
            color=COLOUR_NAMES['TRANSPARENT'],
            batch=window.get_batch("main")
        )
        
        self.farRangeCircle = pyglet.shapes.Arc(
            x=self.pos.x, y=self.pos.y,
            radius=self.farRange,
            color=COLOUR_NAMES['TRANSPARENT'],
            batch=window.get_batch("main")
        )
        
        self.isChosen = False
        
    def increaseNearRange(self):
        
        if self.nearRange + 5 < self.farRange:
            self.nearRange += 5
            
        self.nearRangeCircle.radius = self.nearRange
        
    def decreaseNearRange(self):
        
        if self.nearRange > 10:
            self.nearRange -= 5
            
        self.nearRangeCircle.radius = self.nearRange

    def increaseFarRange(self):
        
        self.farRange += 5
        
        self.farRangeCircle.radius = self.farRange
        
    def decreaseFarRange(self):
        
        if self.farRange - 5 > self.nearRange:
            self.farRange -= 5    
            
        self.farRangeCircle.radius = self.farRange  
 
    def calculate(self, delta):
        
        if self.mode == "Wandering":
            accel = self.wander(delta)
            
        elif self.mode == "Separation":
            
            agentsInNearRange = self.getAllNeighborsInNearRange()
            
            if len(agentsInNearRange) == 0:
                accel = self.wander(delta)
            else:
                nearestAgent = min(agentsInNearRange, key=lambda x: x[1])[0]
                
                accel = self.flee(nearestAgent)
                
        elif self.mode == "Cohesion":
            
            agentsInNearRange = self.getAllNeighborsInNearRange()
            
            if len(agentsInNearRange) == 0:
                accel = self.wander(delta)
            else:
                totalPosX = self.pos.x
                totalPosY = self.pos.y
                for agent, _ in agentsInNearRange:
                    totalPosX += agent.pos.x
                    totalPosY += agent.pos.y
                    
                totalPosX /= (len(agentsInNearRange) + 1)
                totalPosY /= (len(agentsInNearRange) + 1)
                    
                accel = self.seek(Vector2D(x=totalPosX, y=totalPosY))
                
        elif self.mode == "Alignment":
            
            agentsInFarRange = self.getAllNeighborsInFarRange()
            
            if len(agentsInFarRange) == 0:
                accel = self.wander(delta)
            else:
                totalAccel = self.acceleration
                
                for agent, _ in agentsInFarRange:
                    totalAccel = totalAccel + agent.acceleration
                
                accel = totalAccel.normalise() * 100
                
        self.acceleration = accel
        
        return accel
        
    def update(self, delta):
        
        acceleration = self.calculate(delta) / self.mass
        
        # new velocity
        self.vel += acceleration * delta
        # check for limits of new velocity
        self.vel.truncate(self.max_speed)
        # update position
        self.pos += self.vel * delta
        # update heading is non-zero velocity (moving)
        if self.vel.lengthSq() > 0.00000001:
            self.heading = self.vel.get_normalised()
            self.side = self.heading.perp()
        # treat world as continuous space - wrap new position if needed
        self.world.wrap_around(self.pos)
        # update the vehicle render position
        self.vehicle.x = self.pos.x + (self.vel.copy().normalise().x * (sqrt(3) / 3) * 20)
        self.vehicle.y = self.pos.y + (self.vel.copy().normalise().y * (sqrt(3) / 3) * 20)
        self.vehicle.rotation = -self.heading.angle_degrees()
        
        # Update the range renderables
        self.nearRangeCircle.x = self.pos.x
        self.nearRangeCircle.y = self.pos.y
        self.farRangeCircle.x = self.pos.x
        self.farRangeCircle.y = self.pos.y
        
        if self.isChosen:
            self.nearRangeCircle.color = COLOUR_NAMES["RED"]
            self.farRangeCircle.color = COLOUR_NAMES["RED"]
        else:
            self.nearRangeCircle.color = COLOUR_NAMES["TRANSPARENT"]
            self.farRangeCircle.color = COLOUR_NAMES["TRANSPARENT"]
        
        # Update the vehicle renderable
        if self.isChosen or self.isInRangeOfChosenAgent():
            self.vehicle.color = COLOUR_NAMES["RED"]
        else:
            self.vehicle.color = COLOUR_NAMES[self.color]
            
    def isInRangeOfChosenAgent(self):
        
        if self.isChosen:
            return False
        
        chosenAgent = None
        for agent in self.world.agents:
            if agent.isChosen:
                chosenAgent = agent
                break
            
        toChosenAgent = chosenAgent.pos - self.pos
        distanceToChosenAgent = toChosenAgent.length()
        
        return distanceToChosenAgent <= chosenAgent.farRange

    def speed(self):
        return self.vel.length()
    
    def seek(self, target_pos):
        ''' move towards target position '''
        desired_vel = (target_pos - self.pos).normalise() * self.max_speed
        return (desired_vel - self.vel)
    
    def flee(self, other):
        from_target = self.pos - other.pos

        desiredVel = from_target.normalise() * self.max_speed
        return (desiredVel - self.vel) * 20
    
    def wander(self, delta):
        ''' random wandering using a projected jitter circle '''
        wander_target = self.wander_target
        # this behaviour is dependent on the update rate, so this line must
        # be included when using time independent framerate.
        jitter = self.wander_jitter * delta # this time slice
        # first, add a small random vector to the target's position
        wander_target += Vector2D(uniform(-1,1) * jitter, uniform(-1,1) * jitter)
        # re-project this new vector back on to a unit circle
        wander_target.normalise()
        # increase the length of the vector to the same as the radius
        # of the wander circle
        wander_target *= self.wander_radius
        # move the target into a position wander_dist in front of the agent
        wander_dist_vector = Vector2D(self.wander_dist, 0) #also used for rendering
        target = wander_target + Vector2D(self.wander_dist, 0)
        # project the target into world space
        world_target = self.world.transform_point(target, self.pos, self.heading, self.side)
        # and steer towards it

        return self.seek(world_target)
    
    def getAllNeighborsInNearRange(self):
        result = []
        
        for agent in self.world.agents:
            toAgent = agent.pos - self.pos
            distance = toAgent.length()
            
            if distance <= self.nearRange and agent != self:
                result.append((agent, distance))
                
        return result
    
    def getAllNeighborsInFarRange(self):
        result = []
        
        for agent in self.world.agents:
            toAgent = agent.pos - self.pos
            distance = toAgent.length()
            
            if distance <= self.farRange and agent != self:
                result.append((agent, distance))
                
        return result