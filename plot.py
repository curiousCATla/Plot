import json, ast, sys

import matplotlib
from matplotlib.font_manager import FontProperties

try:
  del matplotlib.font_manager.weight_dict['roman']
except:
  pass

import matplotlib.pyplot as plt
# plt.rc('text', usetex=True)
matplotlib.rcParams.update({
  'font.family': 'serif',
  'font.serif': ['Times New Roman Bold', 'FreeSerifBold'],
})
matplotlib.font_manager._rebuild()

from multiple_line import MultipleLines
from parallel_bar import ParallelBars
from annotated_bar import AnnotatedBars
from cdf import Cdf

forth = [114, 83]
third = [173, 122]
half = [238, 109]


class Ploter:
  def plot(self, data, fig=None, ax=None):
    if isinstance(data, str):
      try:
        data = json.loads(data)
      except Exception as e1:
        try:
          data = ast.literal_eval(data)
        except Exception as e2:
          print(e1)
          print(e2)
          raise Exception("Please input a valid json or python object string")

    if not isinstance(data, dict):
      raise Exception("Please input a valid json or python object string, or an object")

    plt.rc('text', usetex=data.get('usetex', False))

    type = data.get('type', None)
    if type == 'bar':
      ParallelBars().draw(data, fig, ax)
    elif type == 'line':
      MultipleLines().draw(data, fig, ax)
    elif type == 'cdf':
      Cdf().draw(data, fig, ax)
    elif type == 'annotated_bar':
      AnnotatedBars().draw(data, fig, ax)
    else:
      raise Exception("Please specify type in json. Supported: bar, line, cdf")
