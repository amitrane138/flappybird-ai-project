import pygame
import neat
import os
import time
import random
pygame.font.init()

WIN_WIDTH=1020
WIN_HEIGHT=795
global gen
gen=0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird1.png"))) , pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird2.png"))) , pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","bird3.png")))]
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs","background1.png")))

STAT_FONT = pygame.font.Font("Pixeboy.ttf" , 50)
class Bird:
	IMGS=BIRD_IMGS
	MAX_ROTATION=25
	ROT_VEL=20
	ANIMATION_TIME = 4  # the lower the no. the faster is speed and movements

	def __init__(self,x,y):
		self.x=x
		self.y=y
		self.tilt=0
		self.tick_count=0
		self.vel=0
		self.height=self.y
		self.img_count=0
		self.img=self.IMGS[0]
  
	def jump(self):
		self.vel=-10.5
		self.tick_count=0
		self.height=self.y

	def move(self):#does movement
			self.tick_count+=1
			d = self.vel*(self.tick_count) + 1.5*(self.tick_count)**2 #formula for tilting and moving

			if(d>16):
				d=16
			if(d<0):
				d-=2

			self.y = self.y + d

			if(d<0 or self.y<self.height + 50):
				if self.tilt<self.MAX_ROTATION:
					self.tilt=self.MAX_ROTATION
			else:
				if self.tilt>-90:
					self.tilt-=self.ROT_VEL

	def draw(self,win):
		self.img_count+=1
#below is logic for flapping wings
		if self.img_count < self.ANIMATION_TIME:
			self.img=self.IMGS[0]
		elif self.img_count < self.ANIMATION_TIME*2:
			self.img=self.IMGS[1]
		elif self.img_count < self.ANIMATION_TIME*3:
			self.img=self.IMGS[2]
		elif self.img_count < self.ANIMATION_TIME*4:
			self.img=self.IMGS[1]
		elif self.img_count == (self.ANIMATION_TIME*4 + 1):
			self.img=self.IMGS[0]
			self.img_count=0

		if self.tilt <= -80:
			self.img=self.IMGS[1]
			self.img_count=self.ANIMATION_TIME*2

		rotated_image=pygame.transform.rotate(self.img ,self.tilt)
		new_rect=rotated_image.get_rect(center=self.img.get_rect(topleft=(self.x,self.y)).center)
		win.blit(rotated_image,new_rect.topleft)

	def get_mask(self):
		return pygame.mask.from_surface(self.img)#crops image till minimum size (imp for collisions)

class Pipe:
	GAP=200
	VEL=5

	def __init__(self,x):
		self.x=x
		self.height=0

		self.top=0
		self.bottom=0
		self.PIPE_TOP=pygame.transform.flip(PIPE_IMG,False,True)#flipping pipe img for top pipe
		self.PIPE_BOTTOM=PIPE_IMG

		self.passed=False
		self.set_height()

	def set_height(self):
		self.height=random.randrange(50,450)#random limit
		self.top=self.height-self.PIPE_TOP.get_height()
		self.bottom=self.height+self.GAP

	def move(self):
		self.x-=self.VEL

	def draw(self,win):
		win.blit(self.PIPE_TOP ,(self.x,self.top))
		win.blit(self.PIPE_BOTTOM ,(self.x,self.bottom))

	def  collide(self,bird):
		bird_mask=bird.get_mask()
		top_mask=pygame.mask.from_surface(self.PIPE_TOP)
		bottom_mask=pygame.mask.from_surface(self.PIPE_BOTTOM)

		top_offset=(self.x-bird.x,self.top-round(bird.y))#offset from bird and pipe top
		bottom_offset=(self.x-bird.x,self.bottom-round(bird.y))	

		b_point=bird_mask.overlap(bottom_mask,bottom_offset)
		t_point=bird_mask.overlap(top_mask,top_offset)

		if t_point or b_point:
			return True
		return False
		
