import re
import urllib
import hashlib

from utils.colors import *
from utils.type_check import *
from urllib.parse import urlparse

IP_SERVER = IP_CLIENT = '127.0.0.1'
PORT_SERVER, PORT_CLIENT = 8080, 9090
LEVEL = 1
BUFFER = 4096
MAX_BITS = 100
MAX_NODES = 2 ** MAX_BITS

@type_check
def getHash(key:str) -> int:
    '''
    Takes key string, uses SHA-1 hashing and returns 
    a 10-bit (1024) compressed integer.
    '''
    result = hashlib.sha1(key.encode())
    return int(result.hexdigest(), 16) % MAX_NODES

@type_check
def checkAddress(address:str) -> bool:
    '''
    Validate the specified address (ip:port) using 
    regular expressions.
    '''
    if address is not None:
        regex = re.compile('\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,6}')
        try:
            assert regex.match(address).end() == len(address)
        except (AssertionError, AttributeError):
            return False
    return True

@type_check
def isValidURL(url:str) -> bool:
    '''
    Validate the specified url.
    '''
    try:
        result = urlparse(url)
        _ = all([ result.scheme, result.netloc, result.path ])
    except:
        return False
    return True

@type_check
def getPageName(url:str) -> str:
    '''
    Return the name of the page according to the 
    specified url.
    '''
    splitURL = url.split('/')
    fileName = splitURL[-1]
    splitFileName = fileName.split('.')
    if splitFileName[0] == 'www':
        page = splitFileName[1]
        return page
    return splitFileName[0]

@type_check
def prefixFuntion(patron:str) -> list:
    '''
    Helper function for kmp method.
    '''
    pi, k = [ 0 for _ in patron ], 0
    for i in range(2, len(patron)):
        while k>0 and patron[k+1] != patron[i]:
            k = pi[k]
        if patron[k+1] == patron[i]:
            k += 1
        pi[i] = k
    return pi

@type_check
def kmp(text:str, patron:str) -> list:
    '''
    Return the occurrences of the patron according 
    to the text.
    '''
    occurrences, k = [], 0
    pi = prefixFuntion(patron)

    for i in range(1, len(text)):
        while k>0 and text[i] != patron[k+1]:
            k = pi[k]
        if text[i] == patron[k+1]:
            k += 1
        if k == len(patron) - 1:
            k = pi[k]
            occurrences.append(i - len(patron) + 1)

    return occurrences

@type_check
def getFolderName(url:str) -> str:
    '''
    Return the name of the folder according to the 
    specified url.
    '''
    splitURL = url.split('/')
    fileName = splitURL[-1]
    splitFileName = fileName.split('.')
    if splitFileName[0] == 'www':
        folderName = '.'.join(splitFileName[1:])
        return folderName
    return fileName

@type_check
def getDomain(url:str) -> str:
    '''
    Return the domain according to the specified url.
    '''
    _, netloc, _, _, _ = urllib.parse.urlsplit(url)
    domainURL = netloc.split('.')[-2]
    return domainURL
