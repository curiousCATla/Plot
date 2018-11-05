import math
import re

import numpy as np
import matplotlib.pyplot as plt

lc = 512

lkMaxMax = 8192
lkMaxMin = 32

lkMax = 1024
lpMax = 12
nkMax = 2 ** 22
nMax = 4096

lpMin = 1
nkMin = 1
nMin = 1

l3 = True
alien = False
alignToCacheLine = True
alignSlotToByte = False
allowGateway = False

compact = False

nk = 1024 * 1024
lk = 1020
lp = 4

lkMin = math.ceil(math.log2(nk))

n = 1024

nbCuckoo = 2
nsCuckoo = 4
elCuckoo = 1.05

ldCuckoo = 8
ldCuckooMax = 64
ldCuckooMin = 1

ldOthello = 8
ldOthelloMax = 64
ldOthelloMin = 1

eaOthello = 1.0
ebOthello = 1.33


def mergeWithGlobal(**kwargs):
  ''':return "n", "logNk", "lk", "lp", "alignBucketToRead", "alignSlotToByte", "l3"'''
  return [kwargs[var] if var in kwargs.keys() else globals()[var]
          for var in ["n", "logNk", "lk", "lp", "alignBucketToRead", "alignSlotToByte", "l3"]]


def combinationNumber(n, k):
  result = 1
  for i in range(k):
    result *= (n - i) / (i + 1)
  return result


def permutationNumber(n, k):
  result = 1
  for i in range(k):
    result *= (n - i)
  return result


def camel_case_split(identifier):
  return re.sub('(?!^)([A-Z][^A-Z]+)', r' \1', identifier).split()


def type_of_script():
  try:
    ipy_str = str(type(get_ipython()))
    if 'zmqshell' in ipy_str:
      return 'jupyter'
    if 'terminal' in ipy_str:
      return 'ipython'
  except:
    return 'terminal'


def in_jupyter():
  return type_of_script() == 'jupyter'


class Base:
  def getExtraRead(self, x="lk"):
    global alignToCacheLine
    oldAlign = alignToCacheLine
    
    alignToCacheLine = False
    unaligned = self.getRead(x)
    alignToCacheLine = True
    aligned = self.getRead(x)
    
    alignToCacheLine = oldAlign
    return list2numpy(unaligned) - list2numpy(aligned)
  
  def getMemoryFootPrint(self, x="lk"):
    pass
  
  def getRead(self, x="lk"):
    pass
  
  def getHashLength(self, x="lk"):
    pass
  
  def getFalsePositive(self, x="lk"):
    pass


