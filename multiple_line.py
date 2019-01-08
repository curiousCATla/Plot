# coding=utf-8
import ast
import json
import os
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np

# 用于比较S个solution的某性能指标随着过程量P变化的趋势. 不同的性能指标放在不同的图上. x轴是过程量 (比如时间), y轴是性能指标 (比如throughput或overhead)

data = {
  'type': "line",
  'figWidth': 600,
  'figHeight': 350,
  
  'mainColors': ['#0072bc',
                 '#d85119',
                 '#edb021',
                 '#7a8cbf',
                 '#009d70',
                 '#979797',
                 '#53b2ea'],
  
  'solutionList': ('MDT', 'AODV'),
  'xTitle': 'Time (s)',
  
  'legendLoc': 'best',
  'legendColumn': 1,
  
  'markerSize': 8,
  'lineWidth': 2,
  
  'xLog': False,
  'xGrid': False,
  'yLog': False,
  'yGrid': False,
  
  'xFontSize': 20,
  'xTickRotate': False,
  'yFontSize': 20,
  'legendFontSize': 20,
  
  'children': [
    {
      'name': 'signalingReceiveCnt',
      'figTitle': "",
      'yTitle': 'Signaling Receive Count',
      'xTicks&Labels': [(0, 2, 4, 6, 7), ('a', '2', 'd', 'asdf', 'dd')],
      'xTickRotate': True,
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


def nonEmptyIterable(obj):
  """return true if *obj* is iterable"""
  try:
    var = obj[1]
    return True
  except:
    return False


dpi = 100


class MultipleLines:
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
      
      if not isinstance(plotData, dict): continue
      
      solList = get('solutionList')
      
      fig, ax = plt.subplots()
      fig.set_size_inches(get('figWidth') / dpi, get('figHeight') / dpi)
      fig.set_dpi(dpi)
      
      yRange = get('yRange', None)
      y = get('y', None)
      if not y: y = list(list((r[1] + r[0]) / 2 for r in a) for a in yRange)
      
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
      x = get('x')
      for i in range(len(solList)):
        ax.errorbar(x[i] if nonEmptyIterable(x[0]) else x, y[i], color=colors[i], capsize=get("errorCapSize", 5),
                    elinewidth=1,
                    marker=markers[i],
                    markersize=get('markerSize', 8),
                    linestyle=linestyles[i], linewidth=get('lineWidth', 2),
                    label=solList[i], ecolor='r', yerr=yerror[i] if nonEmptyIterable(yRange) else None)
      
      handles, labels = ax.get_legend_handles_labels()
      
      lastAndInd = list(zip(
        (list(np.array(list(reversed(y[i]))) / np.array(list(reversed(x[i] if nonEmptyIterable(x[0]) else x))))
         for i in range(len(solList))),
        range(len(solList))))
      lastAndInd.sort(reverse=True)
      
      legend = None
      
      if get("showLegend", True):
        if get("legendAutomaticallyReorder", True):
          handles = [handles[lastAndInd[i][1]][0] for i in range(len(solList))]
          labels = [labels[lastAndInd[i][1]] for i in range(len(solList))]
        
        font = FontProperties('serif', weight='light', size=get('legendFontSize', 20))
        if get("legendOutside", False):
          legend = ax.legend(handles, labels, prop=font,
                             ncol=1, bbox_to_anchor=(1.02, 0.5), loc="center left", handlelength=0.8)
        else:
          legend = ax.legend(handles, labels, frameon=False, loc=get('legendLoc', 'best'), prop=font,
                             ncol=get('legendColumn', 1))
      
      font = FontProperties('serif', weight='light', size=get('xFontSize', 20))
      ax.set_xlabel(get('xTitle', ""), fontproperties=font)
      
      if get('xLog', False):
        ax.set_xscale('log')
        ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.get_xaxis().get_major_formatter().labelOnlyBase = False
      
      if get('xGrid', False):
        ax.xaxis.grid(True)
      
      if get('yLog', False):
        ax.set_yscale('log')
      
      if get('yGrid', False):
        ax.yaxis.grid(True)
      
      ticks = get('xTicks&Labels', None)
      if ticks:
        ax.tick_params(which='minor', length=0)
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_xticks(ticks[0])
          ax.set_xticklabels(ticks[1])
        else:
          ax.set_xticks(ticks)
      
      font = FontProperties('sans-serif', weight='light', size=get('xFontSize', 20) - 4)
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
        if get('xTickRotate', False):
          tick.label.set_rotation(45)

      ticks = get('yTicks&Labels', None)
      if ticks:
        # ax.tick_params(which='minor', length=0)
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_yticks(ticks[0])
          ax.set_yticklabels(ticks[1])
        else:
          ax.set_yticks(ticks)


      font = FontProperties('serif', weight='light', size=get('yFontSize', 20))
      ax.set_ylabel(get('yTitle', ""), fontproperties=font)
      
      font = FontProperties('sans-serif', weight='light', size=get('yFontSize', 20) - 4)
      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
      
      ax.set_title(get('figTitle', ""))
      
      lim = get('yLimit', [])
      if len(lim) > 0:
        realLimit = list(lim).copy()
        
        for i in range(2):
          if callable(lim[i]):
            realLimit[i] = lim[i](ax.get_ylim()[i])
        
        ax.set_ylim(realLimit)
      
      lim = get('xLimit', [])
      if len(lim) > 0:
        realLimit = list(lim).copy()
        
        for i in range(2):
          if callable(lim[i]):
            realLimit[i] = lim[i](ax.get_xlim()[i])
        
        ax.set_xlim(realLimit)
      
      try:
        fig.tight_layout()
      except:
        pass
      
      if get('output', False):
        fig.savefig('dist/' + name + '.eps', format='eps', dpi=dpi)
        fig.savefig('dist/' + name + '.png', format='png', dpi=dpi)
      
      plt.show(block=False)
      
      axes.append(ax)
    
    return axes


if __name__ == '__main__':
  MultipleLines().draw(data)
  
  while True:
    plt.pause(0.5)
