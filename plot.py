import json, ast, sys
from multiple_line import MultipleLines
from parallel_bar import ParallelBars
from cdf import Cdf

forth = [114, 83]
third = [173, 122]
half = [238, 109]


class Ploter:
  def plot(self, data):
    if isinstance(data, str):
      try:
        data = json.loads(data)
      except:
        try:
          data = ast.literal_eval(data)
        except:
          raise Exception("Please input a valid json or python object string")
    
    if not isinstance(data, dict):
      raise Exception("Please input a valid json or python object string, or an object")
    
    type = data.get('type', None)
    if type == 'parallel_bars':
      ParallelBars().draw(data)
    elif type == 'multiple_lines':
      MultipleLines().draw(data)
    elif type == 'cdf':
      Cdf().draw(data)
    else:
      raise Exception("Please specify type in json. Supported: parallel_bars, multiple_lines, cdf")
