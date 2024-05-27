from math import hypot
from enum import Enum
from random import randint

import pyglet

from graphics import COLOUR_NAMES, window
from point2d import Point2D
from graph import SparseGraph, Node, Edge
from searches import SearchAStar
from agent import Agent

BOX_TYPES = {
	".":{"description":'CLEAR', "colour":"WHITE"},
	"m":{"description":'MUD', "colour":"BROWN"},
	"~":{"description":'WATER', "colour":"AQUA"},
	"F":{"description":'FOREST',"colour":"DARK_GREEN"},
	"I":{"description":'ICE',"colour":"BLUE"},
	"X":{"description":'WALL', "colour":"GREY"},
}

MIN_EDGE_COST = 1.0 # must be min value for heuristic cost to work

# def edge_cost(k1, k2):
# 	k1 = box_type.index(k1)
# 	k2 = box_type.index(k2)
# 	return edge_cost_matrix[k1][k2]

class Box(object):
	'''A single box for boxworld. '''

	def __init__(self, index, x, y, width, height, boxType='.'):
		
		self.x = x
		self.y = y
  
		self.index = index
  
		self.width = width
		self.height = height
		
		self.boxType = boxType
    
		# a box must be able to draw:
		# - a box with a grey outline and an (optional) filled colour
		self.box = pyglet.shapes.BorderedRectangle(
			x, y, width, height, border=1,
			color=COLOUR_NAMES[BOX_TYPES[self.boxType]["colour"]], 
			border_color=COLOUR_NAMES["LIGHT_GREY"],
			batch=window.get_batch()
		)
		# - a label showing the box index
		self.label = pyglet.text.Label(
			str(index),
			font_name='Times New Roman',
			font_size=12,
			x=x + width //2, y=y + height // 2,
			anchor_x='center', anchor_y='center',
			color=COLOUR_NAMES["BLACK"],
			batch=window.get_batch("numbers")
		)
		
		# nav graph node
		self.node = None

	def setType(self, boxType):
		if boxType in BOX_TYPES.keys():
			self.boxType = boxType
			self.box.color = COLOUR_NAMES[BOX_TYPES[self.boxType]["colour"]]
   
			return

		else:
			for key, value in BOX_TYPES.items():
				if value['description'] == boxType:
					self.boxType = key
					self.box.color = COLOUR_NAMES[BOX_TYPES[self.boxType]["colour"]]
     
					return
                
		raise ValueError('Not a known tile type "%s"' % boxType)
  
	def traversalCost(agent):
		return agent.traversalCost
	
	def center(self):
		return Point2D(self.x + self.width // 2, self.y + self.height // 2)

class BoxWorld(object):
	'''A world made up of boxes. '''

	def __init__(self, numOfXBoxes, numOfYBoxes, windowWidth, windowHeight):
  
		self.numOfXBoxes = numOfXBoxes 
		self.numOfYBoxes = numOfYBoxes 
  
		boxWidth = windowWidth // numOfXBoxes
		boxHeight = windowHeight // numOfYBoxes
  
		self.wx = (windowWidth - 1) // self.numOfXBoxes
		self.wy = (windowHeight - 1) // self.numOfYBoxes 
  
		self.boxes = [None] * numOfXBoxes * numOfYBoxes
		for i in range(len(self.boxes)):
			self.boxes[i] = Box(index=i, x=i % numOfXBoxes * boxWidth, y=i // numOfXBoxes % numOfYBoxes * boxHeight, width=boxWidth, height=boxHeight)
   
		self.target = None

		fastHunter = Agent(id=1, speedType="FAST", agentType="HUNTER")
  
		slowHunter = Agent(id=2, speedType="SLOW", agentType="HUNTER")

		fastPrey = Agent(id=3, speedType="FAST", agentType="PREY")

		slowPrey = Agent(id=4, speedType="SLOW", agentType="PREY")
  
		self.agents = [fastHunter, slowHunter, fastPrey, slowPrey]

		self.navigationGraphs = {}
		self.paths = {}
		
		self.startMarkers = {}
		for agent in self.agents:
			self.startMarkers[agent.id] = pyglet.shapes.Box(
				self.boxes[0].center().x - self.boxes[0].width,
				self.boxes[0].center().y - self.boxes[0].height,
				self.boxes[0].width, self.boxes[0].height,
				color=COLOUR_NAMES[agent.colors["Start"]],
				batch=window.get_batch("path"),
				thickness=4
			)
		self.targetMarker = pyglet.shapes.Box(
				self.boxes[1].center().x - self.boxes[0].width,
				self.boxes[1].center().y - self.boxes[0].height,
				self.boxes[0].width, self.boxes[0].height,
				color=COLOUR_NAMES["GREEN"],
				batch=window.get_batch("path"),
    			thickness=4
			)
  
		self.setStart(agent=self.agents[0], identificationX=0)
		self.setStart(agent=self.agents[1], identificationX=numOfXBoxes * (numOfYBoxes - 1))
		self.setStart(agent=self.agents[2], identificationX=numOfXBoxes - 1)
		self.setStart(agent=self.agents[3], identificationX=numOfXBoxes * numOfYBoxes - 1)
  
		for subAgent in self.agents:
			if subAgent.currentBox is None:
				subAgent.currentBox = subAgent.startBox
    
		self.currentMarkers = {}
		for agent in self.agents:
			self.currentMarkers[agent.id] = pyglet.shapes.Arc(
				agent.currentBox.center().x,
				agent.currentBox.center().y,
				15 if agent.type == "PREY" else 20, segments=30,
				color=COLOUR_NAMES[agent.colors["Start"]],
				batch=window.get_batch("path"),
				thickness=4
			)

		# Set target for the Preys
		i = randint(1, numOfXBoxes * numOfYBoxes - 2)
		while i == numOfXBoxes * (numOfYBoxes - 1) or i == numOfXBoxes - 1:
			i = randint(1, numOfXBoxes * numOfYBoxes - 2)
   
		self.setTarget(identificationX=i)

		self.agents[0].targetBox = self.agents[3].startBox
		self.agents[1].targetBox = self.agents[2].startBox
  


		self.renderPaths = {}
		self.renderTrees = {}
		self.renderOpenNodes = {}
		self.renderGraphs = {}

		for subAgent in self.agents:
			if subAgent.id not in self.renderPaths:
				self.renderGraphs[subAgent.id] = []

		self.resetNavGraph()

	def getBoxByXY(self, ix, iy):
		idx = (self.numOfXBoxes * iy) + ix
		return self.boxes[idx] if idx < len(self.boxes) else None

	def getBoxByPos(self, x, y):
		idx = (self.numOfXBoxes * (y // self.wy)) + (x // self.wx)
		return self.boxes[idx] if idx < len(self.boxes) else None   
   
	def addEdge(self, agent, fromIdentificationX, toIdentificationX, cost, distance=1.0):
		self.navigationGraphs[agent.id].add_edge(Edge(fromIdentificationX, toIdentificationX, cost * distance))

	def _manhattan(self, idx1, idx2):
		''' Manhattan distance between two nodes in boxworld, assuming the
		minimal edge cost so that we don't overestimate the cost). '''
		x1, y1 = self.boxes[idx1].pos
		x2, y2 = self.boxes[idx2].pos
		return (abs(x1-x2) + abs(y1-y2)) * MIN_EDGE_COST

	def _hypot(self, idx1, idx2):
		'''Return the straight line distance between two points on a 2-D
		Cartesian plane. Argh, Pythagoras... trouble maker. '''
		x1, y1 = self.boxes[idx1].pos
		x2, y2 = self.boxes[idx2].pos
		return hypot(x1-x2, y1-y2) * MIN_EDGE_COST

	def _max(self, idx1, idx2):
		'''Return the straight line distance between two points on a 2-D
		Cartesian plane. Argh, Pythagoras... trouble maker. '''
		x1, y1 = self.boxes[idx1].pos
		x2, y2 = self.boxes[idx2].pos
		return max(abs(x1-x2),abs(y1-y2)) * MIN_EDGE_COST

	def resetNavGraph(self):
		self.navigationGraphs = {}
		for agent in self.agents:
			self.navigationGraphs[agent.id] = SparseGraph()
            
			# Set a heuristic cost function for the search to use
            # self.navigationGraphs[agent.id].cost_h = self._manhattan
			self.navigationGraphs[agent.id].cost_h = self._hypot
			self.navigationGraphs[agent.id].cost_h = self._max

			nx, ny = self.numOfXBoxes, self.numOfYBoxes
			for i, box in enumerate(self.boxes):
				box.pos = (i % nx, i // nx)
				box.node = self.navigationGraphs[agent.id].add_node(Node(idx=i))
                   
			for i, box in enumerate(self.boxes):
				traversalCost = agent.traversalCost[BOX_TYPES[box.boxType]["description"]]
				if traversalCost != float("inf"):
					# UP (i + nx)
					if (i + nx) < len(self.boxes):
						self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=i + nx, cost=traversalCost)
					# DOWN (i - nx)
					if (i - nx) >= 0:
						self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=i - nx, cost=traversalCost)
					# RIGHT (i + 1)
					if (i % nx + 1) < nx:
						self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=i + 1, cost=traversalCost)
					# LEFT (i - 1)
					if (i % nx - 1) >= 0:
					    self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=i - 1, cost=traversalCost)
					# UP LEFT (i + nx - 1)
					j = i + nx
					if (j - 1) < len(self.boxes) and (j % nx - 1) >= 0:
					    self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=j - 1, cost=traversalCost, distance=1.4142)
					# UP RIGHT (i + nx + 1)
					j = i + nx
					if (j + 1) < len(self.boxes) and (j % nx + 1) < nx:
					    self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=j + 1, cost=traversalCost, distance=1.4142)
					# DOWN LEFT (i - nx - 1)
					j = i - nx
					if (j - 1) >= 0 and (j % nx - 1) >= 0:
					    self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=j - 1, cost=traversalCost, distance=1.4142)
					# DOWN RIGHT (i - nx + 1)
					j = i - nx
					if (j + 1) >= 0 and (j % nx + 1) < nx:
					    self.addEdge(agent=agent, fromIdentificationX=i, toIdentificationX=j + 1, cost=traversalCost, distance=1.4142)
                
			for subAgent in self.agents:
				if subAgent.id not in self.renderGraphs.keys():
					self.renderGraphs[subAgent.id] = []
 
			for start, edge in self.navigationGraphs[agent.id].edgelist.items():
				for target in edge.keys():
					self.renderGraphs[agent.id].append(
						pyglet.shapes.Line(
							self.boxes[start].center().x, 
							self.boxes[start].center().y,
							self.boxes[target].center().x,
							self.boxes[target].center().y,
							width=0.5, 
							color=COLOUR_NAMES['PURPLE'],
							batch=window.get_batch("edges")
						)
					)
     
	def setStart(self, agent, identificationX):
		'''Set the start box based on its index idx value. '''

		if self.target == self.boxes[identificationX]:
			raise ValueError("Can't have the same start and target boxes!")

		agent.startBox = self.boxes[identificationX]

		self.startMarkers[agent.id].x = agent.startBox.center().x - self.boxes[0].width / 2
		self.startMarkers[agent.id].y = agent.startBox.center().y - self.boxes[0].height / 2
  
	# Set target for the Preys only
	def setTarget(self, identificationX):
		'''Set the start box based on its index idx value. '''

		for agent in self.agents:
			if agent.startBox == self.boxes[identificationX]:
				raise ValueError("Can't have the same start and target boxes!")

		self.target = self.boxes[identificationX]
		self.agents[2].targetBox = self.target
		self.agents[3].targetBox = self.target

		self.targetMarker.x = self.target.center().x - self.boxes[0].width / 2
		self.targetMarker.y = self.target.center().y - self.boxes[0].height / 2
  
	def moveAgent(self, agent):
		if self.paths[agent.id] is None:
			self.planPath(agent=agent, limit=0)
   
		route = [self.boxes[index] for index in self.paths[agent.id].path]

		for i in range(0, len(route) - 1):
			if route[i].center().x == agent.currentBox.center().x and route[i].center().y == agent.currentBox.center().y:
				agent.currentBox = route[i + 1]

				self.currentMarkers[agent.id].x = agent.currentBox.center().x
				self.currentMarkers[agent.id].y = agent.currentBox.center().y
    
				break

	def resetAgent(self, agent):
		agent.currentBox = agent.startBox
  
		self.currentMarkers[agent.id].x = agent.currentBox.center().x
		self.currentMarkers[agent.id].y = agent.currentBox.center().y

	def planPath(self, agent, limit):
		for subAgent in self.agents:
			self.renderPaths[subAgent.id] = []
   
		self.resetAgent(agent)

		self.paths[agent.id] = SearchAStar(self.navigationGraphs[agent.id], agent.startBox.index, agent.targetBox.index, limit)
		
		# print(self.paths[agent.id].report())

		p = self.paths[agent.id].path 
		if len(p) > 1:
			for identificationX in range(len(p) - 1):
				self.renderPaths[agent.id].append(
					pyglet.shapes.Line(
						self.boxes[p[identificationX]].center().x, 
						self.boxes[p[identificationX]].center().y,
						self.boxes[p[identificationX + 1]].center().x,
						self.boxes[p[identificationX + 1]].center().y,
						width=3, 
						color=COLOUR_NAMES[agent.colors["Path"]],
						batch=window.get_batch("path")
					)
				)

	@classmethod
	def FromFile(cls, filename):
		'''Support a the construction of a BoxWorld map from a simple text file.
		See the module doc details at the top of this file for format details.
		'''
		# open and read the file
		f = open(filename)
		lines = []
		for line in f.readlines():
			line = line.strip()
			if line and not line.startswith('#'):
				lines.append(line)
		f.close()
		# first line is the number of boxes width, height
		nx, ny = [int(bit) for bit in lines.pop(0).split()]
		# Create a new BoxWorld to store all the new boxes in...
		world = BoxWorld(nx, ny, window.width, window.height)
  
		# Ready to process each line
		assert len(lines) == ny, "Number of rows doesn't match data."
		# Eead each line
		idx = 0
		for line in reversed(lines): # in reverse order
			bits = line.split()
			assert len(bits) == nx, "Number of columns doesn't match data."
			for bit in bits:
				bit = bit.strip()
				world.boxes[idx].setType(bit)
				idx += 1
		world.resetNavGraph()
  
		return world