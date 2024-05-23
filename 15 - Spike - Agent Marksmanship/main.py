import pyglet
#importing graphics for side-effects - it creates the egi and window module objects. 
#This is the closest python has to a global variable and it's completely gross
import graphics
#game has to take another approach to exporting a global variable
#the game object is importable, but only contains the game object if it's being imported after the game object has been created below
import game

if __name__ == '__main__':
	game.game = game.Game()
	pyglet.clock.schedule_interval(game.game.update, 1/60.)
	pyglet.app.run()