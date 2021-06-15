import argparse

from utils.tools import *
from chord.chord import Node
from utils.logger import parseLevel
from utils.logger import LoggerFactory as Logger

log = Logger(name='Client')
log.setLevel('DEBUG')

def main(args):

    IP_CLIENT = args.ip
    PORT_CLIENT = args.port
    LEVEL = args.level

    client = Node(IP_CLIENT, PORT_CLIENT, LEVEL)
    client.start()
    client.ServerSocket.close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Client of a distibuted scrapper.')
    parser.add_argument('-i', '--ip', type=str, default=IP_CLIENT, help='IP for stableshing conections.')
    parser.add_argument('-p', '--port', type=int, default=PORT_CLIENT, help='PORT for stableshing conections.')
    parser.add_argument('-l', '--level', type=int, default=LEVEL, help='LEVEL for web scrapping.')

    args = parser.parse_args()
    main(args)