class CuckooSwitch(Base):
  def getMemoryFootPrint(self, x="lk"):
    def calc(nk, lk, lp):
      ls = lk + lp
      if alignSlotToByte:
        ls = (ls + 7) // 8 * 8
      
      s = ls * nk * elCuckoo
      
      if alignToCacheLine:
        # if compact:
        #
        # else:
        eb = math.ceil(nsCuckoo * ls / lc) * lc / (nsCuckoo * ls)
      else:
        eb = 1
      
      if compact:
        ea = 1
      else:
        ea = 2 ** math.ceil(math.log2(math.ceil(nk * elCuckoo / nsCuckoo))) * nsCuckoo / nk / elCuckoo
      
      return eb * ea * s
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getRead(self, x="lk"):
    def calc(nk, lk, lp):
      ls = lk + lp
      if alignSlotToByte:
        ls = (ls + 7) // 8 * 8
      lb = ls * nsCuckoo
      
      def ECi(i):
        if alignToCacheLine:
          return math.ceil(i * ls / lc)
        else:
          lg = math.gcd(lc, lb)
          ll = math.ceil(i * ls % lc / lg) * lg
          
          return math.ceil(i * ls / lc) + ((ll - lg) / lc if ll != 0 else 0)
      
      return math.ceil(lk / lc) + sum([
        (i // nsCuckoo * ECi(nsCuckoo) + ECi(i % nsCuckoo))
        for i in range(1, nbCuckoo * nsCuckoo + 1)
      ]) / (nbCuckoo * nsCuckoo)
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getHashLength(self, x="lk"):
    return [1.5 * (lk if x is not "lk" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getFalsePositive(self, x="lk"):
    return [0 for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]


class CuckooFilter(Base):
  def __init__(self):
    self.stored = {}
  
  def calc(self, nk, lk, lp, ld):
    ls1 = ld + lp
    ls2 = lk + lp
    lb1 = ls1 * nsCuckoo
    lb2 = ls2 * nsCuckoo
    
    if alignSlotToByte:
      ls1 = (ls1 + 7) // 8 * 8
      ls2 = (ls2 + 7) // 8 * 8
    
    # recursively solve the equation set
    N1 = nk
    
    while True:
      oldC1 = N1
      Nb = 2 ** math.ceil(math.log2(math.ceil(N1 * elCuckoo / nsCuckoo)))
      Rl = N1 / Nb / nsCuckoo
      Cb = sum([
        (1 - 1 / 2 ** ldCuckoo) ** i * (1 - Rl) ** (nsCuckoo - i) * Rl ** i * combinationNumber(nsCuckoo, i)
        for i in range(nsCuckoo + 1)
      ])
      N1 = sum([permutationNumber(Nb, i) / (Nb ** nbCuckoo) * Cb ** i
                for i in range(1, nbCuckoo + 1)
                ]) * nk
      if math.fabs(oldC1 - N1) / N1 < 10E-3:
        break
    N2 = nk - N1
    
    eb1 = math.ceil(nsCuckoo * ls1 / lc) * lc / (nsCuckoo * ls1) if alignToCacheLine else 1
    ea1 = 2 ** math.ceil(math.log2(math.ceil(N1 * elCuckoo / nsCuckoo))) * nsCuckoo / N1 / elCuckoo
    if N2 > 0:
      eb2 = math.ceil(nsCuckoo * ls2 / lc) * lc / (nsCuckoo * ls2) if alignToCacheLine else 1
      ea2 = 2 ** math.ceil(math.log2(math.ceil(N2 * elCuckoo / nsCuckoo))) * nsCuckoo / N2 / elCuckoo
    else:
      eb2 = 1
      ea2 = 1
    
    return N1, N2, Nb, Rl, ea1, eb1, ea2, eb2, ls1, ls2, lb1, lb2, Cb
  
  def getMemoryFootPrint(self, x="lk"):
    def calc(nk, lk, lp, ld):
      N1, N2, Nb, Rl, ea1, eb1, ea2, eb2, ls1, ls2, lb1, lb2, Cb = self.calc(nk, lk, lp, ld)
      return Nb * nsCuckoo * ls1 * eb1 + ea2 * N2 * ls2 * eb2
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i, ldCuckoo)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getRead(self, x="lk"):
    def calc(nk, lk, lp, ld):
      N1, N2, Nb, Rl, ea1, eb1, ea2, eb2, ls1, ls2, lb1, lb2, Cb = self.calc(nk, lk, lp, ld)
      
      def ECi(i, ls, lb):
        if alignToCacheLine:
          return math.ceil(i * ls / lc)
        else:
          lg = math.gcd(lc, lb)
          ll = math.ceil(i * ls % lc / lg) * lg
          
          return math.ceil(i * ls / lc) + ((ll - lg) / lc if ll != 0 else 0)
      
      if l3 and allowGateway or not alien:
        result = math.ceil(lk / lc)
        
        result1 = 1 / (nbCuckoo * nsCuckoo) * sum([
          (i // nsCuckoo * ECi(nsCuckoo, ls1, lb1) + ECi(i % nsCuckoo, ls1, lb1))
          for i in range(1, nbCuckoo * nsCuckoo + 1)])
        
        result2 = nbCuckoo * ECi(nsCuckoo, ls1, lb1) + \
                  1 / (nbCuckoo * nsCuckoo) * sum([
          (i // nsCuckoo * ECi(nsCuckoo, ls2, lb2) + ECi(i % nsCuckoo, ls2, lb2))
          for i in range(1, nbCuckoo * nsCuckoo + 1)
        ])
        
        result += N1 / nk * result1 + N2 / nk * result2
        return result
      else:
        return math.ceil(lk / lc) + nbCuckoo * ECi(nsCuckoo, ls1, lb1) + nbCuckoo * ECi(nsCuckoo, ls2, lb2)
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i, ldCuckoo)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getHashLength(self, x="lk"):
    def calc(nk, lk, lp, ld):
      N1, N2, Nb, Rl, ea1, eb1, ea2, eb2, ls1, ls2, lb1, lb2, Cb = self.calc(nk, lk, lp, ld)
      
      if l3 and allowGateway or not alien:
        return (2.5 + 2 * N2 / nk) * lk
      else:
        return 5 * lk
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i, ldCuckoo)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getFalsePositive(self, x="lk"):
    def calc(nk, lk, lp, ld):
      N1, N2, Nb, Rl, ea1, eb1, ea2, eb2, ls1, ls2, lb1, lb2, Cb = self.calc(nk, lk, lp, ld)
      
      if l3 and allowGateway:
        return 0
      else:
        return 1 - Cb
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i, ldCuckoo)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getLvl1Ratio(self, x="lk"):
    def calc(nk, lk, lp, ld):
      N1, N2, Nb, Rl, ea1, eb1, ea2, eb2, ls1, ls2, lb1, lb2, Cb = self.calc(nk, lk, lp, ld)
      return N1 / nk
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i, ldCuckoo)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]


