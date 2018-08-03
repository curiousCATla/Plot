# coding=utf-8
import ast
import json
import os

import matplotlib.pyplot as plt
import numpy as np

# 用于绘制一个或多个量的累积分布函数

data = {
  'type': "cdf",
  'figWidth': 6,
  'figHeight': 3.5,
  
  'xTitle': 'Load balancing measure',
  
  'legendLoc': 'best',
  'legendColumn': 1,
  
  'xLog': False,
  'xGrid': True,
  'yLog': False,
  'yGrid': True,
  
  'children': [
    {
      'name': 'concury-silkroad-balance-cdf',
      'figTitle': "",
      'yTitle': '',
      'solutionList': ('Concury', 'SilkRoad'),
      'x': [0, 0.1, 0.57, 0.63, 0.85, 0.92, 0.99, 1, 1.1, 1.1, 1.2, ],
      'x2': [0, 0.1, 0.57, 0.63, 0.85, 0.92, 0.99, 1, 1.1, 3.1, 3.2, ],
    },
  ]
}

if not os.path.exists('dist'):
  os.makedirs('dist')


def iterable(obj):
  return isinstance(obj, list) or isinstance(obj, tuple)


def nonEmptyIterable(obj):
  """return true if *obj* is iterable"""
  if not isinstance(obj, list) and not isinstance(obj, tuple):
    return False
  return not not len(obj)


class Cdf:
  def draw(self, data):
    if isinstance(data, str):
      try:
        data = json.loads(data)
      except:
        data = ast.literal_eval(data)
    
    for plotData in data['children']:
      name = plotData['name']
      
      def get(key, default=None):
        result = plotData.get(key, None)
        if result is not None and not iterable(result) or nonEmptyIterable(result): return result
        
        result = data.get(key, None)
        if result is not None and not iterable(result) or nonEmptyIterable(result): return result
        
        return default
      
      if not isinstance(plotData, dict): continue
      
      solList = get('solutionList')
      
      fig, ax = plt.subplots()
      fig.set_size_inches(get('figWidth'), get('figHeight'))
      
      colors = get('mainColors', ['C%d' % (i % 10) for i in range(len(solList))])
      
      minx = float("inf")
      maxx = float("-inf")
      X=[]
      for i in range(len(solList)):
        x = get('x%d' % (i + 1), get('x', ()) if i == 0 else ())
        minx = min(minx, x[0])
        maxx = max(maxx, x[-1])
        X.append(x)
      
      ax.hist(X, len(X[0]), density=1, histtype='step', cumulative=True, label=solList, color=colors[0:len(solList)])
      ax.set_ylabel(get('yTitle', ""), fontsize='x-large')
      ax.set_xlabel(get('xTitle', ""), fontsize='x-large')
      
      plt.title(get('figTitle', ""))
      
      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize('x-large')
      
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontsize('x-large')
      
      if get('xLog', False):
        ax.set_xscale('log')
      
      if get('xGrid', False):
        ax.xaxis.grid(True)
      
      if get('yLog', False):
        ax.set_yscale('log')
      
      if get('yGrid', False):
        ax.yaxis.grid(True)
      
      plt.ylim([0,1])
      
      plt.xlim([minx, maxx])
      
      plt.tight_layout()
      
      if get('output', False):
        plt.savefig('dist/' + name + '.eps', format='eps', dpi=1000)


if __name__ == '__main__':
  Cdf().draw(data)
