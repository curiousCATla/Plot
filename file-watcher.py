import json
import os
import sys
import time
from datetime import datetime

from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from multiple_line import MultipleLines
from parallel_bar import ParallelBars


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
      self.lastJson = json.load(f)
      f.close()
    except:
      self.lastJson = json.loads('{}')
  
  def work(self, path):
    try:
      f = open(path, 'r')
      config = json.load(f)
      
      if ordered(self.lastJson) == ordered(config):
        return
      self.lastJson = config
      
      if not os.path.exists('back'):
        os.makedirs('back')
      
      fout = open('back/%s.json' % datetime.now().strftime('%Y-%B-%d-%H-%M-%S'), 'w')
      fout.write(json.dumps(config, indent=4, sort_keys=True))
      fout.close()
      
      type = config.get('type', None)
      if type == 'parallel_bars':
        ParallelBars().draw(config)
      elif type == 'multiple_lines':
        MultipleLines().draw(config)
      else:
        raise Exception("Please specify type in json. Supported: parallel_bars, multiple_lines")
    except Exception as e:
      print(e)
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


if __name__ == "__main__":
  path = sys.argv[1] if len(sys.argv) > 1 else '.'
  event_handler = MyHandler()
  observer = Observer()
  observer.schedule(event_handler, path, recursive=False)
  observer.start()
  try:
    while True:
      time.sleep(1)
  except KeyboardInterrupt:
    observer.stop()
  observer.join()
