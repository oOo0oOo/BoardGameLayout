import pygame
import time
from math import pi
from ext_resources import *
import random
import numpy as np

pygame.init()

# Resources
resources = ['oil', 'minerals', 'coal', 'steel']

# Load all the resource images
# And make resource icons (scale image to be within both max_x and max_y)
icon_size = 35.0
orig_res_imgs = {}
resource_icons = {}

for r in resources:
	filepath = 'img/resources/{}.png'.format(r)

	img = pygame.image.load(filepath)

	# Scale image
	scale = min([icon_size / s for s in img.get_size()])
	scaled = pygame.transform.rotozoom(img, 0, scale)

	# Convert icon
	#icon_color = (5, 5, 5)
	#size = scaled.get_size()
	#for pos in [(x, y) for x in range(size[0]) for y in range(size[1])]:
	#	if scaled.get_at(pos)[3] != 0:
	#		scaled.set_at(pos, icon_color)

	# Save images
	orig_res_imgs[r] = img
	resource_icons[r] = scaled



# playing card size = B8 (62 mm * 88 mm)
# @ 150 dpi: 366 px * 520 px
card_size = (366, 520)

# Rounded corners
rounded = 50

# Some colors
black = (10,10,10)
white = (245,245,245)
red = (160, 10, 10)
bg = (80, 80, 80)



def setup_card():

	surf = pygame.surface.Surface(card_size)

	# White BG
	surf.fill(bg)

	# Draw the rounded corners
	corners = [ (i, j) for i in [0, card_size[0]] for j in [0, card_size[1]] ]
	angles = [ 1, 2, 4, 3 ]
	for i, c in enumerate(corners):
		# Find anti point
		anti = []
		for j in range(2):
			if c[j]:
				anti.append(c[j] - rounded)
			else:
				anti.append(rounded)

		left = min([anti[0], c[0]])
		top = min([anti[1], c[1]])
		rect = pygame.Rect(left, top, rounded, rounded)
		pygame.draw.arc(surf, black, rect, angles[i]*0.5*pi, (angles[i]+1)*0.5*pi, 1)

	# Draw rest of outline
	r_half = rounded/2.
	lines = [
		# Top & bottom
		[(r_half, 0), (card_size[0]-r_half, 0)],
		[(r_half, card_size[1]), (card_size[0]-r_half, card_size[1])],
		# left & right
		[(0, r_half), (0, card_size[1]-r_half)],
		[(card_size[0], r_half), (card_size[0], card_size[1]-r_half)]
	]
	for start, stop in lines:
		pygame.draw.line(surf, black, start, stop, 1)

	return surf



def draw_text(surf, text, position, font = 'helvetica', size = 30, color = (250,240,245)):
	fontObj = pygame.font.SysFont(font, size)
	label = fontObj.render(text, 3, color)

	# Center on point
	rect = label.get_rect()
	rect.center = position

	surf.blit(label, rect)




## The mine cards
def create_mine_matrix(resource_prob = [1.2, 1.0, 1.0, 1.2], levels = (2, 4), depths = (2, 10)):
	# decide size of matrix
	level = random.randrange(*levels)
	depth = random.randrange(*depths)

	res_list = []
	amounts = []

	for j in range(depth):
		# Sample from the resources according to probability
		am = []
		for i, p in enumerate(resource_prob):
			am.append( (random.gauss(p, 0.2), i ) )
		largest = sorted(am)[-1]

		res_list.append(largest[1])

		row = [int(round(l*0.5 + largest[0])) for l in range(level)]
		amounts.append(row)

	amounts = np.array(amounts)
	amounts[amounts>3] = 3
	return res_list, amounts




def layout_mine_card(res_list, amounts, name = '', cost = []):
	card = setup_card()

	# Draw the name
	if name:
		draw_text(card, name, (card_size[0]/2, 15), size=30, color = black)

	# The costs
	y = 50
	for resource in cost:
		card.blit(resource_icons[resource], (10, y))
		y += 50

	# Draw the matrix
	s_x, s_y, step = 70, 75, 80
	size = amounts.shape
	indices = [(x, y) for x in range(size[0]) for y in range(size[1])]
	positions = [(s_x + x * step, s_y + y * step) for y, x in indices]
	for i, (row, col) in enumerate(indices):
		amount = amounts[row, col]
		pos = positions[i]
		res = resource_icons[resources[res_list[row]]]
		if amount == 1:
			card.blit(res, pos)
		elif amount == 2:
			card.blit(res, (pos[0]-6, pos[1]-6))
			card.blit(res, (pos[0]+6, pos[1]+6 ))
		elif amount == 3:
			card.blit(res, (pos[0]-10, pos[1]-10))
			card.blit(res, (pos[0], pos[1] ))
			card.blit(res, (pos[0]+10, pos[1]+10 ))

	return card




