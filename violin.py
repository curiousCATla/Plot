# coding=utf-8
import ast
import itertools
import json
import os
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
import numpy as np
import matplotlib.patches as mpatches

# 用于比较S个solution在E个environment上的性能差别. 不同的性能指标放在不同的图上, 不同的解决方案在各个环境下的同一指标值放在同一张图上
from matplotlib.ticker import FormatStrFormatter

data = {
  'type': "violin",
  'figWidth': 600,
  'figHeight': 350,
  'mainColors': ['#0072bc',
                 '#d95218',
                 '#edb021',
                 '#7a8cbf',
                 '#009d70',
                 '#979797',
                 '#53b2ea'],
  
  'environmentList': ("Intel", "Rome"),
  'solutionList': ('VERID', 'AAR', 'IntegriDB'),
  
  'paddingLeft': 0.2,
  'paddingRight': 0.2,
  
  'marginGroups': 0.4,
  'marginViolins': 0.02,
  
  'yLog': True,
  'yGrid': True,
  
  'xFontSize': 20,
  'yFontSize': 20,
  
  'output': False,
  
  'children': [
    {
      'name': "insertion",
      'xTitle': '',
      'yTitle': 'Insertion time (ms)',
      'yLimit': [0, 1.4],
      'samples': [(
        (0.011, 0.203, 0.161, 0.513),  # 同一个environment, 不同的sample
        (0.428, 0.220, 0.161, 0.513),  # 另一个environment
      ),
        (
          (0.0211, 0.203, 0.4161, 0.513),  # 同一个environment, 不同的sample
          (0.2428, 0.3220, 0.161, 0.513),  # 另一个environment
        ),
        (
          (0.1211, 0.203, 0.4161, 0.513),  # 同一个environment, 不同的sample
          (0.2428, 0.3220, 0.161, 0.0513),  # 另一个environment
        ),
      ]
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


def adjacent_values(vals, q1, q3):
  upper_adjacent_value = q3 + (q3 - q1) * 1.5
  upper_adjacent_value = np.clip(upper_adjacent_value, q3, vals[-1])
  
  lower_adjacent_value = q1 - (q3 - q1) * 1.5
  lower_adjacent_value = np.clip(lower_adjacent_value, vals[0], q1)
  return lower_adjacent_value, upper_adjacent_value


def set_axis_style(ax, labels):
  ax.get_xaxis().set_tick_params(direction='out')
  ax.xaxis.set_ticks_position('bottom')
  ax.set_xticks(np.arange(1, len(labels) + 1))
  ax.set_xticklabels(labels)
  ax.set_xlim(0.25, len(labels) + 0.75)
  ax.set_xlabel('Overall load')


class Violin:
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
      lenEnv = len(envList)
      solList = get('solutionList', [''])
      lenSol = len(solList)
      components = get('components', ())
      lenComp = max(1, len(components))
      
      envIndex = np.arange(lenEnv)  # the x locations for the groups
      groupWidth = 1 - get('marginGroups', 0.2)
      marginViolins = get('marginViolins', 0.02)
      width = groupWidth / lenSol - marginViolins  # the width of the violins
      
      samples = get("samples")
      
      colors = get('mainColors',
                   ['#0072bc', '#d95218', '#edb021', '#7a8cbf', '#009d70', '#979797', '#53b2ea',
                    "#ee4c9c"] + ['C%d' % (i % 10) for i in range(100)])
      
      if figure and axis:
        fig, ax = figure, axis
      else:
        fig, ax = plt.subplots()
        fig.set_size_inches(get('figWidth', 600) / dpi, get('figHeight', 350) / dpi)
        fig.set_dpi(dpi)
      
      fake_handles = []
      for solIdx in range(lenSol):
        solSamples = samples[solIdx]
        color = colors[solIdx % len(colors)]
        fake_handles.append(mpatches.Patch(color=color))
        
        positions = envIndex - groupWidth / 2 + (width + marginViolins) * (solIdx + 0.5)
        widths = [width - marginViolins] * lenEnv
        
        parts = ax.violinplot(solSamples, positions=positions, widths=widths, showmeans=False, showmedians=False,
                              showextrema=False)
        
        for i, pc in enumerate(parts['bodies']):
          pc.set_facecolor(color)
          pc.set_edgecolor('black')
          pc.set_alpha(1)
        
        quartile1, medians, quartile3 = np.percentile(solSamples, [25, 50, 75], axis=1)
        
        whiskers = np.array(
          [adjacent_values(sorted_array, q1, q3)
           for sorted_array, q1, q3 in zip(solSamples, quartile1, quartile3)])
        
        whiskersMin, whiskersMax = whiskers[:, 0], whiskers[:, 1]
        
        ax.scatter(positions, medians, marker='o', color='white', s=20, zorder=3)
        ax.vlines(positions, quartile1, quartile3, color='k', linestyle='-', lw=5)
        ax.vlines(positions, whiskersMin, whiskersMax, color='k', linestyle='-', lw=1)
      
      if get("showLegend", lenSol > 1):
        font = FontProperties('serif', weight='light', size=get('legendFontSize', 20))
        
        if get("legendLoc", None) is None and get("legendOutside", False):
          ax.legend(fake_handles, solList, prop=font, bbox_to_anchor=(0, 1.02, 1, 0.2 * lenComp),
                    loc="lower left", mode="expand", borderaxespad=0, ncol=lenSol, handlelength=1)
        else:
          ax.legend(fake_handles, solList, frameon=False, loc=get('legendLoc', 'best'), prop=font,
                    ncol=get('legendColumn', 1), handlelength=1)
      
      font = FontProperties('serif', weight='light', size=get('xFontSize', 20))
      ax.set_xlabel(get('xTitle', ""), fontproperties=font)
      
      paddingLeft = get('paddingLeft', 0.1)
      paddingRight = get('paddingRight', 0.1)
      ax.set_xlim([0 - groupWidth / 2 - paddingLeft, len(envList) - 1 + groupWidth / 2 + paddingRight])
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
      
      font = FontProperties('sans-serif', weight='light', size=get('xFontSize', 20) - 4)
      for tick in ax.xaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
        if get('xTickRotate', False):
          tick.label.set_rotation(45)
      
      font = FontProperties('serif', weight='light', size=get('yFontSize', 20))
      ax.set_ylabel(get('yTitle', ""), fontproperties=font)
      
      font = FontProperties('sans-serif', weight='light', size=get('yFontSize', 20) - 4)
      for tick in ax.yaxis.get_major_ticks():
        tick.label.set_fontproperties(font)
      
      if get('ySci'):
        ax.ticklabel_format(style='sci', axis='y', scilimits=get('ySci'))
      else:
        ax.ticklabel_format(style='plain', axis='y')
      
      ticks = get('yTicks&Labels', None)
      if ticks:
        if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
          ax.set_yticks(ticks[0])
          ax.set_yticklabels(ticks[1])
        else:
          ax.set_yticks(ticks)
        
        ax.get_yaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
        ax.get_yaxis().set_minor_formatter(matplotlib.ticker.NullFormatter())
      
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
      
      if get('output', True):
        fig.savefig('dist/' + name + '.eps', format='eps', dpi=dpi, bbox_inches="tight")
        fig.savefig('dist/' + name + '.png', format='png', dpi=dpi, bbox_inches="tight")
      
      plt.show(block=False)
      # plt.close('all')
      axes.append(ax)
    
    return axes


if __name__ == '__main__':
  Violin().draw(data)
  
  while True:
    plt.pause(0.5)
