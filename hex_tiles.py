import pygame
from pygame.locals import QUIT, KEYDOWN, K_SPACE, K_s, K_ESCAPE
from math import pi, cos, sin, sqrt
from random import choice, shuffle
import numpy as np
from scipy.interpolate import griddata 

pygame.init()

colors = [
	(0, 88, 95), (0, 147, 147), (120, 143, 41), (54, 102, 19) 
]

class HexGrid(object):
	def __init__(self, size = (7, 7), tile_diam = 100, border_size = 10):
		self.size = size
		self.tile_diam = float(tile_diam)
		self.border_size = border_size
		self.tile_center = tile_diam/2.
		self.num_tiles = size[0] * size[1]

		self.corners = []
		self.centers = []
		self.colors = []

		# Create rectangular grid for interpolation
		self.rect_size = (int(size[0] * 4), int(round(size[1] * 3.5))-2)
		self.height_map = np.zeros(self.rect_size)

		self.calc_tile_corners()
		self.reset_colors(False)


	def calc_tile_corners(self):
		self.corners = []

		c = self.tile_center
		d = self.tile_diam
		# A little bit of voodoo magic for the hex tile centers
		centers = [[c+(x*d)+(y%2)*c,1.125*c+0.865*y*d] for x in range(self.size[0]) for y in range(self.size[1])]
		self.centers = centers

		hex_size = c/cos(pi/6) - self.border_size / 2.
		for i, center in enumerate(centers):
			# Correct for alternating rows in hex grid
			corner = []
			for i in range(6):
				angle = 2*pi/6 * (i+0.5)
				x = center[0] + hex_size * cos(angle)
				y = center[1] + hex_size * sin(angle)
				corner.append((x, y))

			self.corners.append(corner)


	def reset_colors(self, random_colors = True):
		if random_colors:
			self.colors = [choice(colors) for i in range(self.num_tiles)]
		else:
			self.colors = []
			for i in range(self.size[0]):
				for j in range(self.size[1]):
					height = self.get_tile_height((i,j))
					self.colors.append(colors[height])


	def get_tile_ind(self, tile):
		return tile[0] * self.size[0] + tile[1]


	def get_center(self, tile):
		ind = self.get_tile_ind(tile)
		return self.centers[ind]


	def get_tile_height(self, coords):
		x = int(coords[0] * 4)
		y = coords[1] * 3.5
		if not coords[1]%2:
			return int(round(self.height_map[x, int(y)]))
		else:
			x += 3
			return int(round((self.height_map[x, y-0.5] + self.height_map[x, y+0.5])/2.))


	def pixels_to_tile(self, coords):
		s, d, b, c = self.size, self.tile_diam, self.border_size, self.tile_center
		
		# Get a bunch of close centers
		x = int(coords[0] / float(d))
		y = int(coords[1] / float(0.865*d))

		para = [x-2, x+3, y-2, y+3]
		for i in range(4):
			if para[i] < 0:
				para[i] = 0

			if i < 2:
				size = s[0]
			else:
				size = s[1]

			if para[i] > size:
				para[i] = size

		tiles = [(i, j) for i in range(para[0], para[1]) for j in range(para[2], para[3])]
		
		# Find minimal distance
		distances = []
		for t in tiles:
			center = self.get_center(t)
			dist = sqrt((center[0] - coords[0])**2 + (center[1] - coords[1])**2)
			distances.append((dist, t))

		distances.sort()
		# print distances
		distance, tile = distances[0]

		# Check if distance within border
		if distance < c:
			border = False
			if distance > c - b:
				border = True
			return tile, border

		return False


	def reset_height(self, values = [0.7, 0.3, 2.5, 2.1, 1.5, 1.2, 1.7]):
		## Create a height map using a interpolation function

		# Define the corner areas
		corner_inds = [
			(0, 0), (0, self.rect_size[0]-1),
			(self.rect_size[0]-1, 0), 
			(self.rect_size[0]-1, self.rect_size[1]-1)
		]

		# Randomly create some high and low points
		num_points = len(values) - 4
		x = np.random.randint(1, self.rect_size[0]-1, (num_points, 1))
		y = np.random.randint(1, self.rect_size[1]-1, (num_points, 1))
		points = np.concatenate([x, y], axis=1)
		points = np.concatenate([points, corner_inds], 0)

		# Assign the values
		v = np.array(values)
		np.random.shuffle(v)
		#values = np.random.choice(values, (num_points+4), replace=False)
		
		# Interpolate
		grid_x, grid_y = np.mgrid[0:self.rect_size[0], 0:self.rect_size[1]]
		grid_z = griddata(points, v, (grid_x, grid_y), method='cubic')

		# Postprocess & map to colors
		height = np.round(grid_z).astype(int)
		height[height > 3] = 3
		height[height < 0] = 0

		self.height_map = height
		self.reset_colors(False)


	def pixel_size(self):
		x = self.tile_diam * (self.size[0] + 0.5)
		y = self.tile_diam * (self.size[1] - 3.5)
		return (int(x), int(y))


	def num_borders(self):
		'''
		Calculates number of borders inside of board.
		'''
		num = self.size[0] * (self.size[0]-1)
		num += (self.size[1]-1) * (sum(self.size)-1)
		return num


	def render(self):
		surf = pygame.surface.Surface(self.pixel_size())
		surf.fill((255, 254, 222))

		for i, corner in enumerate(self.corners):
			pygame.draw.aalines(surf, self.colors[i], True, corner)
			pygame.draw.polygon(surf, self.colors[i], corner)

		# Draw grid
		delta = self.tile_diam/4
		start = self.centers[0]
		for i in range(self.rect_size[0]-1):
			for j in range(self.rect_size[1]-1):
				pass
				# pygame.draw.circle(surf, (50, 50, 50), (int(start[0]+i*delta), int(start[1]+j*delta)), 2)

		return surf


