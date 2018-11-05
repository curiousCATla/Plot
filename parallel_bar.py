# coding=utf-8
import ast
import itertools
import json
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np

# 用于比较S个solution在E个environment上的性能差别. 不同的性能指标放在不同的图上, 不同的解决方案在各个环境下的同一指标值放在同一张图上

data = {
  'type': "bar",
  'figWidth': 600,
  'figHeight': 350,
  'mainColors': ['#0072bc',
                 '#d85119',
                 '#edb021',
                 '#7a8cbf',
                 '#009d70',
                 '#979797',
                 '#53b2ea'],
  
  'solutionList': ('VERID', 'AAR', 'IntegriDB'),
  'environmentList': ("Intel", "Rome"),
  
  'yLog': False,
  'yGrid': False,
  
  'paddingLeft': 0.2,
  'paddingRight': 0.2,
  
  'margin': 0.4,
  'marginInner': 0.02,
  'xFontSize': 20,
  'xTickRotate': False,
  'yFontSize': 20,
  'legendFontSize': 8,
  
  'children': [
    {
      'name': "insertion",
      'xTitle': '',
      'yTitle': 'Insertion time (ms)',
      'components': ("Acyclic add", "Cyclic add"),
      'yLimit': [0, 1.4],
      'y': (
        (0.011, 0.203),  # 同一个solution, 不同的environment
        (0.428, 0.220),  # 另一个solution
        (0.161, 0.513)
      ),
      'yRange': (
        ([0.009, 0.02], [0.1, 0.25]),  # 误差
        ([0.428, 0.428], [0.220, 0.220]),
        ([0.161, 0.161], [0.513, 0.513])
      ),
      'y2': (  # 第二个分量
        (0.011, 0.203),
        (0, 0.220),
        (0.161, 0.513)
      ),
      'yRange2': (
        ([0.009, 0.02], [0.1, 0.25]),
        ([0.428, 0.428], [0.220, 0.220]),
        ([0.161, 0.161], [0.513, 0.513])
      ),
    },
    {
      'name': "ads",
      'yLog': True,
      'xTitle': '',
      'yTitle': 'ADS update (KB)',
      'yLimit': [0.01, 190.0],
      'y': (
        (0.147, 2.140),
        (1.268, 5.4367),
        (5.365, 5.123),
      ),
      'yRange': (
        ([0.015, 0.147], [0.1, 2.140]),
        ([0.268, 10.268], [5.4367, 5.4367]),
        ([4.365, 6.365], [5.123, 5.123])
      ),
    }
  ]
}

if not os.path.exists('dist'):
  os.makedirs('dist')


def nonEmptyIterable(obj):
  """return true if *obj* is iterable"""
  try:
    var = obj[0]
    return True
  except:
    return False


dpi = 100


