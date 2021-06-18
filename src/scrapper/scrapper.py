import os
import time
import queue
import requests
import urllib.request

from re import match
from utils.tools import *
from bs4 import BeautifulSoup
from utils.type_check import *
from utils.logger import parseLevel
from utils.logger import LoggerFactory as Logger

log = Logger(name='Scrapper')
log.setLevel('DEBUG')

class Scrapper():

    @type_check
    def getHTML(self, url:str) -> bytes:
        wait = 0
        while True:
            try:
                log.info(f'GET {url}', 'getHTML')
                # with requests.get(url) as response:
                #     html = response.text
                with urllib.request.urlopen(url) as response:
                    html = response.read()
                break
            except Exception:
                log.error(f'An error ocurred when try to get {url}', 'getHTML')

                if wait == 2:
                    log.error(f'Download failed: {url}', 'getHTML')
                    return b'ERROR'

                log.info(f'Trying again in {2 ** wait} seconds', 'getHTML')
                time.sleep(2 ** wait)
                wait = wait + 1
        return html

    @type_check
    def getLink(self, link:str) -> bytes:
        wait = 0
        while True:
            try:
                log.info(f'GET {link}', 'getLink')
                with urllib.request.urlopen(link) as response:
                    html = response.read()
                break
            except Exception:
                log.error(f'An error ocurred when try to get {link}', 'getLink')

                if wait == 2:
                    log.error(f'Download failed: {link}', 'getLink')
                    return b'ERROR'

                log.info(f'Trying again in {2 ** wait} seconds', 'getLink')
                time.sleep(2 ** wait)
                wait = wait + 1
        return html

    @type_check
    def startRequests(self, url:str, level:int) -> str:

        folderName = getFolderName(url)
        html = self.getHTML(url)
        if html == b'ERROR':
            log.error(f'Not possible to scrapping this url: "{url}"', 'startRequests')
            return ''

        try:
            domainURL = getDomain(url)
            soupHTML = BeautifulSoup(html, 'lxml')
            baseURL = self.formURL(url)
            soupTag = soupHTML.find_all(self.extractTags)

            for idx in range(len(soupTag)):
                if soupTag[idx].has_attr('href'):
                    name = self.putName(soupTag[idx]['href'])
                    soupTag[idx]['href'] = name

                if soupTag[idx].has_attr('src'):
                    name = self.putName(soupTag[idx]['src'])
                    soupTag[idx]['src'] = name

            direction = os.path.join('downloads', 'urls', folderName)
            page = f'{getPageName(url)}.html'
            if not os.path.isdir(direction):
                os.makedirs(direction)

            with open(os.path.join(direction, page), 'wb') as fileHTML:
                fileHTML.write(soupHTML.prettify(formatter='html').encode('utf-8'))
        except:
            log.error(f'Not possible to scrapping this url: "{url}"', 'startRequests')
            return ''

        countLevel = 0
        queueHTML = queue.Queue()
        queueHTML.put(url)
        listURL = [ url ]

        while not queueHTML.empty():
            countLevel += 1
            url = queueHTML.get()
            html = self.getHTML(url)
            if html == b'ERROR':
                return ''

            baseURL = self.formURL(url)
            soup = BeautifulSoup(html, 'lxml')
            links = []
            soupTag = soup.find_all(self.extractTags)

            for idx in range(len(soupTag)):
                if soupTag[idx].has_attr('href'):
                    name = self.putName(soupTag[idx]['href'])
                    links.append((urllib.parse.urljoin(baseURL, soupTag[idx]['href']), name))
                    soupTag[idx]['href'] = name

                if soupTag[idx].has_attr('src'):
                    name = self.putName(soupTag[idx]['src'])
                    links.append((urllib.parse.urljoin(baseURL, soupTag[idx]['src']), name))
                    soupTag[idx]['src'] = name

            for (tag_url, name_url) in links:
                scheme, netloc, path, query, fragment = urllib.parse.urlsplit(tag_url)
                path = urllib.parse.unquote(path)
                link = urllib.parse.urlunsplit((scheme, netloc, path, query, fragment))
                
                if not link in listURL:
                    html = self.getLink(link)

                    if link.endswith('.html') and countLevel < level and self.isDomain(domainURL, link):
                        queueHTML.put(link)

                    try:                    
                        with open(os.path.join('downloads', 'urls', folderName, name_url), 'wb') as fileHTML:
                            listURL.append(link)
                            fileHTML.write(html)
                    except:
                        pass

        pathURL = os.path.join('downloads', 'urls', folderName, page)
        return pathURL

    @type_check
    def isDomain(self, domain:str, link:str) -> bool:
        domainLink = getDomain(link)
        return domain == domainLink

    @type_check
    def extractTags(self, tag):
        return (tag.has_attr('href') and (match(r'.*\.php', tag['href']) 
          or match(r'.*\.css', tag['href']) or match(r'.*\.js', tag['href']) 
            or match(r'.*\.jpg', tag['href']) or match(r'.*\.html', tag['href']) 
              or match(r'.*\.png', tag['href']))) or (tag.has_attr('src') 
                and (match(r'.*\.php', tag['src']) or match(r'.*\.css', tag['src']) 
                  or match(r'.*\.js', tag['src']) or match(r'.*\.jpg', tag['src']) 
                    or match(r'.*\.html', tag['src']) or match(r'.*\.png', tag['src'])))

    @type_check
    def putName(self, name:str) -> str:
        splitName = name.replace('?', '').replace('=', '').split('/')
        splitName = splitName[max(0, len(splitName) - 4):]
        return '-'.join(splitName)

    @type_check
    def formURL(self, url:str) -> str:
        splitURL = url.split('/')
        if splitURL[0] == 'file:':
            return '/'.join(splitURL[0:])
        else:
            return '/'.join(splitURL[0:3])