## The event cards
def layout_event_card(name = '', cost = [], reward = [], description = '', google = True):
	card = setup_card()

	# The image
	img = False
	if name and google:
		img = googleImage(name)

	if img:
		size_x = 250
		scale = float(size_x) / img.get_size()[0]
		# Rotozoom image
		scaled = pygame.transform.rotozoom(img, 0, scale)
		rect = scaled.get_rect()
		rect.center = (card_size[0]/2, card_size[1]/3)
		card.blit(scaled, rect)
		
		# Paste some polygons to make it look nice
		points = [
			# Top
			[(58, 250), (150, 80), (308, 80), (308, 0), (58, 0)],
			# Bottom
			[(58, 300), (220, 300), (308, 155), (308, 500), (58, 500)]

		]
		for p in points:
			pygame.draw.polygon(card, bg, p)


	# Draw the name
	if name:
		draw_text(card, name, (card_size[0]/2, 15), size=30, color = black)

	# The costs
	y = 50
	for resource in cost:
		card.blit(resource_icons[resource], (10, y))
		y += 50


	# the description
	desc_font = pygame.font.SysFont('helvetica', 20)
	if description:
		lines = description.splitlines()
		x = card_size[0]/2
		y = card_size[1]*0.7
		for line in lines:
			text = desc_font.render(line, True, black)
			textRect = text.get_rect()
			textRect.centerx = x
			textRect.centery = y
			card.blit(text, textRect)
			y += 24

	return card



def random_extra(extras, n, t, r):
	tmpl, req = random.choice(extras)
	if req:
		p = []
		for ty in req:
			if ty == 'n':
				p.append(random.choice(n))
			elif ty == 't':
				p.append(random.choice(t))
			elif ty == 'r':
				p.append(random.choice(r))

		desc = tmpl.format(*p)
	else:
		desc = tmpl
	return desc



def random_ocean_tech():
	params = {}
	prob = ['oil']*5 + ['steel'] * 6 + ['minerals'] * 2 + ['coal']
	params['cost'] = sorted([random.choice(prob) for i in range(random.randrange(2, 5))])
	params['name'] = random.choice(ocean).title()#  + random.choice([' I', ' II', ' III', ' IV', ' V'])

	# do tech extra
	desc = ''
	t = ['land'] + ['ocean'] * 3
	r = ['oil']*5 + ['steel'] + ['minerals'] * 5 + ['coal']
	n = [1, 2, 3]

	if random.random() > 0.1:
		desc = random_extra(tech_extras, n, t, r)

	params['description'] = desc
	return params



def random_land_tech():
	params = {}
	prob = ['oil']*3 + ['steel'] * 3 + ['minerals'] * 2 + ['coal'] * 5
	params['cost'] = sorted([random.choice(prob) for i in range(random.randrange(2, 5))])
	params['name'] = random.choice(land).title()
	

	# do tech extra
	desc = ''
	t = ['land'] * 3 + ['ocean']
	r = ['oil']*2 + ['steel']*5 + ['minerals'] * 3 + ['coal']*5
	n = [1, 2]

	if random.random() > 0.1:
		desc = random_extra(tech_extras, n, t, r)

	params['description'] = desc
	return params



def random_discovery():
	params = {}
	prob = ['oil'] + ['steel'] + ['minerals'] + ['coal']
	params['cost'] = sorted([random.choice(prob) for i in range(random.randrange(3, 7))])
	params['name'] = random.choice(epochs).title()
	

	# do land extra
	t = ['land', 'ocean']
	r = ['oil'] + ['steel']*2 + ['minerals'] * 3 + ['coal']
	n = [1, 2, 3, 4]

	desc = random_extra(discovery_extras, n, t, r)

	params['description'] = desc
	return params



def show_card(screen, card, timeout = 1):
	screen.blit(card, (0, 0))
	pygame.display.update()
	time.sleep(timeout)



if __name__ == '__main__':
	# Make a card
	screen = pygame.display.set_mode(card_size)

	# An example card
	example = {
		'name': 'Geo Research Center', 
		'cost': ['steel', 'coal', 'oil'],
		'description': 'Sector upgrade to PHASE 2,\nif workshop in same sector',
		'reward': [] 
		}

	# card = layout_event_card(**example)
	# show_card(screen, card)

	for i in range(1):
		params = random_land_tech()
		card = layout_event_card(**params)
		#pygame.image.save(card, 'output/cards/land_tech{}.png'.format(i))
		show_card(screen, layout_event_card(**params))

		params = random_ocean_tech()
		card = layout_event_card(**params)
		#pygame.image.save(card, 'output/cards/ocean_tech{}.png'.format(i))
		show_card(screen, layout_event_card(**params))

		params = random_discovery()
		card = layout_event_card(**params)
		#pygame.image.save(card, 'output/cards/discovery{}.png'.format(i))
		show_card(screen, layout_event_card(**params))

		res_list, amounts = create_mine_matrix(resource_prob = [1.2, 1.0, 1.0, 1.2], levels = (2, 4), depths = (3, 5))
		card = layout_mine_card(res_list, amounts)
		#pygame.image.save(card, 'output/cards/mine{}.png'.format(i))
		show_card(screen, layout_mine_card(res_list, amounts))