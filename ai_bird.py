import pygame
import sys
import random
import neat 
import os

"""
AI playing the flappybird game

"""
pygame.font.init()

def setup():
	global screen
	screen = pygame.display.set_mode((600,700))
	screen.fill((0,0,0))
	global clock
	clock = pygame.time.Clock()



class Bird:
	def __init__(self,x,y):
		self.x = x
		self.y = y
		self.initial_velocity = 5
		self.time = 0
		self.bird_imgs = [pygame.image.load("bird1.png"),pygame.image.load("bird2.png"),pygame.image.load("bird3.png")]
		self.animation = 0
		self.current_bird = self.bird_imgs[0]
		self.Rotation = -25
		

	def draw_bird(self):

		if(self.animation < 10):
			self.current_bird = self.bird_imgs[0]

		elif(self.animation >= 10 and self.animation < 20):
			self.current_bird = self.bird_imgs[1]


		elif(self.animation>= 20 and self.animation <30):
			self.current_bird = self.bird_imgs[2]


		elif(self.animation >= 30):
			self.current_bird = self.bird_imgs[0]
			self.animation = 0

		screen.blit(self.current_bird,(self.x,self.y))

		self.animation += 3


	def move_bird(self):
		self.y += self.initial_velocity * self.time + 5 * self.time* self.time
		if(self.y > 670):
			self.y = 670


	def jump(self):
		self.y -= 50
		self.time = 0


	def clock(self):
		self.time += 1/10


	def get_bird_rect(self):
		return self.c.get_rect()


class Pipe:
	def __init__(self,x,y1=0,y2=0):
		self.x = x
		self.min_gap = 50 # the gap between the pipes
		self.pipe_img_bottom = pygame.image.load("pipe.png").convert_alpha()
		self.pipe_img_top = pygame.image.load("pipe2.png").convert_alpha()
		self.height_top = self.pipe_img_top.get_height()
		self.height_bottom = self.pipe_img_bottom.get_height()
		self.bottom_y = random.randint(220,630)
		self.top_y = (self.bottom_y-150) - (self.height_bottom)



	def move_pipe(self):
		self.x -= 10


	def draw_pipes(self):
		screen.blit(self.pipe_img_top,(self.x,self.top_y))
		screen.blit(self.pipe_img_bottom,(self.x,self.bottom_y))
		
	def is_collided(self,Bird):
		first_pipe = self.pipe_img_top.get_rect(topleft = (self.x,self.top_y))
		second_pipe = self.pipe_img_bottom.get_rect(topleft = (self.x,self.bottom_y))

		bird = Bird.current_bird.get_rect(topleft = (Bird.x,Bird.y))

		one = first_pipe.colliderect(bird)
		two = second_pipe.colliderect(bird)

		if(one or two):
			return True

		elif(Bird.y >= 670 or Bird.y < 0):
			return True


		return False


class Main:
	def start(self,genomes,config):
		setup()
		self.Bird = Bird(50,60)
		self.Back_ground = pygame.image.load("bg.png")
		self.pipe_list = [Pipe(650),Pipe(650+400)]

		self.nets = []
		self.Bird_list = []
		self.genomes = []

		for genome_id,genome in genomes:
			genome.fitness = 0
			net = neat.nn.FeedForwardNetwork.create(genome,config)
			self.nets.append(net)
			self.Bird_list.append(Bird(50,60))
			self.genomes.append(genome)




# ---- Main GAME Loop ---------#
	def main_game_loop(self,genomes,config):
		self.start(genomes,config)
		gaming = True
		score = 0
		while (gaming) and len(self.Bird_list)>0:
			clock.tick(30)
			for e in pygame.event.get():
				if(e.type == pygame.QUIT):
					pygame.quit()
					sys.exit()


			screen.blit(self.Back_ground,(0,0))

			for i in self.Bird_list:
				i.move_bird()
				i.draw_bird()
				i.clock()

			current_pipe = self.pipe_list[0]
			if(len(self.Bird_list) > 0):
				if(self.Bird_list[0].x > self.pipe_list[0].x):
					current_pipe = self.pipe_list[1]

				elif(self.Bird_list[0].x > self.pipe_list[1].x):
					current_pipe = self.pipe_list[0]


				elif((self.Bird_list[0].x < self.pipe_list[1].x) and (self.Bird_list[0].x < self.pipe_list[0].x)):
					diff1 = self.pipe_list[1].x - self.Bird_list[0].x 
					diff2 = self.pipe_list[0].x - self.Bird_list[0].x
					if(diff1 > diff2):
						current_pipe = self.pipe_list[0]

					else:
						current_pipe = self.pipe_list[1]

			for i in self.Bird_list:
				pygame.draw.line(screen,(255,0,0),(current_pipe.x,current_pipe.top_y+480),(i.x+i.current_bird.get_width(),i.y))
				pygame.draw.line(screen,(255,0,0),(current_pipe.x,current_pipe.bottom_y),(i.x+i.current_bird.get_width(),i.y))



			for x,bird in enumerate(self.Bird_list):
				self.genomes[x].fitness += 0.1

				output = self.nets[x].activate((abs(bird.x - current_pipe.x), abs(bird.y - (current_pipe.top_y+480)), abs(bird.y - current_pipe.bottom_y)))

				if(output[0] > 0.5):
					bird.jump()


			temp_bird_list = []
			for i in self.Bird_list:
				temp_bird_list.append(i)


			for i in self.pipe_list:
				for Bird in self.Bird_list:
					if(i.is_collided(Bird) and (Bird.x-i.x) < 50):
						self.nets.pop(self.Bird_list.index(Bird))
						self.genomes[self.Bird_list.index(Bird)].fitness -= 5
						self.genomes.pop(self.Bird_list.index(Bird))
						self.Bird_list.pop(self.Bird_list.index(Bird))
			

			
			for x,Bird in enumerate(self.Bird_list):
				for i in self.pipe_list:
					if(Bird.x - i.x == i.pipe_img_top.get_width()):
						self.genomes[x].fitness += 5		



			for i in self.pipe_list:
				if(i.x < -80):
					self.pipe_list.remove(i)
					self.pipe_list.append(Pipe(650))

			for i in self.pipe_list:
				i.move_pipe()
				i.draw_pipes()


			pygame.display.update()


#--------neat-stuff---------#

def run(config_file):
    """
    runs the NEAT algorithm to train a neural network to play flappy bird.
    :param config_file: location of config file
    :return: None
    """
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_file)

    # Create the population, which is the top-level object for a NEAT run.
    p = neat.Population(config)

    # Add a stdout reporter to show progress in the terminal.
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    #p.add_reporter(neat.Checkpointer(5))

    # Run for up to 50 generations.
    m = Main()
    winner = p.run(m.main_game_loop, 1000)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))



if __name__ == '__main__':
    # Determine path to configuration file. This path manipulation is
    # here so that the script will run successfully regardless of the
    # current working directory.
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)