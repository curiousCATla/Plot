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
from matplotlib.ticker import FormatStrFormatter

data = {
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
  
  'solutionList': ('VERID', 'AAR', 'IntegriDB'),
  'environmentList': ("Intel", "Rome"),
  
  'yLog': False,
  'yGrid': False,
  
  'paddingLeft': 0.2,
  'paddingRight': 0.2,
  
  'marginGroups': 0.4,
  'marginInner': 0.02,
  'xFontSize': 20,
  'xTickRotate': False,
  'yFontSize': 20,
  'legendFontSize': 8,
  'output': False,
  
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
      print("---->" + name + "<----\n")

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
      
      envIndex = np.arange(len(envList))  # the x locations for the groups
      groupWidth = 1 - get('marginGroups', 0.2)
      paddingLeft = get('paddingLeft', 0.1)
      paddingRight = get('paddingRight', 0.1)
      marginBars = get('marginBars', 0.02)
      width = groupWidth / lenSol - marginBars  # the width of the bars
      
      colors = get('mainColors',
                   ['#0072bc', '#d95218', '#edb021', '#7a8cbf', '#009d70', '#979797', '#53b2ea',
                    "#ee4c9c"] + ['C%d' % (i % 10) for i in range(100)])
      
      if figure and axis:
        fig, ax = figure, axis
      else:
        fig, ax = plt.subplots()
        fig.set_size_inches(get('figWidth', 600) / dpi, get('figHeight', 350) / dpi)
        fig.set_dpi(dpi)
      
      rects = [None] * (lenComp * lenSol)
      
      oldy = np.array([[0.0, ] * len(envList), ] * lenSol)
      for comIdx in range(lenComp):
        yRange = get('yRange' if comIdx == 0 else 'y%dRange' % (comIdx + 1), get('yRange%d' % (comIdx + 1), None))
        y = plotData['y' if comIdx == 0 else 'y%d' % (comIdx + 1)]
        
        if nonEmptyIterable(yRange):
          yError = np.zeros((lenSol, 2, len(y[0])))
          for r in range(lenSol):
            for c in range(len(y[r])):
              yError[r][0][c] = y[r][c] - yRange[r][c][0]  # lower
              yError[r][1][c] = yRange[r][c][1] - y[r][c]  # upper
        else:
          yerror = get('yError' if comIdx == 0 else 'yError%d' % (comIdx + 1), None)
          
          if yerror:
            yError = np.zeros((lenSol, 2, len(y[0])))
            for r in range(lenSol):
              for c in range(len(y[r])):
                yError[r][0][c] = yerror[r][c][1]  # lower
                yError[r][1][c] = yerror[r][c][0]  # upper
          else:
            yError = None
        
        highContrast = get("highContrast", False)
        
        for solIdx in range(lenSol):
          normalIdx = (lenComp - 1 - comIdx) * lenSol + solIdx
          transpos = normalIdx // lenSol + normalIdx % lenSol * lenComp
          rects[transpos] = ax.bar(
            envIndex - groupWidth / 2 + (width + marginBars) * (solIdx + 0.5),
            y[solIdx], width - marginBars,
            bottom=oldy[solIdx],
            color='none' if highContrast else colors[comIdx * lenSol + solIdx],
            edgecolor=colors[comIdx * lenSol + solIdx] if highContrast else "black",
            hatch=['/', '\\', '-', '+', 'x', '.', 'o', 'O', '*', '//', '\\\\'][
              comIdx * lenSol + solIdx] if highContrast else None,
            ecolor='r', yerr=yError[solIdx] if yError is not None else None)
        oldy += y
      
      ax.set_xlim([0 - groupWidth / 2 - paddingLeft, len(envList) - 1 + groupWidth / 2 + paddingRight])
      if len(components):
        if lenSol == 1:
          legendTitles = components
        else:
          legendTitles = [None] * (
              lenComp * lenSol)  # list((com + ' - ' + sol for sol, com in itertools.product(solList, components, )))
          for comIdx in range(lenComp):
            for solIdx in range(lenSol):
              normalIdx = (lenComp - 1 - comIdx) * lenSol + solIdx
              transpos = normalIdx // lenSol + normalIdx % lenSol * lenComp
              legendTitles[transpos] = components[comIdx] + ' - ' + solList[solIdx]
              
              # print(components[comIdx] + ' - ' + solList[solIdx], (lenComp - 1 - comIdx, solIdx), normalIdx, transpos)
      else:
        legendTitles = solList
      
      if get("showLegend", True):
        font = FontProperties(weight='regular', size=get('legendFontSize', 20))
        
        if get("legendLoc", None) is None and get("legendOutside", True):
          ax.legend(rects, legendTitles, prop=font, bbox_to_anchor=(0, 1.02, 1, 0.2 * lenComp),
                    loc="lower left", mode="expand", borderaxespad=0, ncol=lenSol, handlelength=1)
        else:
          ax.legend(rects, legendTitles, frameon=False, loc=get('legendLoc', 'best'), prop=font,
                    ncol=get('legendColumn', 1), handlelength=1)
      
      font = FontProperties(weight='regular', size=get('xFontSize', 20))
      ax.set_xlabel(get('xTitle', ""), fontproperties=font)
      
      ticks = get('yTicks&Labels', None)
      if get('ySci'):
        ax.ticklabel_format(style='sci', axis='y', scilimits=get('ySci'))
      else:
        ax.ticklabel_format(style='plain', axis='y')
      
      if ticks:
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_yticks(ticks[0])
          ax.set_yticklabels(ticks[1])
        else:
          ax.set_yticks(ticks)
        
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
      
      ticks = get('xTicks&Labels', None)
      if ticks:
        ax.tick_params(which='minor', length=0)
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_xticks(ticks[0])
          ax.set_xticklabels(ticks[1])
        else:
          ax.set_xticks(ticks)
          ax.set_xticklabels([str(i) for i in ticks])
      else:
        ax.set_xticks(envIndex)
        ax.set_xticklabels(envList)
      
      font = FontProperties('sans-serif', weight='regular', size=get('xFontSize', 20) - 4)
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
        if get('xTickRotate', False):
          tick.label.set_rotation(45)
      
      font = FontProperties(weight='regular', size=get('yFontSize', 20))
      ax.set_ylabel(get('yTitle', ""), fontproperties=font)
      
      font = FontProperties('sans-serif', weight='regular', size=get('yFontSize', 20) - 4)
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
        fig.savefig('dist/' + name + '.pdf', format='pdf', dpi=dpi, bbox_inches="tight")
      
      plt.show(block=False)
      # plt.close('all')
      axes.append(ax)
    
    return axes


if __name__ == '__main__':
  ParallelBars().draw(data)
  
  while True:
    plt.pause(0.5)
