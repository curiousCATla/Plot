# coding=utf-8
import ast
import json

import numpy as np
import matplotlib.pyplot as plt
import os
import copy

# 用于比较S个solution的某性能指标随着过程量P变化的趋势. 不同的性能指标放在不同的图上. x轴是过程量 (比如时间), y轴是性能指标 (比如throughput或overhead)

data = {
  'type': "multiple_lines",
  'figWidth': 6,
  'figHeight': 3.5,
  
  'solutionList': ('MDT', 'AODV'),
  'xTitle': 'Time (s)',
  
  'legendLoc': 'best',
  'legendColumn': 1,
  
  'markersize': 8,
  'linewidth': 2,
  
  'xLog': False,
  'xGrid': False,
  'yLog': False,
  'yGrid': False,
  
  'children': [
    {
      'name': 'signalingReceiveCnt',
      'figTitle': "",
      'yTitle': 'Signaling Receive Count',
      'x': [1, 2, 3, 4, 5, 6, 7, ],
      'y': [[300, 200, 100, 200, 300, 200, 100, ],
            [100, 300, 200, 100, 200, 300, 200, ]]
    },
    {
      'name': 'signalingReceiveAmount',
      'yTitle': 'Signaling Receive Amount',
      'yLog': True,
      'x': [1, 2, 3, 4, 5, 6, 7, ],
      'y': [[300, 200, 100, 200, 300, 200, 100, ],
            [100, 300, 200, 100, 200, 300, 200, ]],
      'yRange': [
        [[300 - 10, 300 + 10], [200 - 10, 200 + 10], [100 - 10, 100 + 10], [200 - 10, 200 + 10], [300 - 10, 300 + 10],
         [200 - 10, 200 + 10], [100 - 10, 100 + 10], ],
        [[100 - 10, 100 + 10], [300 - 10, 300 + 10], [200 - 10, 200 + 10], [100 - 10, 100 + 10], [200 - 10, 200 + 10],
         [300 - 10, 300 + 10], [200 - 10, 200 + 10], ]],
    },
    {
      'name': 'signalingSendCnt',
      'yTitle': 'Signaling Send Cnt',
      'x': [1, 2, 3, 4, 5, 6, 7, ],
      'y': [[300, 200, 100, 200, 300, 200, 100, ],
            [100, 300, 200, 100, 200, 300, 200, ]]
    },
    {
      'name': 'signalingSendAmount',
      'yTitle': 'Signaling Send Amount',
      'x': [1, 2, 3, 4, 5, 6, 7, ],
      'y': [[300, 200, 100, 200, 300, 200, 100, ],
            [100, 300, 200, 100, 200, 300, 200, ]]
    }
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


class MultipleLines:
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
      
      yRange = get('yRange', None)
      y = plotData['y']
      
      if nonEmptyIterable(yRange):
        yerror = np.zeros((len(solList), 2, len(y[0])))
        for r in range(len(solList)):
          for c in range(len(y[r])):
            yerror[r][0][c] = y[r][c] - yRange[r][c][0]  # lower
            yerror[r][1][c] = yRange[r][c][1] - y[r][c]  # upper
      
      colors = get('mainColors', ['C%d' % (i % 10) for i in range(len(solList))])
      markers = get('markers',
                    ["+", "x", "X", "o", "v", "^", "<", ">", "1", "2", "3", "4", "8", "s", "p", "P", "*", "h",
                     "H", "D", "d", "|", "_", ])
      styles = ['solid', 'dashed', 'dashdot', 'dotted']
      linestyles = get('linestyles', [styles[i % len(styles)] for i in range(len(solList))])
      for i in range(len(solList)):
        ax.errorbar(get('x'), get('y')[i], color=colors[i], capsize=5, elinewidth=1,
                    marker=markers[i] if yRange is None else None,
                    markersize=get('markersize', 8) if yRange is None else None,
                    linestyle=linestyles[i], linewidth=get('linewidth', 2),
                    label=solList[i], ecolor='r', yerr=yerror[i] if nonEmptyIterable(yRange) else None)
      
      handles, labels = ax.get_legend_handles_labels()
      
      lastAndInd = list(zip((get('y')[i][-1] for i in range(len(solList))), range(len(solList))))
      lastAndInd.sort(reverse=True)
      
      handles = [handles[lastAndInd[i][1]] for i in range(len(solList))]
      labels = [labels[lastAndInd[i][1]] for i in range(len(solList))]
      
      ax.legend(handles, labels, fancybox=True, shadow=True, loc=get('legendLoc', 'best'), fontsize='12',
                ncol=get('legendColumn', 1))
      
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
      
      lim = get('yLimit', [])
      if len(lim) > 0: plt.ylim(lim)
      
      lim = get('xLimit', [])
      if len(lim) > 0: plt.xlim(lim)
      
      plt.tight_layout()
      
      if get('display', True):
        plt.show()
        
      if get('output', False):
        plt.savefig('dist/' + name + '.eps', format='eps', dpi=1000)


if __name__ == '__main__':
  MultipleLines().draw(data)
