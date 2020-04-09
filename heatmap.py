# coding=utf-8
import ast
import json
import os, math
import matplotlib
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import BoundaryNorm
from matplotlib.ticker import MaxNLocator
import matplotlib.colors as colors
import matplotlib.cbook as cbook

# 用于比较S个solution的某性能指标随着过程量P变化的趋势. 不同的性能指标放在不同的图上. x轴是过程量 (比如时间), y轴是性能指标 (比如throughput或overhead)
cmaps = [('Perceptually Uniform Sequential', [
  'viridis', 'plasma', 'inferno', 'magma', 'cividis']),
         ('Sequential', [
           'Greys', 'Purples', 'Blues', 'Greens', 'Oranges', 'Reds',
           'YlOrBr', 'YlOrRd', 'OrRd', 'PuRd', 'RdPu', 'BuPu',
           'GnBu', 'PuBu', 'YlGnBu', 'PuBuGn', 'BuGn', 'YlGn']),
         ('Sequential (2)', [
           'binary', 'gist_yarg', 'gist_gray', 'gray', 'bone', 'pink',
           'spring', 'summer', 'autumn', 'winter', 'cool', 'Wistia',
           'hot', 'afmhot', 'gist_heat', 'copper']),
         ('Diverging', [
           'PiYG', 'PRGn', 'BrBG', 'PuOr', 'RdGy', 'RdBu',
           'RdYlBu', 'RdYlGn', 'Spectral', 'coolwarm', 'bwr', 'seismic']),
         ('Cyclic', ['twilight', 'twilight_shifted', 'hsv']),
         ('Qualitative', [
           'Pastel1', 'Pastel2', 'Paired', 'Accent',
           'Dark2', 'Set1', 'Set2', 'Set3',
           'tab10', 'tab20', 'tab20b', 'tab20c']),
         ('Miscellaneous', [
           'flag', 'prism', 'ocean', 'gist_earth', 'terrain', 'gist_stern',
           'gnuplot', 'gnuplot2', 'CMRmap', 'cubehelix', 'brg',
           'gist_rainbow', 'rainbow', 'jet', 'nipy_spectral', 'gist_ncar'])]
