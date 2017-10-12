import sys
import os.path
import socket

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class EthernetInstrument(object):
    
    def __init__(self, host, port=9876, term='\n'):
        self.term = term
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # log.info("Opening host {} port {}".format(host, int(port)))
        self.sock.connect((host, int(port)))

    def cmd(self, s, verbose=False):
        # log.debug("Sending: %s", s)
        s = s + self.term
        if verbose:
            print("EthernetInstrument.cmd(): Sending: %s" % self.make_nice_ascii(s))
        self.sock.send(s)
        resp = self.sock.recv(1024)
        while resp[-1] != self.term:
            resp += self.sock.recv(1024)
        if verbose:
            print("EthernetInstrument.cmd(): Received: %s" % self.make_nice_ascii(resp))
        
        return resp

    def close(self):
        self.sock.close()

    @staticmethod
    def make_nice_ascii(ins):
        outs = ""
        if isinstance(ins, basestring):
            for ch in ins:
                if (ord(ch) > 31) and (ord(ch) < 127):
                    outs = outs + ch
                else:
                    outs = outs + '<' + str(ord(ch)) + '>'
            return outs
        else:
            outs = "<"+str(ins)+">"
            return outs
