# coding=utf-8
import ast
import itertools
import json
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import pyhuman
from pyhuman import *
import matplotlib.lines as mlines

# 用于比较S个solution在E个environment上的性能差别. 不同的性能指标放在不同的图上, 不同的解决方案在各个环境下的同一指标值放在同一张图上

data = {
  "type": "annotated_bar",
  "figWidth": 600,
  "figHeight": 350,
  
  "solutionList": [["Ludo Hashing", ["value", "bkt loc", "slot loc", "ovfl"]],
                   ["PK-Cuckoo", ["value", "fp"]], ["Othello Hashing", ["A", "B"]],
                   ["Cuckoo Hashing", ["value", "key"]]],
  
  "yGrid": False,
  
  "xFontSize": 20,
  "xTickRotate": False,
  "yFontSize": 20,
  "legendFontSize": 8,
  "componentFontSize": 6,
  "legendColumn": 2,
  
  "children": [
    {
      "environmentList": ["256M", "512M", "1B"],
      "name": "memory-keys",
      "xTitle": "Number of keys in table",
      "yTitle": "Memory (MB)",
      "y": [  # 低维是environment, 高维是不同的breakdown component
        [[1409.286144, 2818.572288, 5637.144576], [78.18182656, 156.36365312, 312.72730624],
         [44.040192, 88.080384, 176.160768], [3.9107690496, 7.8215380992, 15.6430761984]],
        
        [[1409.286144, 2818.572288, 5637.144576], [671.08864, 1342.17728, 2684.35456]],
        
        [[1785.0957824000002, 3570.1915648000004, 7140.383129600001],
         [1342.17728, 2684.35456, 5368.70912]],
        
        [[1409.286144, 2818.572288, 5637.144576],
         [1691.1433728000002, 3382.2867456000004, 6764.573491200001]]
      ],
      
      "annotationPos": [('bottom', -0.1, 200), ('right', -0.15, -300), ('right', -0.15, -300),
                        ('bottom', -0.05, 900), ('right', -0.15, 0), ('right', -0.15, 0),
                        ('bottom', 0.1, 1700), ('right', -0.15, 300), ('right', -0.15, 300), ]
    },
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


class AnnotatedBars:
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
      
      y = plotData['y']
      envList = get('environmentList')
      solList = get('solutionList')
      lenSol = len(solList)
      
      lenComp = solList.toList().map(lambda it: len(it[1]))
      
      groupWidth = 1 - get('margin', 0.2)
      envIndex = np.arange(len(envList))  # the x locations for the groups
      paddingLeft = get('paddingLeft', 0.1)
      paddingRight = get('paddingRight', 0.1)
      marginInner = get('marginInner', 0.02)
      width = groupWidth / lenSol - marginInner  # the width of the bars

      colors = get('mainColors', ['#0072bc', '#d95218', '#edb021', '#7a8cbf', '#009d70', '#979797', '#53b2ea', "#ee4c9c"] + ['C%d' % (i % 10) for i in range(100)])

      highContrast = get("highContrast", False)
      
      componentFontSize = get('componentFontSize', 8)

      if figure and axis:
        fig, ax = figure, axis
      else:
        fig, ax = plt.subplots()
        
        fig.set_size_inches(get('figWidth') / dpi, get('figHeight') / dpi)
        fig.set_dpi(dpi)
      
      rects = []
      for i in range(lenSol): rects.append([])
      
      oldy = np.array([[0.0, ] * len(envList), ] * lenSol)
      
      for solIdx in range(lenSol):
        for comIdx in range(lenComp[solIdx]):
          rectSet = ax.bar(envIndex - groupWidth / 2 + width * (solIdx + 0.5) + 2 * marginInner,
                        y[solIdx][comIdx],
                        width - marginInner,
                        bottom=oldy[solIdx],
                        color='none' if highContrast else colors[solIdx],
                        edgecolor=colors[solIdx] if highContrast else "black",
                        hatch=['/', '\\', '-', '+', 'x', '.', 'o', 'O', '*', '//', '\\\\'][
                          (comIdx - 1) * lenSol + solIdx] if highContrast else None,
                        ecolor='r')
          rects[solIdx].append(rectSet)
          
          oldy[solIdx] += y[solIdx][comIdx]
      
      if get('xLog', False):
        ax.set_xscale('log')
      
      if get('yLog', False):
        ax.set_yscale('log')
      
      if get('yGrid', False):
        ax.yaxis.grid(True)
      
      lim = get('yLimit', [])
      if len(lim) > 0:
        realLimit = lim.copy()
        
        for comIdx in range(2):
          if callable(lim[comIdx]):
            realLimit[comIdx] = lim[comIdx](ax.get_ylim()[comIdx])
        
        ax.set_ylim(realLimit)
      
      lim = get('xLimit', [])
      if len(lim) > 0:
        ax.set_xlim(lim)

      plt.gcf().canvas.draw()
      
      tooSmall = []
      figHeight = ax.get_ylim()[1] - ax.get_ylim()[0]
      
      for solIdx in range(lenSol):
        for comIdx in range(lenComp[solIdx]):
          
          for r in rects[solIdx][comIdx]:
            string = solList[solIdx][1][comIdx]
            text = ax.text(r.get_x() + r.get_width() / 2., r.get_y() + r.get_height() / 2., string,
                           rotation=90, ha='center', va='center',
                           fontsize=componentFontSize)
            
            bb = text.get_window_extent().transformed(ax.transData.inverted())
            
            if bb.height > r.get_height() * 0.95:
              text.remove()
              del text

              text = ax.text(r.get_x() + r.get_width() / 2., r.get_y() + r.get_height() / 2., string,
                            rotation=90, ha='center', va='center',
                            fontsize=componentFontSize - 2)
              
              bb = text.get_window_extent().transformed(ax.transData.inverted())
              
              if bb.height > r.get_height() * 0.95:
                text.remove()
                del text

                tooSmall.append([len(tooSmall), r.get_x() + r.get_width() / 2.,
                               r.get_y() + r.get_height() / 2., string])
      
      annotationPos = get("annotationPos", [])
      for (i, x, y, string) in tooSmall:
        if len(annotationPos) > i:
          loc = annotationPos[i][0]
          lx = x + annotationPos[i][1]
          ly = y + annotationPos[i][2] * figHeight
          
          l = mlines.Line2D([x, lx], [y, ly], linewidth=1, linestyle='--', color='black')
          ax.add_line(l)
          ha = "center" if loc == 'top' or loc == 'bottom' else loc
          va = "center" if loc == 'left' or loc == 'right' else loc
        
          ax.text(lx, ly, string, ha=ha, va=va, fontsize=get('componentFontSize', 8))
      
      ax.set_xticks(envIndex)
      ax.set_xticklabels(envList)
      
      ax.set_xlim([0 - groupWidth / 2 - paddingLeft,
                   len(envList) - 1 + groupWidth / 2 + paddingRight])
      
      if get("showLegend", True):
        font = FontProperties(weight='regular', size=get('legendFontSize', 20))
        ax.legend(rects.toList().map(lambda it: it[0]), solList.toList().map(lambda it: it[0]),
                  frameon=get('legendBoxed', False), loc=get('legendLoc', 'best'), prop=font,
                  ncol=get('legendColumn', lenSol), handlelength=1)
      
      font = FontProperties(weight='regular', size=get('xFontSize', 20))
      ax.set_xlabel(get('xTitle', ""), fontproperties=font)

      ticks = get('yTicks&Labels', None)
      if ticks:
        ax.ticklabel_format(style='plain', axis='y')
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_yticks(ticks[0])
          ax.set_yticklabels(ticks[1])
        else:
          ax.set_yticks(ticks)
  
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())

      font = FontProperties(weight='regular', size=get('xFontSize', 20) - 4)
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
        if get('xTickRotate', False):
          tick.label.set_rotation(45)
      
      font = FontProperties(weight='regular', size=get('yFontSize', 20))
      ax.set_ylabel(get('yTitle', ""), fontproperties=font)
      
      font = FontProperties('sans-serif', weight='regular', size=get('yFontSize', 20) - 4)
      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
      
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
  AnnotatedBars().draw(data)
  
  while True:
    plt.pause(0.5)
