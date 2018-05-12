# coding=utf-8
import numpy as np
import matplotlib.pyplot as plt
import os
import copy

# 用于比较S个solution在E个environment上的性能差别. 不同的性能指标放在不同的图上, 不同的解决方案在各个环境下的同一指标值放在同一张图上

data = {
  'figWidth': 6,
  'figHeight': 3.5,
  'mainColors': ['#0072bc', '#d85119', '#edb021'],
  
  'solutionList': ('VERID', 'AAR', 'IntegriDB'),
  'environmentList': ("Intel", "Rome"),
  
  'legendLoc': 'upper center',
  'legendColumn': 3,
  
  'yLog': False,
  'yGrid': False,
  
  'paddingLeft': 0.2,
  'paddingRight': 0,
  
  'margin': 0.4,
  'marginMiddle': 0.02,
  
  "insertion": {
    'xTitle': '',
    'yTitle': 'Insertion time (ms)',
    'legendLoc': 'upper left',
    'yLimit': [0, 0.8],
    'y': (
      (0.011, 0.203),
      (0.428, 0.220),
      (0.161, 0.513)
    ),
    'yrange': (
      ([0.009, 0.02], [0.1, 0.25]),
      ([0.428, 0.428], [0.220, 0.220]),
      ([0.161, 0.161], [0.513, 0.513])
    ),
  },
  "ads": {
    'yLog': True,
    'xTitle': '',
    'yTitle': 'ADS update (KB)',
    'yLimit': [0.01, 190.0],
    'y': (
      (0.147, 2.140),
      (1.268, 5.4367),
      (5.365, 5.123),
    ),
    'yrange': (
      ([0.01, 0.147], [0.1, 2.140]),
      ([0.268, 10.268], [5.4367, 5.4367]),
      ([4.365, 6.365], [5.123, 5.123])
    ),
  }
}

if not os.path.exists('dist'):
  os.makedirs('dist')


def draw(data):
  for name, plotData in data.items():
    def get(key, default=None):
      result = plotData.get(key, data.get(key, default))
      return result
    
    if not isinstance(plotData, dict): continue
    
    envList = get('environmentList')
    solList = get('solutionList')
    
    groupWidth = 1 - get('margin')
    ind = np.arange(len(envList))  # the x locations for the groups
    width = groupWidth / len(solList) - get('marginMiddle')  # the width of the bars
    
    fig, ax = plt.subplots()
    fig.set_size_inches(get('figWidth'), get('figHeight'))
    
    yrange = get('yrange', None)
    yerror = yrange
    y = plotData['y']
    
    if yerror:
      yerror = copy.deepcopy(yerror)
      for r in range(len(solList)):
        for c in range(len(y[r])):
          yerror[r][0][c] = y[r][c] - yrange[r][c][0]  # lower
          yerror[r][1][c] = yrange[r][c][1] - y[r][c]  # upper
    
    colors = get('mainColors', ['#0072bc', '#d85119', '#edb021'])
    rects = []
    for i in range(len(solList)):
      rects.append(
        ax.bar(ind + width * i + get('marginMiddle') / 2, y[i], width - get('marginMiddle'), color=colors[i],
               ecolor='r', yerr=yerror[i] if yerror else None))
    
    ax.set_xticks(ind + width * len(solList) / 2)
    ax.set_xticklabels(get('environmentList'), fontsize='x-large')
    
    for tick in ax.yaxis.get_major_ticks():
      tick.label.set_fontsize('x-large')
    
    plt.xlim([0 - groupWidth / 2 - get('paddingLeft'), 1 + len(solList) * width + groupWidth / 2 + get('paddingRight')])
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
      autoLabel(rects[i], (yrange[i][j][1] for j in range(len(envList))) if yerror else y[i])
    plt.tight_layout()
    
    if get('show', True):
      plt.show()
    else:
      plt.savefig('dist/' + name + '.eps', format='eps', dpi=1000)


if __name__ == '__main__':
  draw(data)