class Base:
	VEL=5
	WIDTH=BASE_IMG.get_width()
	IMG=BASE_IMG

	def __init__(self, y):
		self.y=y
		self.x1=0
		self.x2=self.WIDTH
		self.x3=self.x2+self.WIDTH

	def move(self):# base movement adding new baseimg once old is off the screen
		self.x1-=self.VEL
		self.x2-=self.VEL
		self.x3-=self.VEL

		if self.x1+self.WIDTH< 0:
			self.x1=self.x3+self.WIDTH

		if self.x2+self.WIDTH < 0:
			self.x2=self.x1+self.WIDTH

		if self.x3+self.WIDTH < 0:
			self.x3=self.x2+self.WIDTH	

	def draw(self,win):
		win.blit(self.IMG ,(self.x1 , self.y))
		win.blit(self.IMG ,(self.x2 , self.y))
		win.blit(self.IMG ,(self.x3 , self.y))

def draw_window(win,birds,pipes,base,score,gen):
	win.blit(BG_IMG,(-135,-50))

	for pipe in pipes: 
		pipe.draw(win)

	text = STAT_FONT.render("Score: " + str(score), 1,(223,97,46))	#render score and string of score and white color text
	win.blit(text,(800,70))#draw on window and if score gets large move left to fit text (10px)	

	
	score_label = STAT_FONT.render("Gen no: " + str(gen-1),1,(223,97,46))
	win.blit(score_label, (790, 270))

    # alive
	score_label = STAT_FONT.render("Alive: " + str(len(birds)),1,(223,97,46))
	win.blit(score_label, (790, 470))

		
	base.draw(win)

	for bird in birds:	
		bird.draw(win)

	pygame.display.update()

def main(genomes,config):
	nets=[]
	ge=[]
	birds=[]
	global gen
	gen += 1

	for _,g in genomes:
		net = neat.nn.FeedForwardNetwork.create(g,config)
		nets.append(net)
		birds.append(Bird(230,350))
		g.fitness=0
		ge.append(g)



	base=Base(730)
	pipes=[Pipe(600)]# adding 1 pipe first
	win=pygame.display.set_mode((WIN_WIDTH,WIN_HEIGHT))					
	clock=pygame.time.Clock()
	run=True
	score=0


	while run:
		clock.tick(20)#change no. to change speed
		for event in pygame.event.get():# for quitting on x button
			if event.type==pygame.QUIT:
				run=False
				pygame.quit()
				quit()

		
		pipe_ind = 0
		if len(birds) > 0:
			if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():# if first pipe is passed then check second
				pipe_ind = 1
		else:
			run=False
			break		

		for x, bird in enumerate(birds):#imp: input to the neural network 
			
			ge[x].fitness +=0.1 # giving fitness for survival
			bird.move()
			output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y-pipes[pipe_ind].bottom)))
			if output[0] > 0.5:# criteria 
				bird.jump() 


		add_pipe=False
		rem=[]

		for pipe in pipes:
			pipe.move()
			for x, bird in enumerate(birds):
				if pipe.collide(bird):
					ge[x].fitness-=1 #give negative 1 fitness when bird hits a pipe 
					birds.pop(x)
					nets.pop(x)
					ge.pop(x)



				if not pipe.passed and pipe.x < bird.x:  # if bird passed the pipe or not 
					pipe.passed=True
					add_pipe=True	

			if pipe.x + pipe.PIPE_TOP.get_width() < 0:   #if pipe is off the screen or not
				rem.append(pipe)	
			
			

		if add_pipe: #adds new pipe once first one is gone
			score+=1
			for g in ge:
				g.fitness += 5#add fitness 5 if bird made further in level and went from between the pipe
			pipes.append(Pipe(600))

		for r in rem:#adds the pipes which have passed the screen to rem list
			pipes.remove(r)

		for x, bird in enumerate(birds):	
			if 	bird.y +bird.img.get_height() >= 730 or bird.y < 0: #if bird has hit the ground or not
				birds.pop(x)
				nets.pop(x)
				ge.pop(x)


		base.move()
		draw_window(win,birds,pipes,base,score,gen)

	
				

def run(config_path):
	config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                         neat.DefaultSpeciesSet, neat.DefaultStagnation,
                         config_path)

	p = neat.Population(config)

	p.add_reporter(neat.StdOutReporter(True))
	stats = neat.StatisticsReporter()
	p.add_reporter(stats)

	winner = p.run(main,50)# run the game 50 times if no success quit


if __name__ == "__main__":
	local_dir = os.path.dirname(__file__)
	config_path = os.path.join(local_dir,"config-feedforward.txt")
	run(config_path)	


				
