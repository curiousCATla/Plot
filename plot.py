import json, ast, sys, os

import matplotlib
from matplotlib.font_manager import FontProperties

import matplotlib.pyplot as plt

fontProp = FontProperties(fname="./LinLibertine_R.ttf")

plt.rc('text', usetex=True)
matplotlib.rcParams.update({
  'text.latex.preamble': "\\usepackage{libertine}\n\\usepackage[libertine]{newtxmath}\n\\usepackage{sfmath}\n\\usepackage[T1]{fontenc}",
  'pdf.fonttype': 42,
  'ps.fonttype': 42,
  'font.family': fontProp.get_name(),  # fontProp.get_name(),
  'text.usetex': True,
  # 'font.serif': ['Times New Roman Bold', 'FreeSerifBold'],
})
# matplotlib.font_manager._rebuild()

from multiple_line import MultipleLines
from parallel_bar import ParallelBars
from annotated_bar import AnnotatedBars
from violin import Violin
from cdf import Cdf
from heatmap import HeatMap
import rapidjson
import copy

if not os.path.exists('dist'):
  os.makedirs('dist')

if not os.path.exists('back'):
  os.makedirs('back')
  
forth = [114, 83]
third = [173, 122]
half = [238, 109]

from datetime import datetime


def nonEmptyIterable(obj):
  """return true if *obj* is iterable"""
  try:
    var = obj[0]
    return True
  except:
    return False


class Ploter:
  def plot(self, data, fig=None, ax=None):
    fout = open('../plot/back/%s.json' % datetime.now().strftime('%Y-%B-%d-%H-%M-%S'), 'w')
    fout.write(data if isinstance(data, str) else rapidjson.dumps(data))
    fout.close()

    def work(data):
      if isinstance(data, str):
        try:
          data = rapidjson.loads(data)
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
      elif type == 'violin':
        Violin().draw(data, fig, ax)
      elif type == 'heatmap':
        HeatMap().draw(data, fig, ax)
      else:
        raise Exception("Please specify type in json. Supported: bar, line, cdf")

    if nonEmptyIterable(data):
      for d in data:
        work(d)
    else:
      work(data)
