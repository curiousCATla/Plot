# coding=utf-8
import ast
import json

from multiple_line import MultipleLines

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
      'x': ([0, 0.1, 0.57, 0.63, 0.85, 0.92, 0.99, 1, 1.1, 1.1, 1.2, ],
            [0, 0.1, 0.57, 0.63, 0.85, 0.92, 0.99, 1, 1.1, 3.1, 3.2, ])
    },
  ]
}


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
      def get(key, default=None):
        result = plotData.get(key, None)
        if result is not None and not iterable(result) or nonEmptyIterable(result): return result
        
        result = data.get(key, None)
        if result is not None and not iterable(result) or nonEmptyIterable(result): return result
        
        return default
      
      if not isinstance(plotData, dict): continue
      
      solList = get('solutionList')
      
      minx = float("inf")
      maxx = float("-inf")
      X = []
      Y = []
      inputX = get('x')
      
      for i in range(len(solList)):
        x = inputX[i]
        minx = min(minx, x[0])
        maxx = max(maxx, x[-1])
        
        sum = 0
        y = [0]
        newX = [x[0]]
        for v in x[1:]:
          sum += 1
          y.append(y[-1])
          newX.append(v)
          newY = sum / len(x)
          y.append(newY)
          newX.append(v)
        newX.append(maxx)
        y.append(1)
        X.append(newX)
        Y.append(y)
      
      plotData['x'] = X
      plotData['y'] = Y
      plotData['xLimit'] = (minx, maxx)
      plotData['yLimit'] = (0, 1)
      plotData['markerSize'] = 0
    data['type'] = 'multiple_lines'
    MultipleLines().draw(data)


if __name__ == '__main__':
  Cdf().draw(data)
