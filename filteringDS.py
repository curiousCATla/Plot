from multiple_line import MultipleLines
import math


class Base:
  def __init__(self):
    self.lastLd = 100
  
  def fpToBits(self, fp):
    for i in range(self.lastLd, 0, -1):
      b, p = self.getFalsePositiveRatio(i)
      if p > fp:
        self.lastLd = i + 1
        return self.getFalsePositiveRatio(i + 1)[0]
  
  def getFalsePositiveRatio(self, ld):
    return 1, 1


class Othello(Base):
  def getFalsePositiveRatio(self, ld):
    bitsPerKey = ld * 2.33
    return bitsPerKey, 0.33 / (2 ** ld - 1)


class OthelloFork(Base):
  def getFalsePositiveRatio(self, ld):
    bitsPerKey = math.ceil(ld / 2) * 3.33
    return bitsPerKey, 0.33 / (2 ** ld - 1)


loadFactor = 0.85

class Cuckoo(Base):
  def getFalsePositiveRatio(self, ld):
    bitsPerkey = ld / loadFactor
    return bitsPerkey - 1, 8 * loadFactor / 2 ** ld


x = [0.00001 * 1.005 ** i for i in range(2000)]
print(x[-1])
o = Othello()
of = OthelloFork()
c = Cuckoo()

y = [
  [o.fpToBits(x[i]) for i in range(len(x))],
  [of.fpToBits(x[i]) for i in range(len(x))],
  [c.fpToBits(x[i]) for i in range(len(x))]
]

data = {
  'type': "multiple_lines",
  'figWidth': 600,
  'figHeight': 350,
  
  'solutionList': ('Othello', 'Othello Fork', 'Cuckoo'),
  
  'legendLoc': 'best',
  'legendColumn': 1,
  
  'markerSize': 0,
  'lineWidth': 1,
  
  'xLog': True,
  'xGrid': True,
  'yLog': False,
  'yGrid': False,
  
  'output': True,
  
  'children': [
    {
      'name': 'bits-FP',
      'xTitle': 'False positive',
      'yTitle': 'Bits per key',
      'x': x,
      'y': y
    }
  ]
}

MultipleLines().draw(data)