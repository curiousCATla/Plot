# coding=utf-8
import sys
import threading

import Pyro4
import Pyro4.naming

from plot import Ploter

with Pyro4.core.Daemon() as daemon:
  class NameServer(threading.Thread):
    def __init__(self, hostname, hmac=None):
      super(NameServer, self).__init__()
      self.setDaemon(True)
      self.hostname = hostname
      self.hmac = hmac
      self.started = threading.Event()
    
    def run(self):
      self.uri, self.ns_daemon, self.bc_server = Pyro4.naming.startNS(self.hostname, hmac=self.hmac)
      self.started.set()
      if self.bc_server:
        self.bc_server.runInThread()
      self.ns_daemon.requestLoop()
  
  
  def startNameServer(host, hmac=None):
    ns = NameServer(host, hmac=hmac)
    ns.start()
    ns.started.wait()
    return ns
  
  
  startNameServer("localhost")
  ns = Pyro4.naming.locateNS()
  
  obj = Ploter()
  uri = daemon.register(obj)
  ns.register("space.shouqianshi.utils.ploter", uri)
  
  print("server started")
  
  daemon.requestLoop()
