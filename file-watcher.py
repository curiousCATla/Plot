import rapidjson, ast
import os
import sys
import time
import traceback

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

import queue

# somewhere accessible to both:
callback_queue = queue.Queue()

from plot import Ploter


def ordered(obj):
  if isinstance(obj, dict):
    return sorted((k, ordered(v)) for k, v in obj.items())
  if isinstance(obj, list):
    return sorted(ordered(x) for x in obj)
  else:
    return obj


class MyHandler(FileSystemEventHandler):
  def __init__(self):
    try:
      f = open('last-plot-data.json', 'r')
      self.lastJson = rapidjson.load(f)
      f.close()
    except:
      self.lastJson = rapidjson.loads('{}')
  
  def work(self, path):
    try:
      f = open(path, 'r', encoding="utf-8")
      data_ = f.read()
      f.close()
      try:
        data = rapidjson.loads(data_)
      except Exception as e:
        try:
          data = ast.literal_eval(data_)
        except Exception as e2:
          raise Exception(
            "Please input a valid json or python object string\nWhy it is not a python dict: %s\nWhy it is not a JSON object: %s" % (
              e2, e))
      
      try:
        if ordered(self.lastJson) == ordered(data):
          return
      except:
        pass
      
      self.lastJson = data
      
      if not os.path.exists('back'):
        os.makedirs('back')
      
      callback_queue.put(data)
    
    except Exception as e:
      print(e, file=sys.stderr)
      traceback.print_exc()
    finally:
      try:
        f.close()
      except:
        pass
  
  def on_created(self, event):
    if os.path.normpath(event.src_path) == os.path.normpath('./last-plot-data.json'):
      self.work(event.src_path)
  
  def on_modified(self, event):
    if os.path.normpath(event.src_path) == os.path.normpath('./last-plot-data.json'):
      self.work(event.src_path)


import matplotlib.pyplot as plt

if __name__ == "__main__":
  path = sys.argv[1] if len(sys.argv) > 1 else '.'
  event_handler = MyHandler()
  observer = Observer()
  observer.schedule(event_handler, path, recursive=False)
  observer.start()
  try:
    while True:
      try:
        data = callback_queue.get(False)  # doesn't block
        Ploter().plot(data)
      except queue.Empty:  # raised when queue is empty
        pass
      try:
        plt.pause(0.5)
      except:
        pass
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
