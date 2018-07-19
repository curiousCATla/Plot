# coding=utf-8
import ast
import json

import numpy as np
import matplotlib.pyplot as plt
import os
import copy

# 提供break_down功能, 用于不同solution在相同条件下的性能细致分析
# 每个solution的性能指标可能有不同的分量, 把分量分开画为不同的颜色
# 如果不同solution的分量分解相同, 而且仅有一个environment, 可以不用颜色和图例区分不同solution, 否则颜色和图例会很多

data = {
  'type': "breakdown_bars",
  'figWidth': 6,
  'figHeight': 3.5,
  'mainColors': ['#0072bc', '#d85119', '#edb021'],
  
  'solutionList': ('VERID', 'AAR', 'IntegriDB'),
  'componentList': ("Initialize", "Exit"),
  
  'legendLoc': 'upper center',
  'legendColumn': 3,
  
  'yLog': False,
  'yGrid': False,
  
  'paddingLeft': 0.2,
  'paddingRight': 0,
  
  'margin': 0.4,
  'marginInner': 0.02,
  
  'children': [
    {
      'name': "insertion",
      'xTitle': '',
      'yTitle': 'Insertion time (ms)',
      'legendLoc': 'upper left',
      'yLimit': [0, 0.8],
      'y': (
        (0.011, 0.203),
        (0.428, 0.220),
        (0.161, 0.513)
      ),
      'yRange': (
        ([0.009, 0.02], [0.1, 0.25]),
        ([0.428, 0.428], [0.220, 0.220]),
        ([0.161, 0.161], [0.513, 0.513])
      ),
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


class BreakdownBars:
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
      
      envList = get('environmentList')
      solList = get('solutionList')
      
      groupWidth = 1 - get('margin')
      ind = np.arange(len(envList))  # the x locations for the groups
      width = groupWidth / len(solList) - get('marginInner')  # the width of the bars
      
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
      rects = []
      for i in range(len(solList)):
        rects.append(
          ax.bar(ind + width * i + get('marginInner') / 2, y[i], width - get('marginInner'), color=colors[i],
                 ecolor='r', yerr=yerror[i] if nonEmptyIterable(yRange) else None))
      
      ax.set_xticks(ind + width * len(solList) / 2)
      ax.set_xticklabels(get('environmentList'), fontsize='x-large')
      
      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontsize('x-large')
      
      plt.xlim(
        [0 - groupWidth / 2 - get('paddingLeft'), 1 + len(solList) * width + groupWidth / 2 + get('paddingRight')])
      ax.legend((rect[0] for rect in rects), solList, fancybox=True, shadow=True,
                loc=get('legendLoc', 'best'), fontsize='12', ncol=get('legendColumn', len(solList)))
      
      ax.set_ylabel(get('yTitle'), fontsize='x-large')
      ax.set_xlabel(get('xTitle'), fontsize='x-large')
      
      if get('xLog', False):
        ax.set_xscale('log')
      
      if get('yLog', False):
        ax.set_yscale('log')
      
      if get('yGrid', False):
        ax.yaxis.grid(True)
      
      lim = get('yLimit', [])
      if len(lim) == 2: plt.ylim(lim)
      
      def autoLabel(rects, yHeighestOfRects):
        """
        Attach a text label above each bar displaying its height
        """
        yLog = get('yLog', False)
        
        ylim = ax.get_ylim()
        if yLog and ylim[0] <= 0:
          raise Exception("ylim must > 0 when y is logarithmic")
        unit = ((ylim[1] / ylim[0]) ** (1 / 60.0) if yLog else (ylim[1] - ylim[0]) / 60)
        
        for rect, yHeighestOfRects in zip(rects, yHeighestOfRects):
          height = rect.get_height()
          truncated = (height * unit ** 2 if yLog else height + unit * 2) >= ylim[1]
          
          if yLog:
            yLabelPos = yHeighestOfRects * unit if not truncated else ylim[1] / unit ** 12
          else:
            yLabelPos = yHeighestOfRects + unit if not truncated else ylim[1] - unit * 12
          
          ax.text(rect.get_x() + rect.get_width() / 2 if not truncated else rect.get_x() + rect.get_width() * 1.05,
                  yLabelPos, "%.2f" % height if not truncated else '%d' % height,
                  ha='center' if not truncated else 'left',
                  va='bottom', fontsize='small')
      
      for i in range(len(rects)):
        autoLabel(rects[i], (yRange[i][j][1] for j in range(len(envList))) if nonEmptyIterable(yerror) else y[i])
      plt.tight_layout()
      
      if get('display', True):
        plt.show()
      
      if get('output', False):
        plt.savefig('dist/' + name + '.eps', format='eps', dpi=1000)


if __name__ == '__main__':
  ParallelBars().draw(data)
