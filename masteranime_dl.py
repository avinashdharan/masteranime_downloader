#!/usr/bin/python
# Author : Parameshwaran B

import sys
import requests
import cfscrape
from bs4 import BeautifulSoup
import re
import subprocess

def isUrlInvalid(url):
    """
        1. Check if this is masterani.me url link
        2. URL should be anime URL and not an episode's URL
    """
    return True

def get_animeName(url):
    # URL format : https://www.masterani.me/anime/info/231-steinsgate
    scraper = cfscrape.create_scraper()
    soup = BeautifulSoup(scraper.get(url).content, 'lxml')
    script_content = soup.find_all('script')[2].string
    title_regex = re.compile('title\":"(.*)","slug')
    title = title_regex.search(script_content)
    if title:
        animeTitle = title.group(1)
    else:
        animeTitle = "UnTitle_Anime"

    return animeTitle    
    #return "Steins Gate"

def get_episodeName(url):
    # URL format : https://www.masterani.me/anime/info/231-steinsgate
    scraper = cfscrape.create_scraper()
    soup = BeautifulSoup(scraper.get(url).content, 'lxml')
    script_content = soup.find_all('script')[2].string
    ep_title_regex = re.compile('"type":([0-9]+),"title":"(.*)","duration')
    ep_title = ep_title_regex.search(script_content)
    if ep_title:
        episodeTitle = ep_title.group(2)
    else:
        episodeTitle = "UnTitle_Episode"

    return episodeTitle 

def get_no_of_Episodes(url):
    # episode_length
    """
        Cloud Flare does NOT allow script request as a DDoS prevention mechanism.
        Use Cloud Flare Scrape package to work around that.
    """
    #print "Get no of episodes in " + url
    scraper = cfscrape.create_scraper()
    soup = BeautifulSoup(scraper.get(url).content, 'lxml')
    script_content = soup.find_all('script')[2].string
    #for script_content in soup.find_all('script'):
    #    print script_content.contents
    ep_regex = re.compile('episode_length\":([0-9]+)}')
    ep_len = ep_regex.search(script_content)
    if ep_len:
        no_of_ep = int(ep_len.group(1))
    else:
        no_of_ep = 0

    return no_of_ep

def get_animeUrl(url):
    # Input  URL format : https://www.masterani.me/anime/info/231-steinsgate
    # Output URL format : https://www.masterani.me/anime/watch/231-steinsgate/
    animeURL = re.sub(r'\/info\/', "/watch/", url)

    # Append a "/" if there isn't one already.
    if (False == animeURL.endswith("/")):
        animeURL += "/"

    return animeURL
    #return "https://www.masterani.me/anime/watch/231-steinsgate/"

def get_dl_url_for_ep(url):
    # Input URL format : https://www.masterani.me/anime/watch/231-steinsgate/1
    # DL    URL format : https://aika.masterani.me/v/p3RKei533Qq3WjhY/1080

    """
        1. Get the source of input URL
        2. search for "https://aika.masterani.me/v/"
        3. return URL after appending "/1080" or "/480" depending on request
            3.1. For now always use HD until we provide user input option for quality.
    """
    #print url
    scraper = cfscrape.create_scraper()
    soup = BeautifulSoup(scraper.get(url).content, 'lxml')
    script_content = soup.find_all('script')[5].string

    # Gets HD link
    link_pattern = re.compile('https.*1080')
    # Gets SD link
    #link_pattern = re.compile('https.*480')
    ep_link = link_pattern.search(script_content)

    if ep_link:
        ep_hd_link = ep_link.group()
        #print ep_hd_link
        #ep_sd_link = ep_link.groups()[1]
        #print ep_sd_link
    else:
        ep_hd_link = ""
        #print "No Downloadable URL found for " + url

    return ep_hd_link


def download_episode(url, episodeName):
    ep_dl_url = get_dl_url_for_ep(url)
    if (0 != len(ep_dl_url)):
        # Download the video now to current working directory 
        # until a user option is given to specify a directory of choice
        print "Downloading " + episodeName + " from " + ep_dl_url
        wget = subprocess.Popen(['wget','--continue','-O', episodeName, ep_dl_url])
        wget.wait()
    else:
        print "No downloadable URL found for " + url


def download_Anime(url):
    # Function to download all episodes 

    # Base URL for download
    dl_url_base = get_animeUrl(url)

    # Find no of episodes in this anime
    # No of episodes is not scrapable from main page. So scraping from first episode link for now.
    no_of_ep = get_no_of_Episodes(dl_url_base + str(1))

    # Anime name & No of episodes can be scraped in a single request. Optimize it.
    animeName = get_animeName(dl_url_base + str(1))

    print "Anime          : " + animeName
    print "No of episodes : " + str(no_of_ep)

    """
        TODO
            1. download directory should be user choice
            2. If not, Create a directory in the name of anime being downloaded instead of using pwd
            3. Handle Seasons as well - Create a directory per season?
                Each season has a separate link in masterani.me. So leave it upto the user.
            4. Get video extension for each episode instead of assuming it as mp4
            5. Support parallel downloading of episodes
            6. download accelerator support (anything other than wget for faster download)
            7. Make sure this script is portable.
    """

    for i in range(no_of_ep):
        ep_url = dl_url_base + str(i+1)
        # Maybe we need to add season prefix
        # Need to find video extension - get_episodeVideoExtension(ep_url)
        ep_Name = str(i+1) + "_" + get_episodeName(ep_url) + ".mp4"
        download_episode(ep_url, ep_Name)


def main():
    if len(sys.argv) == 2:
        url = sys.argv[1]
        # Check if URL is valid
        if (False == isUrlInvalid(url)):
            print "Invalid URL " 
            sys.exit(1)
        
        download_Anime(url)
    else:
        print "usage : masteranime_dl.py <url>"
        # Example usage : ./masteranime_dl.py https://www.masterani.me/anime/watch/231-steinsgate
        sys.exit(1)



if __name__ == '__main__':
    main()
