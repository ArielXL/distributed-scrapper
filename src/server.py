import argparse

from utils.tools import *
from chord.chord import Node
from utils.logger import parseLevel
from utils.logger import LoggerFactory as Logger

log = Logger(name='Server')
log.setLevel('DEBUG')

def main(args):

    IP_SERVER = args.ip
    PORT_SERVER = args.port
    LEVEL = args.level

    server = Node(IP_SERVER, PORT_SERVER, LEVEL)
    server.start()
    server.ServerSocket.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Server of a distibuted scrapper.')
    parser.add_argument('-i', '--ip', type=str, default=IP_SERVER, help='IP for stableshing conections.')
    parser.add_argument('-p', '--port', type=int, default=PORT_SERVER, help='PORT for stableshing conections.')
    parser.add_argument('-l', '--level', type=int, default=LEVEL, help='LEVEL for web scrapping.')

    args = parser.parse_args()
    main(args)
