import requests
from bs4 import BeautifulSoup
import libtorrent as lt
import time

# Function to download the movie from magnet link. Change the save_path.
def downloadMovie(link):
	print("Downloading: ",link)
	ses = lt.session()
	params = { 'save_path': '/home/gaurav/Desktop'}
	handle = lt.add_magnet_uri(ses, link, params)
	print ('downloading metadata...')
	while (not handle.has_metadata()): time.sleep(1)
	print ('got metadata, starting torrent download...')
	while (handle.status().state != lt.torrent_status.seeding):
	    print ('%d %% done' % (handle.status().progress*100))
	    time.sleep(5)
	return "downloaded"

# Function to crawl the magnet links
def crawl():
	print("Crawling...")
	# Get movies pages links from main page
	main_url = 'https://yify-movies.fun/'
	page = requests.get(main_url)
	soup = BeautifulSoup(page.content, 'html.parser')
	popular_containers = soup.findAll("div", {"class" : "mag-box-container clearfix"})[0:3]
	movie_page_links = set()
	magnets = []
	for container in popular_containers:
		a_tags = container.findAll("a")
		for a_tag in a_tags:
			movie_page_links.add(a_tag['href'])

	# Visit movie pages one by one and get magnet links
	for page_link in movie_page_links:
		movie_page = requests.get(page_link)
		soup_page = BeautifulSoup(movie_page.content, 'html.parser')
		magnet_divs = soup_page.findAll("div", {"class" : "downblockright2"})

		# Get magnet link for 1080p (fallback 720p)
		for magnet_div in magnet_divs:
			if('1080' in magnet_div.text):
				href = magnet_div.find("a")["href"]
			else:
				href = magnet_div.find("a")["href"]

		magnets.append(href)

	print("Crawling complete...")
	return magnets

magnets = crawl()
for magnet in magnets:
	downloadMovie(magnet)