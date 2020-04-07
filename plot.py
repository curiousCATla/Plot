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
from violin import Violin
from cdf import Cdf
import rapidjson
import copy

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


data = {
  # all properties are hierarchical
  'type': "bar",
  'figWidth': 600,
  'figHeight': 350,
  'mainColors': ['#0072bc',
                 '#d95218',
                 '#edb021',
                 '#7a8cbf',
                 '#009d70',
                 '#979797',
                 '#53b2ea'],
  
  'xLog': False,
  'xGrid': False,
  'xFontSize': 20,
  'xTickRotate': False,
  
  'yLog': False,
  'yGrid': False,
  'yFontSize': 20,
  
  'legendLoc': 'best',
  'legendColumn': 1,
  
  'markerSize': 8,
  'lineWidth': 2,
  
  "componentFontSize": 6,   # only for annotated bar
  
  'legendFontSize': 12,
  'output': False,
  
  "parent": None,  # 每个节点都有一个parent, 只是根节点能确定parent是None, 其余的不能现在赋值
  
  # separate figures.
  # 如果没有这一项, 就把当前dict作为唯一的一个figure
  "figures": [
    {
      'name': 'test_figure_1',
      
      'column': 2,  # 一行有几个
      'xPadding': 5,
      'yPadding': 5,
  
      # subfigures 一张图, 分几块画. 按个数分配长宽. 也可以自定义长宽
      # 如果没有这一项, 就把当前dict作为唯一的一个subfigure
      "subfigures": [
        {
          'type': "bar",
          'solutionList': ('VERID', 'AAR', 'IntegriDB'),
          'xLog': True,
          
          'groupWidth': 0.7,  # 由最近的两个数据点的x坐标算出group最大可占的宽度. group的最终宽度是 group的最大宽度*groupWidth. 对数坐标自动支持.
          'barWidth': 0.8,  # 由group的最终宽度知每个bar的最大宽度. 然后每个bar的最终宽度是 bar的最大宽度*barWidth
          
          # 这一个subfigure可以有好几层, 比如一层bar一层line
          # 如果没有这一项, 就把当前dict作为唯一的一个layer
          'layers': [
            {
              'xTicks&Labels': [[1024, 2048, 4096], ("1K", "2K", "4K")],
              
            }
          ]
        },
        {
          'type': "line",
          
        }
      ]
    },
    {
    
    }
  ]
}


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
      else:
        raise Exception("Please specify type in json. Supported: bar, line, cdf")
    
    if nonEmptyIterable(data):
      for d in data:
        work(d)
    else:
      work(data)
