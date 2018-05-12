import multiple_line
import parallel_bar
import numpy as np

dataPath = '../UAV/results/'

for speed in [2, 5, 10, 15, 20]:
  for mobility in ['ST']:
    trafficFile = open(dataPath + '%s-%d-traffic.txt' % (mobility, speed))
    print trafficFile.name, trafficFile.readline()
    packetTypeList = trafficFile.readline().strip().split(' ')
    
    trafficData = tuple(([], [], [], []) for i in range(len(packetTypeList)))
    
    for line in trafficFile.readlines():
      valuesOfPacketType = line.strip().split('\t')[1:]
      for packetType in range(len(trafficData)):
        valuesOfTrafficType = tuple(map(lambda s: int(s), g.split(' ')) for g in valuesOfPacketType)
        for j in range(4):
          trafficData[packetType][j].append(valuesOfTrafficType[packetType][j])
    trafficFile.close()
    
    memoryFile = open(dataPath + '%s-%d-memory.txt' % (mobility, speed))
    memoryData = []
    
    memoryFile.close()
    
    data = {
      'show': False,
      'figWidth': 12,
      'figHeight': 7,
      
      'solutionList': packetTypeList,
      'xTitle': 'Time (s)',
      
      'yLog': True,
      
      'legendLoc': 'best',
      'legendColumn': 1,
      
      'markersize': 8,
      'linewidth': 2,
      
      '%s-%d-signalingReceiveCnt' % (mobility, speed): {
        'figTitle': trafficFile.name,
        'yTitle': 'Signaling Receive Count',
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficData[packetType][0] for packetType in range(len(packetTypeList))
        ]
      },
      '%s-%d-signalingReceiveAmount' % (mobility, speed): {
        'yTitle': 'Signaling Receive Amount (B)',
        'figTitle': trafficFile.name,
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficData[packetType][1] for packetType in range(len(packetTypeList))
        ]
      },
      '%s-%d-signalingSendCnt' % (mobility, speed): {
        'yTitle': 'Signaling Send Cnt',
        'figTitle': trafficFile.name,
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficData[packetType][2] for packetType in range(len(packetTypeList))
        ]
      },
      '%s-%d-signalingSendAmount' % (mobility, speed): {
        'yTitle': 'Signaling Send Amount (B)',
        'figTitle': trafficFile.name,
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficData[packetType][3] for packetType in range(len(packetTypeList))
        ]
      }
    }
    
    multiple_line.draw(data)
    
    trafficSum = (tuple(np.zeros(len(trafficData[0][0])) for i in range(4)),
                  tuple(np.zeros(len(trafficData[0][0])) for i in range(4)))
    
    for t in range(len(packetTypeList) - 3):
      for d in range(4):
        for i in range(len(trafficData[t][d])):
          trafficSum[0][d][i] += trafficData[t][d][i]
    
    for t in range(len(packetTypeList) - 3, len(packetTypeList)):
      for d in range(4):
        for i in range(len(trafficData[t][d])):
          trafficSum[1][d][i] += trafficData[t][d][i]
    
    data = {
      'show': False,
      'figWidth': 12,
      'figHeight': 7,
      
      'solutionList': ('MDT', 'AODV'),
      'xTitle': 'Time (s)',
      'yLog': True,
      'legendLoc': 'best',
      'legendColumn': 1,
      
      'markersize': 8,
      'linewidth': 2,
      
      '%s-%d-signalingReceiveCnt-aggregated' % (mobility, speed): {
        'figTitle': trafficFile.name,
        'yTitle': 'Signaling Receive Count',
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficSum[0][0], trafficSum[1][0],
        ]
      },
      '%s-%d-signalingReceiveAmount-aggregated' % (mobility, speed): {
        'yTitle': 'Signaling Receive Amount (B)',
        'figTitle': trafficFile.name,
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficSum[0][1], trafficSum[1][1],
        ]
      },
      '%s-%d-signalingSendCnt-aggregated' % (mobility, speed): {
        'yTitle': 'Signaling Send Cnt',
        'figTitle': trafficFile.name,
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficSum[0][2], trafficSum[1][2],
        ]
      },
      '%s-%d-signalingSendAmount-aggregated' % (mobility, speed): {
        'yTitle': 'Signaling Send Amount (B)',
        'figTitle': trafficFile.name,
        'x': range(len(trafficData[0][0])),
        'y': [
          trafficSum[0][3], trafficSum[1][3],
        ]
      }
    }
    
    multiple_line.draw(data)
