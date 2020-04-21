import re
import socketserver, sys, logging
import os, subprocess, requests
import yaml


with open("config.yml", "r") as ymlfile:
    cfg = yaml.load(ymlfile, Loader=yaml.FullLoader)


USER_AGENT = "Asterix PBX"

class HoneyUDPHandler(socketserver.BaseRequestHandler):
    """
    self.request consists of a pair of data and client socket, and since
    there is no connection the client address must be given explicitly
    when sending data back via sendto().
    """



    def handle(self):
        #data = self.request[0].strip()
        data = self.request[0].decode('utf-8')
        socket = self.request[1]
        # Further limiting the string to valid ACSII
        rematch = re.match("([A-Z]+) ([^ ]+) ?.*", data)
        if not rematch:
            print("Unexpected UDP input from %s" % self.client_address[0])
            return
        method = rematch.group(1)
        url = rematch.group(2)
        # Fake Reply
        if method == 'OPTIONS':
            resp = 'SIP/2.0 200 OK\n'
            rheaders = {}
            rheaders['Allow'] = 'INVITE, ACK, BYE, CANCEL, OPTIONS, MESSAGE, SUBSCRIBE, NOTIFY, INFO'
            rheaders['User-Agent'] = USER_AGENT
            logging.info('OPTIONS from %s' % self.client_address[0])
            if cfg['log']['logrequest'] == True:
                logging.debug('REQUEST: "%s' % data)
            print("OPTIONS from %s" % self.client_address[0])
            report(self.client_address[0],method)
        elif method == 'REGISTER':
            resp = 'SIP/2.0 200 OK\n'
            rheaders['User-Agent'] = USER_AGENT
            logging.info('REGISTER from %s' % self.client_address[0])
            if cfg['log']['logrequest'] == True:
                logging.debug('REQUEST: "%s' % data)
            print("REGISTER from %s" % self.client_address[0])
            report(self.client_address[0],method)
        elif method == 'INVITE':
            resp = 'SIP/2.0 433 Anonymity Disallowed\n'
            rheaders = {}
            rheaders['User-Agent'] = USER_AGENT
            logging.info('INVITE from %s' % self.client_address[0])
            if cfg['log']['logrequest'] == True:
                logging.debug('REQUEST: "%s' % data)
            print("INVITE from %s" % self.client_address[0])
            report(self.client_address[0],method)
        elif (method == 'ACK' or method == 'BYE'):
            resp = 'SIP/2.0 200 OK\n'
            rheaders = {}
            rheaders['User-Agent'] = USER_AGENT
            logging.info('ACK from %s' % self.client_address[0])
            if cfg['log']['logrequest'] == True:
                logging.debug('REQUEST: "%s' % data)
            print("ACK from %s" % self.client_address[0])
        else:
            resp = 'SIP/2.0 501 Not Implemented\n'
            rheaders = {}
        # Assemble response
        for k in rheaders:
            #resp += '%s: %s\n' % k % rheaders[k]
            resp += k + ':' + rheaders[k] + '\n'
            socket.sendto(resp.encode('utf-8'), self.client_address)

def report(hostip,method):
    if cfg['report']['enabled'] == True:
        myobj = {'host': hostip, 'method': method}
        x = requests.post(cfg['report']['url'], data = myobj)

# Please do not run as root
if os.geteuid() is 0:
    print("This honepot should not run as root.")
    sys.exit(1)

if __name__ == "__main__":
    logging.basicConfig(filename=cfg['log']['logfile'],level=logging.DEBUG,format='%(asctime)s %(message)s')
    HOST, PORT = "0.0.0.0", 5060
    logging.debug('Starting HONEYSIP')
    print("Listening UDP/5060...")
    print("Logging to: " + cfg['log']['logfile'])
    if cfg['report']['enabled'] == True:
        print("Reporting to: " + cfg['report']['url'])
    server = socketserver.UDPServer((HOST, PORT), HoneyUDPHandler)
    server.serve_forever()

