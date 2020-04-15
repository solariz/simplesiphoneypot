import StringIO, re
import SocketServer, sys, logging
import os, subprocess, requests
#from termcolor import colored

USER_AGENT = "Asterix PBX"


class HoneyUDPHandler(SocketServer.BaseRequestHandler):
    """
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """



    def handle(self):
        data = self.request[0].strip()
        socket = self.request[1]
        # Further limiting the string to valid ACSII
        rematch = re.match("([A-Z]+) ([^ ]+) ?.*", data)
        if not rematch:
            print "Unexpected UDP input from {}".format(self.client_address[0])
            return
        method = rematch.group(1)
        url = rematch.group(2)
        # Fake Reply
        if method == 'OPTIONS':
            resp = 'SIP/2.0 200 OK\n'
            rheaders = {}
            #rheaders['To'] += ';tag=' + uuid.uuid4().hex
            rheaders['Allow'] = 'INVITE, ACK, BYE, CANCEL, OPTIONS, MESSAGE, SUBSCRIBE, NOTIFY, INFO'
            rheaders['User-Agent'] = USER_AGENT
            logging.info('OPTIONS from {}'.format(self.client_address[0]))
            logging.debug('REQUEST: "{}"'.format(data))
            print "OPTIONS from {}".format(self.client_address[0])
            report(self.client_address[0],method)
        elif method == 'REGISTER':
            resp = 'SIP/2.0 200 OK\n'
            rheaders['User-Agent'] = USER_AGENT
            logging.info('REGISTER from {}'.format(self.client_address[0]))
            logging.debug('REQUEST: "{}"'.format(data))
            print "REGISTER from {}".format(self.client_address[0])
            report(self.client_address[0],method)
        elif method == 'INVITE':
            #resp = 'SIP/2.0 501 Not Implemented\n'
            resp = 'SIP/2.0 433 Anonymity Disallowed\n'
            rheaders = {}
            rheaders['User-Agent'] = USER_AGENT
            logging.info('INVITE from {}'.format(self.client_address[0]))
            logging.debug('REQUEST: "{}"'.format(data))
            print "INVITE from {}".format(self.client_address[0])
            report(self.client_address[0],method)
        elif (method == 'ACK' or method == 'BYE'):
            resp = 'SIP/2.0 200 OK\n'
            rheaders = {}
            rheaders['User-Agent'] = USER_AGENT
            logging.info('ACK from {}'.format(self.client_address[0]))
            logging.debug('REQUEST: "{}"'.format(data))
            print "ACK from {}".format(self.client_address[0])        
        else:
            resp = 'SIP/2.0 501 Not Implemented\n'
            rheaders = {}
        # Assemble response
        for k in rheaders:
            resp += '{}: {}\n'.format(k, rheaders[k])
            socket.sendto(resp, self.client_address)

def report(hostip,method):
    # reporting online
    url = 'https://dev.mgz.de/honeypot/honeysip.php'
    myobj = {'host': hostip, 'method': method}
    x = requests.post(url, data = myobj)
    print(x.text)

# Please do not run as root
if os.geteuid() is 0:
    print "This honepot should not run as root."
    sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(filename='honeysip.log',level=logging.DEBUG,format='%(asctime)s %(message)s')
    HOST, PORT = "0.0.0.0", 5060
    logging.debug('Starting HONEYSIP')
    print "Listening UDP/5060..."
    server = SocketServer.UDPServer((HOST, PORT), HoneyUDPHandler)
    server.serve_forever()