####
# A super simple "GUI"
####

def simple_view(grid):
	screen = pygame.display.set_mode(grid.pixel_size())	
	pygame.display.set_caption('Hex Height Map')

	values = [0.2, 0.2, 2.75, 2.75, 1.5, 0.2, 2.5, 
		0.2, 2.5, 0.2, 2.5, 0.2, 2.5, 0.2, 2.5,
		0.2, 2.5, 0.2, 2.5, 0.2, 2.5, 0.2, 2.5,
		0.2, 2.5, 0.2, 2.5, 0.2, 2.5, 0.2, 2.5,
		1.7, 1.2, 0.7, 2.2, 1.7, 1.2, 0.7, 2.2,
		1.5, 1.2, 0.7, 2.2, 1.7, 1.2, 0.7, 2.2,
		# 1.7, 1.2, 0.7, 2.2, 1.7, 1.2, 0.7, 2.2
	]
	grid.reset_height(values)

	fpsClock = pygame.time.Clock()

	# The loop
	while True:
		screen.fill((0, 0, 0))

		# Render grid
		surf = grid.render()
		screen.blit(surf, (0,0))

		#Handle events (single press, not hold)
		quitted = False
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				quitted = True

			if event.type == pygame.MOUSEBUTTONDOWN:
				pos = pygame.mouse.get_pos()
				coords = grid.pixels_to_tile(pos)
				if coords:
					ind = grid.get_tile_ind(coords[0])
					c_ind = colors.index(grid.colors[ind])
					if event.button == 1 and c_ind < 3:
						c_ind += 1
					elif event.button == 3 and c_ind > 0:
						c_ind -= 1

					grid.colors[ind] = colors[c_ind]

			elif event.type == KEYDOWN:
				if event.key == K_SPACE:
					grid.reset_height(values)
				elif event.key == K_s:
					surf = grid.render()
					pygame.image.save(surf, 'map.png')
				elif event.key == K_ESCAPE:
					pygame.quit()
					quitted = True
		
		if quitted:
			break
		else:

			pygame.display.update()
			fpsClock.tick(40)


if __name__ == '__main__':
	import time
	values = [0.2, 0.2, 2.75, 2.75, 1.5, 0.2, 2.5, 
		0.2, 2.5, 0.2, 2.5, 0.2, 2.5, 0.2, 2.5,
		0.2, 2.5, 0.2, 2.5, 0.2, 2.5, 0.2, 2.5,
		0.2, 2.5, 0.2, 2.5, 0.2, 2.5, 0.2, 2.5,
		1.7, 1.2, 0.7, 2.2, 1.7, 1.2, 0.7, 2.2,
		1.5, 1.2, 0.7, 2.2, 1.7, 1.2, 0.7, 2.2,
		# 1.7, 1.2, 0.7, 2.2, 1.7, 1.2, 0.7, 2.2
	]
	grid = HexGrid((30, 30), 30, 4)
	#for i in xrange(20):
	#	grid.reset_height(values)
	simple_view(grid)