data = {
  'type': "heatmap",
  'figWidth': 600,
  'figHeight': 350,

  'legendLoc': 'best',
  'legendColumn': 1,

  'xFontSize': 20,
  'xTickRotate': False,
  'yFontSize': 20,

  'legendFontSize': 14,
  'output': False,

  'cmap': "Wistia",  # "YlGn"
  'figTitle': "meshTest",

  'children': [
    {
      'name': 'meshTest',

      'norm': 'linear',  # 'log', 'power@xx', 'diverge@xx', where xx is a number
      'quantify': list('ABCDEFG'),  # to quantify or not, and how many levels should there be.
      # if quantify is set, norm is ignored because boundary norm is used.

      'xTicks&Labels': list("{}0".format(i) for i in range(4, 17, 4)),
      'xTickRotate': False,
      'xTitle': '# disks in one bkt',

      'yTicks&Labels': list(range(1, 5)),
      'yTitle': '# added disks',

      'zTitle': '# Relocation',
      # 'zLimit': [0, 10],

      'aThreshold': None,  # the threshold that turns the annotation on the figure to light color
      'aFormat': "{x:.1f}",  # overrided by the
      'aColors': ["black", "white"],

      'z': 10 - np.random.rand(4, 4) * 5
    },
    {
      'name': 'meshTest2',
      'norm': 'linear',

      'xTicks&Labels': list("{}0".format(i) for i in range(4, 17, 4)),
      'xTickRotate': True,
      'xTitle': '# disks in one bkt',

      'yTicks&Labels': list(range(1, 5)),
      'yTitle': '# added disks',

      'zTitle': '# Relocation',
      'zLimit': [0, 100],

      'aThreshold': None,  # the threshold that turns the annotation on the figure to light color
      'aFormat': "{x:.1f}",  # overrided by the
      'aColors': ["black", "white"],

      'z': 50 + np.random.rand(4, 4) * 50
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


class HeatMap:
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

      if not isinstance(plotData, dict): continue

      fig, ax = plt.subplots()
      fig.set_size_inches(get('figWidth', 600) / dpi, get('figHeight', 350) / dpi)
      fig.set_dpi(dpi)

      plt.show(block=False)
      z = np.array(get('z'))

      zmin, zmax = get('zLimit', (z.min(), z.max()))

      # Plot the heatmap
      quantify = get('quantify')
      if quantify is not None:
        qrates = np.array(quantify)
        nLevels = len(quantify)
        norm = colors.BoundaryNorm(np.linspace(zmin, zmax, nLevels + 1), nLevels)
        fmt = matplotlib.ticker.FuncFormatter(lambda x, pos: qrates[::-1][max(0, min(nLevels - 1, norm(x)))])
        cmap = plt.get_cmap(get('cmap', "YlGn"), nLevels)
        zticks = list(zmin + (i + 0.5) * (zmax - zmin) / nLevels for i in range(nLevels))
      else:
        fmt = zticks = None
        cmap = get('cmap', "YlGn")
        normstr = get('norm', 'linear')
        if normstr == 'linear':
          norm = None
        elif normstr == 'log':
          norm = colors.LogNorm(vmin=zmin, vmax=zmax)
        elif normstr.startswith('pow@'):
          n = float(normstr[len('pow@') + 1:])
          norm = colors.PowerNorm(n, vmin=zmin, vmax=zmax)
        elif normstr.startswith('diverge@'):
          n = float(normstr[len('diverge@') + 1:])
          norm = colors.DivergingNorm(n, vmin=zmin, vmax=zmax)
        else:
          raise Exception("unrecognized norm string: " + normstr)

      im = ax.imshow(z, cmap=cmap, norm=norm, vmax=zmax, vmin=zmin, origin='lower')

      ax.set_title(get('figTitle', ""))

      if get("showLegend", True):
        cbar = ax.figure.colorbar(im, ax=ax, format=fmt, ticks=zticks)

        font = FontProperties('serif', weight='light', size=get('legendFontSize', 16))
        cbar.ax.set_ylabel(get('zTitle', ""), rotation=-90, va="bottom", fontproperties=font)

      if True:
        ticks = get('xTicks&Labels', None)
        if ticks:
          if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
            ax.set_xticks(ticks[0])
            ax.set_xticklabels(ticks[1])
          else:
            ax.set_xticks(np.arange(z.shape[1]))
            ax.set_xticklabels(ticks)
        else:
          ax.set_xticks(np.arange(z.shape[1]))

        font = FontProperties('sans-serif', weight='light', size=get('xFontSize', 20) - 4)
        for tick in ax.xaxis.get_major_ticks():
          tick.label.set_fontproperties(font)

        font = FontProperties('serif', weight='light', size=get('xFontSize', 20))
        ax.set_xlabel(get('xTitle', ""), fontproperties=font)

        if get('xTickRotate', True):
          # Rotate the tick labels and set their alignment.
          plt.setp(ax.get_xticklabels(), rotation=30, ha="right", rotation_mode="anchor")

      if True:
        font = FontProperties('serif', weight='light', size=get('yFontSize', 20))
        ax.set_ylabel(get('yTitle', ""), fontproperties=font)

        ticks = get('yTicks&Labels', None)
        if ticks:
          if len(ticks) == 2 and nonEmptyIterable(ticks[0]) and nonEmptyIterable(ticks[1]):
            ax.set_yticks(ticks[0])
            ax.set_yticklabels(ticks[1])
          else:
            ax.set_yticks(np.arange(z.shape[0]))
            ax.set_yticklabels(ticks)
        else:
          ax.set_yticks(np.arange(z.shape[0]))

        font = FontProperties('sans-serif', weight='light', size=get('yFontSize', 20) - 4)
        for tick in ax.yaxis.get_major_ticks():
          tick.label.set_fontproperties(font)

      # Turn spines off and create white grid.
      for edge, spine in ax.spines.items():
        spine.set_visible(False)

      ax.grid(which="minor", color="w", linestyle='-', linewidth=2)
      ax.tick_params(which="minor", bottom=False, left=False)

      # Normalize the threshold to the images color range.
      threshold = get('aThreshold')
      if threshold is not None:
        threshold = im.norm(threshold)
      else:
        threshold = im.norm(z.max()) / 2.

      # Set default alignment to center, but allow it to be
      # overwritten by textkw.
      kw = dict(horizontalalignment="center", verticalalignment="center")

      valfmt = fmt if fmt else get('aFormat', '{x:.1f}')
      # Get the formatter in case a string is supplied
      if isinstance(valfmt, str):
        valfmt = matplotlib.ticker.StrMethodFormatter(valfmt)

      # Loop over the data and create a `Text` for each "pixel".
      # Change the text's color depending on the data.
      aColors = get('aColors', ["black", "white"])
      texts = []
      for i in range(z.shape[0]):
        for j in range(z.shape[1]):
          kw.update(color=aColors[int(im.norm(z[i, j]) > threshold)])
          text = im.axes.text(j, i, valfmt(z[i, j], None), **kw)
          texts.append(text)

      try:
        fig.tight_layout()
      except:
        pass

      if get('output', True):
        fig.savefig('dist/' + name + '.eps', format='eps', dpi=dpi)
        fig.savefig('dist/' + name + '.png', format='png', dpi=dpi)

      plt.show(block=False)
      # plt.close('all')
      axes.append(ax)

    return axes


if __name__ == '__main__':
  HeatMap().draw(data)

  while True:
    plt.pause(0.5)
