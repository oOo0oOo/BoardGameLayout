import urllib2
import simplejson
import cStringIO
import pygame
pygame.init()



####
# Some names for tech cards
####

land = ['Surface Mining','Underground Mining',
'Open Pit Mining','Open Cast Mining','Placer Mining','Solution Mining','Mining Machinery','Biographical Sketches',
'Mechanical Extraction','Dimension Stone Quarrying','Highwall/Auger Mining',
'Extract Minerals','Rock Breakage','Blasting Prisms','Highwall Mining',
'Mechanical Excavation','Hydraulic Disintegration','Physicochemical Dissolution',
'Aqueous Extraction']

ocean = ['Environmental Study','Ocean Mining',
'cooperative program','deep-sea','environment protection',
'deep-ocean mining system','nodule mining system','seafloor miners',
'seafloor collectors','hoisting systems','pipe dynamics',
'dynamically position ship','self-propelled miner','reduce axial motion',
'vertical slurry lift','manganese nodules','recovery sweep efficiency',
'Pipe Deployment','Pipe Retrieval','pipe-handling system','tow-sled miner',
'remote-controlled miner','miner-to-buffer link','Deep submersible pumps',
'air-lift system','compressed-air injection','Deep-ocean drilling'
]

epochs = ['Paleozoic', 'Cambrian', 'Furongian', 'Ordovician', 'Silurian',
	'Devonian', 'Carboniferous', 'Permian', 'Cisuralian', 'Mesozoic', 
	'Triassic', 'Jurassic', 'Cretaceous', 'Cenozoic', 'Paleogene', 
	'Paleocene', 'Eocene', 'Oligocene', 'Neogene', 'Miocene', 
	'Pliocene', 'Pleistocene']



####
# Tech cards and discovery cards
####

# Tech and discovery extras will be completed using specified parameters:
# n = number (e.g. random choice from 1, 2, 3)
# r = resource
# t = tech (land or ocean)

tech_extras = [
	('One Round: {0} {1}\nfor {1} mine in sector.', ('n', 'r')),
	('3 Rounds: {0} {1}\nfor each {1} mine in sector.', ('n', 'r')),
	('Everyone: {0} {1}\nfor each {1} mine in sector.', ('n', 'r')),

	('3 Rounds:\nDouble the income of a {} mine.', ('t')),
	('3 Rounds:\nDouble the income of a mine.', False),

	('5 Rounds: Trade\n{} {} <==> {} {}', ('n', 'r', 'n', 'r')),
	('5 Rounds: Trade\n{} {} ==> {} {}', ('n', 'r', 'n', 'r')),

	('Build a {} tech card for free.', ('t')),
	('Build a {} mine for half price.', ('t')),

	('Drill for half price\nwith all {} mines.', ('t')),
	('Drill for half price\nwith all {} mines.', ('r')),
	('Drill for free with a {} mine.', ('t')),
	('All {} mines in sector:\ndrill, drill, drilll.', ('r')),

	('3 Rounds:\nTake over an enemy {} mine.', ('t')),
	('3 Rounds:\nTake over an enemy {} mine.', ('r')),
	('{} Rounds:\nTake over all enemy mines in sector.', ('n')),
	('3 Rounds:\nTake over {} enemy pipeline(s).', ('n')),

	('Connect a new mine\nwith a pipeline for free!', False),
	('Connect a new {} mine\nwith a pipeline for free!', ('r')),
	('Build {} pipeline(s) for free!', ('n')),
	('Build {} {} pipeline(s) for free!', ('n', 't')),

	('Take {} {} and {} {}.', ('n', 'r', 'n', 'r')),
	('Take {} {}\nfor each pipeline you possess.', ('n', 'r')),
	('Take {} {}\nfor each {} pipeline you possess.', ('n', 'r', 't')),
	('Take {} {}\nfor each {} mine you possess.', ('n', 'r', 't')),

	('Upgrade sector if {} {} mines exist.', ('n', 'r')),
	('Upgrade sector if {} separate pipeline(s)\nenter sector.', ('n'))
]


discovery_extras = [
	('Permanently 1 {}\nfor each {} mine in sector.', ('r', 'r')),
	('Drill for half price 5 rounds.', False),

	('Upgrade sector to level 2\nat least 3 tech cards', False),
	('Upgrade sector to level 3\nat least 6 tech cards', False),
	('Upgrade sector to level 3\nat least 8 tech cards', False),
	('Upgrade sector to level 2\nat least {} mines', ('n')),

	('You found 3 {} and 3 {}', ('r', 'r')),
	('Permanently trade in sector:\n1 {} ==> 1 {}', ('r', 'r')),
	('Permanently trade in sector:\n2 {} ==> 1 {}', ('r', 'r')),
	('Permanently trade (once per round):\n1 {} ==> 1 {}', ('r', 'r')),

	# ('Free discovery card!', False)
]



####
# A helper function that returns the most popular search result 
# of a google image search as a pygame image.
####

def googleImage(search_term, width = (200, 1000), height = (200, 800)):
	'''
		Image search using Google Images inspired by: 
		http://stackoverflow.com/questions/11242967/python-search-with-image-google-images
	'''
	# Clean up search term
	search_term = search_term.replace(' ','%20')
	search_term = search_term.replace('\n','%20')

	# Construct URL
	url = ('https://ajax.googleapis.com/ajax/services/search/images?' + 'v=1.0&q='+search_term+'&start=0&userip=MyIP')
	request = urllib2.Request(url, None, {'Referer': 'testing'})
	response = urllib2.urlopen(request)

	# Get the image results
	results = simplejson.load(response)
	data = results['responseData']
	try:
		dataInfo = data['results']
	except TypeError, e:
		return False

	# Return first valid result as pygame image
	for url in dataInfo:
		# Check size within bounds
		if width[0] < int(url['width']) < width[1] and height[0] < int(url['height']) < height[1]:
			try:
				# Load image (tmp)
				file = cStringIO.StringIO(urllib2.urlopen(url['url']).read())
				try:
					return pygame.image.load(file)
				# Not right format
				except pygame.error:
					pass
			# Not available
			except (urllib2.HTTPError, urllib2.URLError):
				pass
				
	return False