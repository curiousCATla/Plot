import ast
import json
import socketserver

from plot import Ploter


class MyTCPHandler(socketserver.StreamRequestHandler):
  mem = ""
  
  def handle(self):
    # self.rfile is a file-like object created by the handler;
    # we can now use e.g. readline() instead of raw recv() calls
    data = self.rfile.readline().strip().decode("utf-8")
    # Likewise, self.wfile is a file-like object used to write back
    # to the client
    self.mem += data
    
    try:
      data = None
      try:
        data = json.loads(self.mem)
      except:
        data = ast.literal_eval(self.mem)
      
      if data:
        mem = self.mem
        self.mem = ""
        Ploter().plot(data)
    except:
      pass


if __name__ == "__main__":
  HOST, PORT = "localhost", 8848
  
  # Create the server, binding to localhost on port 9999
  with socketserver.TCPServer((HOST, PORT), MyTCPHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
