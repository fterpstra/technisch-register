from fs.osfs import OSFS
from bs4 import BeautifulSoup as BS
from json import load
from subprocess import call
import codecs

def create_standard_title(title, description):
	title = '''
		<h2>%s</h2>
		<p>%s</p>
		''' % (title, description)

	# use python's built-in parser which skips
	# creation of html and body tags
	return BS(title, 'html.parser')

def create_substandard_title(standard, artifact, title):
	title = '''
		<p><i class="fa fa-file-o"></i>
			<span style='margin-left: 25px'>
				<a href="http://register.geostandaarden.nl/%s/%s">%s</a>
			</span>
		</p> ''' % (artifact, standard, title)

	return BS(title, 'html.parser')

def create_substandard_description(substandard):
	summary ='''
		<p>
			<span style='margin-left:37px; width: 100%%'>%s</span>
		</p>
		''' % substandard['beschrijving']

	return BS(summary, 'html.parser')

def create_standard_webpage(standard, artifacts):
	# builds each standard's overview page
	# e.g. http://register.geostandaarden.nl/imgeo/

	# load standard HTML template
	with open('web/templates/standard.html', 'r') as f:
		html = BS(f)

	# construct title
	title = create_standard_title(standard['title'], standard['beschrijving'])
	
	# add to #title div
	el_title = html.find(id="title")

	# fetch #container from template
	el_container = html.find(id="container")

	# append title
	el_title.append(title)

	with codecs.open('descriptions.json', encoding='utf8') as f:
		descriptions = load(f)

	# iterate over all artifacts i.e. informatiemodel, gmlapplicatieschema, regels, etc.
	for artifact in artifacts:
		# create title of each sub standard
		title = create_substandard_title(standard['id'], artifact, descriptions[artifact]['titel'])
		el_container.append(title)

		# create description of each standard
		description = create_substandard_description(descriptions[artifact])
		el_container.append(description)

	return html.prettify()

def create_overview_entry(standard, description):
	# url = "http://register.geostandaarden.nl"
	url = "."
	overview = '''
		<p>
			<i class="fa fa-file"></i>
			<span style='margin-left: 25px'>
				<a href="%s/%s/index.html">%s</a>
			</span>
		</p>
		<p><span style='margin-left:37px; width: 100%%'>%s</span></p>
			''' % (url, standard, standard.upper(), description)

 	return BS(overview, 'html.parser')

def create_overview_page(standards, source, destination):
	print 'Creating overview page...'

	# open overview page template
	with codecs.open('web/templates/overview.html', 'r', encoding='utf8') as f:
		html = BS(f)

	el_container = html.find(id='leftcolumn')

	for standard in standards:
		overview = create_overview_entry(standard['id'], standard['beschrijving'])
		el_container.append(overview)

	with codecs.open('%s/index.html' % destination, 'w', encoding='utf8') as f:
		f.write(html.prettify())
		OSFS('./').copydir('web/assets', '%s/assets' % destination)

		print 'Done!'

def build_folders(source, destination, standards, root):
	print "Building register..."

	source_fs = OSFS(source)

	# iterate over all standards in source directory
	for standard in standards:
		print "Processing %s ... " % standard['id']
		standard_fs = source_fs.opendir(standard['id'])

		# list all sub standards of a standard
		artifacts = standard_fs.listdir(dirs_only=True)
		if '.git' in artifacts: artifacts.remove(".git")

		for artifact in artifacts:
			# check whether artifact folder exists in destination 
			if root.exists('%s/%s' % (destination, artifact)) == False:
				root.makedir('%s/%s' % (destination, artifact))
				
			# copy standard folders from source to destination in desired structure
			root.copydir('%s/%s/%s' % (source, standard['id'], artifact),  '%s/%s/%s' % (destination, artifact, standard['id']))

		# create standard HTML page
		html = create_standard_webpage(standard, artifacts)

		# check whether standard folder exists in register root
		if root.exists('%s/%s' % (destination, standard['id'])) == False:
			root.makedir('%s/%s' % (destination, standard['id']))
		
		# write standard HTML page to register/standard/index.html
		with codecs.open('%s/%s/index.html' % (destination, standard['id']), 'w', encoding='utf8') as f:
			f.write(html)

def fetch_repos():
	print "Fetching repositories..."

	with open('repos.json') as f:
		repos = load(f)

		for repo in repos:
			call('git clone %s repos/%s' % (repo['url'], repo['id']));

		#TODO: git pull additions into existing repos, clone new ones


if __name__ == "__main__":
	source = 'repos'
	destination = 'register'

	root = OSFS('./') # 'c:\Users\<login name>' on Windows
	print "removing %s" % source
	# root.removedir(source, force=True)
	# root.makedir(source)
	root.removedir(destination, force=True)
	root.makedir(destination)

	#standards = OSFS(source).listdir(dirs_only=True)
	with open('repos.json') as f:
		standards = load(f)
	
	# fetch_repos()
	build_folders(source, destination, standards, root)
	create_overview_page(standards, source, destination)