class ParallelBars:
  def draw(self, data, figure=None, axis=None):
    if isinstance(data, str):
      try:
        data = json.loads(data)
      except:
        data = ast.literal_eval(data)

    axes = []

    for plotData in data['children']:
      name = plotData['name']
      
      def get(key, default=None):
        result = plotData.get(key, None)
        if result is not None: return result
        
        result = data.get(key, None)
        if result is not None: return result
        
        return default
      
      envList = get('environmentList')
      solList = get('solutionList')
      lenSol = len(solList)
      components = get('components', ())
      lenComp = max(1, len(components))
      
      groupWidth = 1 - get('margin')
      envIndex = np.arange(len(envList))  # the x locations for the groups
      width = groupWidth / lenSol - get('marginInner')  # the width of the bars
      paddingLeft = get('paddingLeft', 0)
      marginInner = get('marginInner', 0)
      
      colors = get('mainColors', ['C%d' % (i % 10) for i in range(100)])
      
      if figure and axis:
        fig, ax = figure, axis
      else:
        fig, ax = plt.subplots()
      
        fig.set_size_inches(get('figWidth') / dpi, get('figHeight') / dpi)
        fig.set_dpi(dpi)
      
      rects = []
      oldy = ((0,) * len(envList),) * lenSol
      for i in range(1, lenComp + 1):
        yRange = get('yRange' if i == 1 else 'yRange%d' % i, None)
        y = plotData['y' if i == 1 else 'y%d' % i]
        
        if nonEmptyIterable(yRange):
          yError = np.zeros((lenSol, 2, len(y[0])))
          for r in range(lenSol):
            for c in range(len(y[r])):
              yError[r][0][c] = y[r][c] - yRange[r][c][0]  # lower
              yError[r][1][c] = yRange[r][c][1] - y[r][c]  # upper
        else:
          yerror = get('yError' if i == 1 else 'yError%d' % i, None)
          
          if yerror:
            yError = np.zeros((lenSol, 2, len(y[0])))
            for r in range(lenSol):
              for c in range(len(y[r])):
                yError[r][0][c] = yerror[r][c][1]  # lower
                yError[r][1][c] = yerror[r][c][0]  # upper
          else:
            yError = None
        
        for sol in range(lenSol):
          rects.append(
            ax.bar(envIndex - groupWidth / 2 + width * (sol + 0.5) + marginInner, y[sol], width - marginInner,
                   bottom=oldy[sol], color=colors[(i - 1) * lenSol + sol], ecolor='r',
                   yerr=yError[sol] if yError is not None else None))
        oldy = y
      
      ax.set_xticks(envIndex)
      ax.set_xticklabels(get('environmentList'))
      
      ax.set_xlim([0 - groupWidth / 2 - paddingLeft, len(envList) - 1 + groupWidth / 2 + get('paddingRight', 0)])
      if len(components):
        legendTitles = list((sol + ' - ' + com for sol, com in itertools.product(components, solList, )))
      else:
        legendTitles = solList
      
      if get("showLegend", True):
        font = FontProperties('serif', weight='light', size=get('legendFontSize', 20))
        ax.legend((rects[i // lenComp + lenSol * (lenComp - 1 - i % lenComp)][0] for i in range(len(rects))),
                  legendTitles, prop=font, bbox_to_anchor=(0, 1.02, 1, 0.2 * lenComp), loc="lower left",
                  mode="expand", borderaxespad=0, ncol=lenSol)
      
      font = FontProperties('serif', weight='light', size=get('xFontSize', 20))
      ax.set_xlabel(get('xTitle', ""), fontproperties=font)
      
      ticks = get('xTicks&Labels', None)
      if ticks:
        ax.tick_params(which='minor', length=0)
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_xticks(ticks[0])
          ax.set_xticklabels(ticks[1])
        else:
          ax.set_xticks(ticks)
      
      font = FontProperties('serif', weight='light', size=get('xFontSize', 20) - 4)
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
        if get('xTickRotate', False):
          tick.label.set_rotation(45)
      
      font = FontProperties('serif', weight='light', size=get('yFontSize', 20))
      ax.set_ylabel(get('yTitle', ""), fontproperties=font)
      
      font = FontProperties('sans-serif', weight='light', size=get('yFontSize', 20) - 4)
      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
      
      if get('xLog', False):
        ax.set_xscale('log')
      
      if get('yLog', False):
        ax.set_yscale('log')
      
      if get('yGrid', False):
        ax.yaxis.grid(True)
      
      lim = get('yLimit', [])
      if len(lim) > 0:
        realLimit = lim.copy()
        
        for i in range(2):
          if callable(lim[i]):
            realLimit[i] = lim[i](ax.get_ylim()[i])
        
        ax.set_ylim(realLimit)
      
      lim = get('xLimit', [])
      if len(lim) > 0:
        ax.set_xlim(lim)
      
      subAxes = []
      for subfigure in get('subfigures', []):
        from .plot import Ploter
        subAxes.append(Ploter().plot(subfigure, fig, ax))
      
      # TODO add subfigures
      
      try:
        fig.tight_layout()
      except:
        pass
      
      if get('output', False):
        fig.savefig('dist/' + name + '.eps', format='eps', dpi=dpi, bbox_inches="tight")
        fig.savefig('dist/' + name + '.png', format='png', dpi=dpi, bbox_inches="tight")
      
      plt.show(block=False)
      
      axes.append(ax)

    return axes


if __name__ == '__main__':
  ParallelBars().draw(data)
  
  while True:
    plt.pause(0.5)