class Othello(Base):
  def calc(self, nk, lk, lp):
    lsa = lp if allowGateway else lp + ldOthello
    lsb = lp if allowGateway else max(lp, ldOthello)
    
    if alignSlotToByte:
      lsa = (lsa + 7) // 8 * 8
      lsb = (lsb + 7) // 8 * 8
    
    eca = lc / (lc // lsa * lsa)
    ecb = lc / (lc // lsb * lsb)
    
    Ea = 2 ** math.ceil(math.log2(nk * eaOthello)) / nk / eaOthello
    Eb = 2 ** math.ceil(math.log2(nk * ebOthello)) / nk / ebOthello
    
    ma = Ea * nk
    mb = Eb * nk
    
    return eca, ecb, ma, mb, Ea, Eb, lsa, lsb
  
  def getMemoryFootPrint(self, x="lk"):
    def calc(nk, lk, lp):
      eca, ecb, ma, mb, Ea, Eb, lsa, lsb = self.calc(nk, lk, lp)
      return eca * ma * lsa + ecb * mb * lsb
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getRead(self, x="lk"):
    def calc(nk, lk, lp):
      eca, ecb, ma, mb, Ea, Eb, lsa, lsb = self.calc(nk, lk, lp)
      
      if alignToCacheLine:
        return math.ceil(lk / lc) + 2
      else:
        lga = math.gcd(lc, lsa)
        lgb = math.gcd(lc, lsb)
        
        return math.ceil(lk / lc) + 2 + (lsa - lga) / lc + (lsb - lgb) / lc
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getHashLength(self, x="lk"):
    return [3 * (lk if x is not "lk" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]
  
  def getFalsePositive(self, x="lk"):
    def calc(nk, lk, lp):
      if allowGateway:
        return 1 if not l3 else 0
      
      eca, ecb, ma, mb, Ea, Eb, lsa, lsb = self.calc(nk, lk, lp)
      
      ea = math.exp(- nk / ma)
      eb = math.exp(- nk / mb)
      
      return 1 / (2 ** ldOthello - 1) * (1 - ea) * (1 - eb)
    
    return [calc(nk if x is not "nk" else i, lk if x is not "lk" else i, lp if x is not "lp" else i)
            for i in range(globals()[x + "Min"], globals()[x + "Max"] + 1)]


solutions = [CuckooFilter(), Othello()]

commonXTitles = ["lk", "lp"]

yTitles = ["ExtraRead", "Lvl1RatioFilter", "MemoryFootPrint", "Read",
           "HashLength", "FalsePositive"]

vars = "nk", "lkMax", "lk", "lp", "ldCuckoo", "ldOthello"
booleans = "l3", "alignToCacheLine", "alignSlotToByte", "alien", "allowGateway"

fig = plt.figure()
fig.set_figwidth(8)
fig.set_figheight(1.6 * len(yTitles))


def redraw():
  fig.clf()
  
  for row in range(len(yTitles), 0, -1):
    yTitle = yTitles[row - 1]
    
    lastWordInYTitle = camel_case_split(yTitle)[-1]
    tmpSolutions = []
    
    for solution in solutions:
      if lastWordInYTitle in solution.__class__.__name__:
        tmpSolutions.append(solution)
    
    if len(tmpSolutions) == 0:
      tmpSolutions = solutions
    else:
      yTitle = yTitle[0:-len(lastWordInYTitle)]
    
    for column in range(1, len(commonXTitles) + 1):
      xTitle = commonXTitles[column - 1]
      ax = fig.add_subplot(len(yTitles), len(commonXTitles), len(commonXTitles) * (row - 1) + column)
      if row == len(yTitles):
        ax.set_xlabel(xTitle, fontsize='x-small')
      else:
        plt.setp(ax.get_xticklabels(), visible=False)
      ax.set_ylabel(yTitle, fontsize='x-small')
      
      for solution in tmpSolutions:
        line, = ax.plot(range(globals()[xTitle + "Min"], globals()[xTitle + "Max"] + 1),
                        getattr(solution, "get" + yTitle)(xTitle))
  
  fig.tight_layout()
  fig.canvas.draw()


redraw()

if in_jupyter():
  from ipywidgets import *
  
  
  def sync(**kwargs):
    for var in kwargs.keys():
      try:
        globals()[var] = kwargs[var]
      except Exception as e:
        print(e)
  
  
  left = []
  right = []
  d = {}
  for var in vars:
    slider = widgets.IntSlider(description=var, min=globals()[var + "Min"], max=globals()[var + "Max"], step=1,
                               value=globals()[var])
    d[var] = slider
    left.append(slider)
  
  for var in booleans:
    checkbox = widgets.Checkbox(description=var, value=globals()[var])
    d[var] = checkbox
    right.append(checkbox)
  
  ui = HBox((VBox(left), VBox(right)))
  
  
  def update(nk, lkMax, lk, lp, ldCuckoo, ldOthello, l3, alien, alignToCacheLine, alignSlotToByte, allowGateway):
    sync(**locals())
    
    d["lk"].max = lkMax
    
    if lk > lkMax:
      globals()["lk"] = lkMax
      d["lk"].value = lkMax
    
    if nk > 2 ** lk:
      lkMin = math.ceil(math.log2(nk))
      globals()["lk"] = lkMin
      d["lk"].min = lkMin
    
    redraw()
  
  
  widgets.interactive_output(update, d)
  display(ui)
else:
  from matplotlib.widgets import *
  
  controlFig = plt.figure()
  
  
  def checkChanged(label):
    globals()[label] = not globals()[label]
    redraw()
  
  
  rax = plt.axes([0.05, 0.05, 0.9, 0.4])
  
  check = CheckButtons(rax, booleans, tuple(globals()[name] for name in booleans))
  check.on_clicked(checkChanged)
  
  sliders = {}
  
  
  def sliderChanged(val):
    for var in vars:
      globals()[var] = int(sliders[var].val)
    
    if lk > lkMax:
      sliders["lk"].val = lkMax
    
    elif nk > 2 ** lkMin:
      min = math.ceil(math.log2(nk))
      sliders["lk"].valmin = min
      globals()["lkMin"] = min
      
      if sliders["lk"].val < min:
        sliders["lk"].val = min
    else:
      redraw()
      return
    
    sliderChanged(val)
  
  
  for var in vars:
    sax = plt.axes([0.15, 0.55 + len(sliders) * 0.05, 0.7, 0.035], facecolor='lightgoldenrodyellow')
    slider = Slider(sax, var, globals()[var + "Min"], globals()[var + "Max"], valinit=globals()[var])
    slider.on_changed(sliderChanged)
    sliders[var] = slider
  
  sliders["lk"].slidermax = sliders['lkMax']
  redraw()
  
  plt.show()
