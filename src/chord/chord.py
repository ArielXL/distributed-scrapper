import os
import time
import pickle
import socket
import threading

from utils.tools import *
from utils.logger import parseLevel
from collections import OrderedDict
from scrapper.scrapper import Scrapper
from utils.logger import LoggerFactory as Logger

log = Logger(name='NodeChor')
log.setLevel('DEBUG')

class Node:

    def __init__(self, ip, port, level):
        if checkAddress(f'{ip}:{port}'):
            self.filenameList = set()
            self.ip = ip
            self.port = port
            self.level = level
            self.address = (ip, port)
            self.id = getHash(f'{ip}:{str(port)}')
            self.pred = (ip, port)
            self.predID = self.id
            self.succ = (ip, port)
            self.succID = self.id
            self.fingerTable = OrderedDict()

            try:
                self.ServerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.ServerSocket.bind((self.ip, self.port))
                self.ServerSocket.listen()
            except socket.error:
                log.error('Socket not opened.', 'init')
        else:
            log.error(f'Parameter address inserted is not a valid ip:port.', 'init')
            exit(1)

    def listenThread(self):
        '''
        Storing the IP and port in address and saving 
        the connection and threading.
        '''
        while True:
            try:
                connection, address = self.ServerSocket.accept()
                connection.settimeout(120)
                threading.Thread(target=self.connectionThread, args=(connection, address)).start()
            except socket.error:
                pass

    def connectionThread(self, connection, address):
        '''
        Thread for each peer connection.
        Types of connections 0 : peer connect
                             1 : client
                             2 : ping
                             3 : lookupID
                             4 : updateSucc/Pred
                             5 : updateFingerTable
        '''
        rDataList = pickle.loads(connection.recv(BUFFER))
        connectionType = rDataList[0]
        if connectionType == 0:
            print(f'Connection with: {address[0]} : {address[1]}')
            print('Join network request recevied')
            self.joinNode(connection, address, rDataList)
            self.printMenu()
        elif connectionType == 1:
            print(f'Connection with: {address[0]} : {address[1]}')
            print('Upload/Download request recevied')
            self.transferFile(connection, address, rDataList)
            self.printMenu()
        elif connectionType == 2:
            connection.sendall(pickle.dumps(self.pred))
        elif connectionType == 3:
            self.lookupID(connection, address, rDataList)
        elif connectionType == 4:
            if rDataList[1] == 1:
                self.updateSucc(rDataList)
            else:
                self.updatePred(rDataList)
        elif connectionType == 5:
            self.updateFingerTable()
            connection.sendall(pickle.dumps(self.succ))
        else:
            print('Problem with connection type')
    
    def joinNode(self, connection, address, rDataList):
        '''
        Deals with join network request by other node.
        '''
        if rDataList:
            peerIPport = rDataList[1]
            peerID = getHash(f'{peerIPport[0]}:{str(peerIPport[1])}')
            oldPred = self.pred
            self.pred = peerIPport
            self.predID = peerID
            sDataList = [oldPred]
            connection.sendall(pickle.dumps(sDataList))
            time.sleep(0.1)
            self.updateFingerTable()
            self.updateOtherFingerTables()

    def transferFile(self, connection, address, rDataList):
        # choice: 0 = download, 1 = upload
        choice = rDataList[1]
        filename = rDataList[2]
        fileID = getHash(filename)
        # if client wants to download file
        if choice == 0:
            print(f'Download request for file: {filename}')
            try:
                if filename not in self.filenameList:
                    connection.send('NotFound'.encode('utf-8'))
                    print('File not found')
                else:
                    connection.send('Found'.encode('utf-8'))
                    self.sendFile(connection, filename)
            except ConnectionResetError as error:
                print(error, '\nClient disconnected\n\n')
        # else if client wants to upload something to network
        elif choice == 1 or choice == -1:
            print(f'Receiving file: {filename}')
            fileID = getHash(filename)
            print(f'Uploading file ID: {fileID}')
            self.filenameList.add(filename)
            self.receiveFile(connection, filename)
            print('Upload complete')
            if choice == 1:
                if self.address != self.succ:
                    self.uploadFile(filename, self.succ, False)

    def lookupID(self, connection, address, rDataList):
        keyID = rDataList[1]
        sDataList = []

        # case 0: if keyId at self
        if self.id == keyID:
            sDataList = [ 0, self.address ]
        # case 1: if only one node
        elif self.succID == self.id:
            sDataList = [ 0, self.address ]
        # case 2: node id greater than keyId, ask pred
        elif self.id > keyID:
            if self.predID < keyID:
                sDataList = [ 0, self.address ]
            elif self.predID > self.id:
                sDataList = [ 0, self.address ]
            else:
                sDataList = [ 1, self.pred ]
        # case 3: node id less than keyId USE fingertable to search
        else:
            if self.id > self.succID:
                sDataList = [ 0, self.succ ]
            else:
                value = ()
                for key, value in self.fingerTable.items():
                    if key >= keyID:
                        break
                value = self.succ
                sDataList = [ 1, value ]
        connection.sendall(pickle.dumps(sDataList))

    def updateSucc(self, rDataList):
        newSucc = rDataList[2]
        self.succ = newSucc
        self.succID = getHash(f'{newSucc[0]}:{str(newSucc[1])}')

    def updatePred(self, rDataList):
        newPred = rDataList[2]
        self.pred = newPred
        self.predID = getHash(f'{newPred[0]}:{str(newPred[1])}')

    def start(self):
        '''
        Accepting connections from other threads.
        '''
        threading.Thread(target=self.listenThread, args=()).start()
        threading.Thread(target=self.pingSucc, args=()).start()
        # in case of connecting to other clients
        while True:
            print('Listening to other clients')
            self.asAClientThread()

    def pingSucc(self):
        while True:
            # ping every 5 seconds
            time.sleep(2)
            # if only one node, no need to ping
            if self.address == self.succ:
                continue

            try:
                pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pSocket.connect(self.succ)
                pSocket.sendall(pickle.dumps([2]))
                recvPred = pickle.loads(pSocket.recv(BUFFER))
            except:
                print('\nOffline node dedected!\nStabilizing...')
                # search for the next succ from the finger table
                newSuccFound = False
                value = ()
                for key, value in self.fingerTable.items():
                    if value[0] != self.succID:
                        newSuccFound = True
                        break
                if newSuccFound:
                    self.succ = value[1]
                    self.succID = getHash(f'{self.succ[0]}:{str(self.succ[1])}')
                    # inform new succ to update its pred to me now
                    pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    pSocket.connect(self.succ)
                    pSocket.sendall(pickle.dumps([4, 0, self.address]))
                    pSocket.close()
                else:
                    self.pred = self.address
                    self.predID = self.id
                    self.succ = self.address
                    self.succID = self.id
                self.updateFingerTable()
                self.updateOtherFingerTables()
                self.printMenu()

    def asAClientThread(self):
        '''
        Handles all outgoing connections and printing options.
        '''
        self.printMenu()
        userChoice = input()
        if userChoice == '1':
            ip = input('Enter IP to connect: ')
            port = input('Enter port to connect: ')
            try:
                self.sendJoinRequest(ip, int(port))
            except:
                pass
        elif userChoice == '2':
            self.leaveNetwork()
        elif userChoice == '3':
            self.printFingerTable()
        elif userChoice == '4':
            print(f'ID: {self.id}')
            print(f'Predecessor: {self.predID}')
            print(f'Successor: {self.succID}')
        elif userChoice == '5':
            print(f'ID: {self.id}')
            print(f'IP: {self.ip}')
            print(f'PORT: {self.port}')
            print(f'LEVEL: {self.level}')
        elif userChoice == '6':
            self.printFiles()
        elif userChoice == '7':
            url = input('Write url to web scrapping: ')
            if isValidURL(url):
                if not self.findURL(url):
                    scrapper = Scrapper()
                    pathURL = scrapper.startRequests(url, self.level)
                    if pathURL != '':
                        fileID = getHash(pathURL)
                        recvIPport = self.getSuccessor(self.succ, fileID)
                        self.uploadFile(pathURL, recvIPport, True)
                    else:
                        print(f'Not possible to scrapping this url: "{url}"')
                else:
                    print(f'URL already present: "{url}"')
            else:
                print(f'Invalid url: "{url}"')
        elif userChoice == '8':
            filename = input('Enter filename: ')
            fileID = getHash(filename)
            recvIPport = self.getSuccessor(self.succ, fileID)
            self.uploadFile(filename, recvIPport, True)
        elif userChoice == '9':
            filename = input('Enter filename: ')
            self.downloadFile(filename)
            time.sleep(3)
            # self.downloadFile(filename)

    def findURL(self, url):
        nameURL = url.split('/')[-1]
        for file in self.filenameList:
            try:
                fileSplit = file.split('/')
                nameFolder = fileSplit[-2]
                nameFile = fileSplit[-1]
                if nameURL == nameFolder and nameFile.endswith('.html'):
                    return True
            except:
                pass
        return False

    def printFiles(self):
        if len(self.filenameList) == 0:
            print('There are not files')
        else:
            for file in self.filenameList:
                print(file)

    def sendJoinRequest(self, ip, port):
        try:
            recvIPPort = self.getSuccessor((ip, port), self.id)
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            peerSocket.connect(recvIPPort)
            sDataList = [ 0, self.address ]

            peerSocket.sendall(pickle.dumps(sDataList))
            rDataList = pickle.loads(peerSocket.recv(BUFFER))
            self.pred = rDataList[0]
            self.predID = getHash(f'{self.pred[0]}:{str(self.pred[1])}')
            self.succ = recvIPPort
            self.succID = getHash(f'{recvIPPort[0]}:{str(recvIPPort[1])}')
            sDataList = [ 4, 1, self.address ]
            pSocket2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            pSocket2.connect(self.pred)
            pSocket2.sendall(pickle.dumps(sDataList))
            pSocket2.close()
            peerSocket.close()
        except socket.error:
            print('Socket error. Recheck IP/Port')
        except Exception:
            print('Invalid IP or Port. Recheck IP/Port')

    def leaveNetwork(self):
        # first inform my succ to update its pred
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.succ)
        pSocket.sendall(pickle.dumps([4, 0, self.pred]))
        pSocket.close()
        # then inform my pred to update its succ
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        pSocket.connect(self.pred)
        pSocket.sendall(pickle.dumps([4, 1, self.succ]))
        pSocket.close()
        print(f'I had files: {self.filenameList}') if len(self.filenameList) > 0 else print('I had files: { }')
        # and also replicating its files to succ as a client
        print('Replicating files to other nodes before leaving')
        try:
            for filename in self.filenameList:
                pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                pSocket.connect(self.succ)
                sDataList = [ 1, 1, filename ]
                pSocket.sendall(pickle.dumps(sDataList))
                with open(filename, 'rb') as file:
                    # getting back confirmation
                    pSocket.recv(BUFFER)
                    self.sendFile(pSocket, filename)
                    pSocket.close()
                    print('File replicate')
                pSocket.close()
        except:
            print('Not possible replicate files')
        
        self.updateOtherFingerTables()
        self.pred = (self.ip, self.port)
        self.predID = self.id
        self.succ = (self.ip, self.port)
        self.succID = self.id
        self.fingerTable.clear()
        print(self.address, 'has left the network')

    def uploadFile(self, filename, recvIPport, replicate):
        print('Uploading file:', filename)
        sDataList = [1]
        if replicate:
            sDataList.append(1)
        else:
            sDataList.append(-1)
        try:
            file = open(filename, 'rb')
            file.close()
            sDataList += [ filename ]
            cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            cSocket.connect(recvIPport)
            cSocket.sendall(pickle.dumps(sDataList))
            self.filenameList.add(filename)
            self.sendFile(cSocket, filename)
            cSocket.close()
            print('File uploaded')
        except IOError:
            print('File not in directory')
        except socket.error:
            print('Error in uploading file')

    def downloadFile(self, filename):
        print(f'Downloading file: {filename}')
        fileID = getHash(filename)
        recvIPport = self.getSuccessor(self.succ, fileID)
        sDataList = [ 1, 0, filename ]
        cSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        cSocket.connect(recvIPport)
        cSocket.sendall(pickle.dumps(sDataList))
        fileData = cSocket.recv(BUFFER)
        if fileData == b'NotFound':
            print(f'File not found: {filename}')
        else:
            print(f'Receiving file: {filename}')
            self.receiveFile(cSocket, filename, True)

    def getSuccessor(self, address, keyID):
        rDataList = [ 1, address ]
        recvIPPort = rDataList[1]
        while rDataList[0] == 1:
            peerSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                peerSocket.connect(recvIPPort)
                sDataList = [ 3, keyID ]
                peerSocket.sendall(pickle.dumps(sDataList))
                rDataList = pickle.loads(peerSocket.recv(BUFFER))
                recvIPPort = rDataList[1]
                peerSocket.close()
            except socket.error:
                print('Connection denied while getting Successor')
                return
        return recvIPPort

    def updateFingerTable(self):
        for i in range(MAX_BITS):
            entryId = (self.id + (2 ** i)) % MAX_NODES
            if self.succ == self.address:
                self.fingerTable[entryId] = (self.id, self.address)
                continue
            recvIPPort = self.getSuccessor(self.succ, entryId)
            recvId = getHash(f'{recvIPPort[0]}:{str(recvIPPort[1])}')
            self.fingerTable[entryId] = (recvId, recvIPPort)

    def updateOtherFingerTables(self):
        here = self.succ
        while True:
            if here == self.address:
                break
            pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                pSocket.connect(here)
                pSocket.sendall(pickle.dumps([5]))
                here = pickle.loads(pSocket.recv(BUFFER))
                pSocket.close()
                if here == self.succ:
                    break
            except socket.error:
                print('Connection denied')

    def sendFile(self, connection, filename):
        print('Sending file:', filename)
        try:
            with open(filename, 'rb') as file:
                data = file.read()
                print('File size:', len(data))
                fileSize = len(data)
        except:
            print('File not found')
        try:
            with open(filename, 'rb') as file:
                while True:
                    fileData = file.read(BUFFER)
                    time.sleep(0.001)
                    if not fileData:
                        break
                    connection.sendall(fileData)
        except:
            pass
        print('File sent')

    def receiveFile(self, connection, filename, flag=False):
        '''
        Receiving file in parts if file already in directory.
        '''
        name = filename.split('/')[-1]
        filename = f'downloads/files/{name}'
        fileAlready = flag
        try:
            with open(filename, 'rb') as file:
                data = file.read()
                size = len(data)
                if size == 0:
                    print('Retransmission request sent')
                    fileAlready = True
                else:
                    print('File already present')
                    fileAlready = False
        except FileNotFoundError:
            pass

        if fileAlready:
            totalData = b''
            recvSize = 0
            try:
                with open(filename, 'wb') as file:
                    while True:
                        fileData = connection.recv(BUFFER)
                        recvSize += len(fileData)
                        if not fileData:
                            break
                        totalData += fileData
                    file.write(totalData)
            except ConnectionResetError:
                print('Data transfer interupted')
                print('Waiting for system to stabilize')
                print('Trying again in 10 seconds')
                time.sleep(5)
                os.remove(filename)
                time.sleep(5)
                self.downloadFile(filename)

    def printMenu(self):
        print('\nChoose an option:\n1. Join network\n2. Leave network')
        print('3. Print finger table\n4. Print my predecessor and successor')
        print('5. Print IP, PORT and LEVEL\n6. Print files on the network')
        print('7. Make web scrapping\n8. Upload file\n9. Download file\n')

    def printFingerTable(self):
        print('Printing Finger Table')
        for key, value in self.fingerTable.items(): 
            print(f'KeyID: {key}, Value: {value}')
