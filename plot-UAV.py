from multiple_line import MultipleLines
import parallel_bar
import numpy as np

dataPath = '../UAV/results/'

for speed in [2, 5, 10, 15, 20]:
  for mobility in ['ST']:
    trafficFile = open(dataPath + '%s-%d-traffic.txt' % (mobility, speed))
    print(trafficFile.name, trafficFile.readline())
    packetTypeList = trafficFile.readline().strip().split(' ')
    
    trafficData = tuple(([], [], [], []) for i in range(len(packetTypeList)))
    
    for line in trafficFile.readlines():
      valuesOfPacketType = line.strip().split('\t')[1:]
      for packetType in range(len(trafficData)):
        valuesOfTrafficType = tuple(list(map(lambda s: int(s), g.split(' '))) for g in valuesOfPacketType)
        for j in range(4):
          trafficData[packetType][j].append(valuesOfTrafficType[packetType][j])
    trafficFile.close()
    
    data = {
      'type': "line",
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
      
      'children': [
        {
          'name': '%s-%d-signalingReceiveCnt' % (mobility, speed),
          'figTitle': trafficFile.name,
          'yTitle': 'Signaling Receive Count',
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficData[packetType][0] for packetType in range(len(packetTypeList))
          ]
        },
        {
          'name': '%s-%d-signalingReceiveAmount' % (mobility, speed),
          'yTitle': 'Signaling Receive Amount (B)',
          'figTitle': trafficFile.name,
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficData[packetType][1] for packetType in range(len(packetTypeList))
          ]
        },
        {
          'name': '%s-%d-signalingSendCnt' % (mobility, speed),
          'yTitle': 'Signaling Send Cnt',
          'figTitle': trafficFile.name,
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficData[packetType][2] for packetType in range(len(packetTypeList))
          ]
        },
        {
          'name': '%s-%d-signalingSendAmount' % (mobility, speed),
          'yTitle': 'Signaling Send Amount (B)',
          'figTitle': trafficFile.name,
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficData[packetType][3] for packetType in range(len(packetTypeList))
          ]
        }
      ],
    }
    
    MultipleLines().draw(data)
    
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
      'type': "line",
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
      
      'children': [
        {
          'name': '%s-%d-signalingReceiveCnt-aggregated' % (mobility, speed),
          'figTitle': trafficFile.name,
          'yTitle': 'Signaling Receive Count',
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficSum[0][0], trafficSum[1][0],
          ]
        },
        {
          'name': '%s-%d-signalingReceiveAmount-aggregated' % (mobility, speed),
          'yTitle': 'Signaling Receive Amount (B)',
          'figTitle': trafficFile.name,
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficSum[0][1], trafficSum[1][1],
          ]
        },
        {
          'name': '%s-%d-signalingSendCnt-aggregated' % (mobility, speed),
          'yTitle': 'Signaling Send Cnt',
          'figTitle': trafficFile.name,
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficSum[0][2], trafficSum[1][2],
          ]
        },
        {
          'name':'%s-%d-signalingSendAmount-aggregated' % (mobility, speed),
          'yTitle': 'Signaling Send Amount (B)',
          'figTitle': trafficFile.name,
          'x': range(len(trafficData[0][0])),
          'y': [
            trafficSum[0][3], trafficSum[1][3],
          ]
        }
      ],
    }
    
    MultipleLines().draw(data)
    
    memoryFile = open(dataPath + '%s-%d-memory.txt' % (mobility, speed))
    print(memoryFile.name, memoryFile.readline())
    tableTypeList = memoryFile.readline().strip().split(' ')
    
    memoryData = tuple(([], []) for i in range(len(tableTypeList)))
    
    for line in memoryFile.readlines():
      valuesOfTableType = line.strip().split('\t')[1:]
      for tableType in range(len(tableTypeList)):
        valuesOfMetricType = tuple(list(map(lambda s: int(s), g.split(' '))) for g in valuesOfTableType)
        for j in range(2):
          memoryData[tableType][j].append(valuesOfMetricType[tableType][j])
    memoryFile.close()
    
    data = {
      'type': "line",
      'show': False,
      'figWidth': 12,
      'figHeight': 7,
      
      'solutionList': tableTypeList,
      'xTitle': 'Time (s)',
      
      'yLog': True,
      
      'legendLoc': 'best',
      'legendColumn': 1,
      
      'markersize': 8,
      'linewidth': 2,
      
      'children': [
        {
          'name': '%s-%d-TableEntryCount' % (mobility, speed),
          'figTitle': memoryFile.name,
          'yTitle': 'TableEntryCount',
          'x': range(len(memoryData[0][0])),
          'y': [
            memoryData[tableType][0] for tableType in range(len(tableTypeList))
          ]
        },
        {
          'name': '%s-%d-TableEntrySize' % (mobility, speed),
          'yTitle': 'TableEntrySize (B)',
          'figTitle': memoryFile.name,
          'x': range(len(memoryData[0][0])),
          'y': [
            memoryData[tableType][1] for tableType in range(len(tableTypeList))
          ]
        },
      ]
    }
    
    MultipleLines().draw(data)
    
    tableSum = (tuple(np.zeros(len(memoryData[0][0])) for i in range(2)),
                tuple(np.zeros(len(memoryData[0][0])) for i in range(2)))
    
    for t in range(len(tableTypeList) - 6):
      for d in range(2):
        for i in range(len(memoryData[t][d])):
          tableSum[0][d][i] += memoryData[t][d][i]
    
    for t in range(len(tableTypeList) - 6, len(tableTypeList)):
      for d in range(2):
        for i in range(len(memoryData[t][d])):
          tableSum[1][d][i] += memoryData[t][d][i]
    
    data = {
      'type': "line",
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
      
      'children': [
        {
          'name': '%s-%d-TableEntryCount-aggregated' % (mobility, speed),
          'figTitle': memoryFile.name,
          'yTitle': 'TableEntryCount',
          'x': range(len(memoryData[0][0])),
          'y': [
            tableSum[0][0], tableSum[1][0],
          ]
        },
        {
          'name': '%s-%d-TableEntrySize-aggregated' % (mobility, speed),
          'yTitle': 'TableEntrySize (B)',
          'figTitle': memoryFile.name,
          'x': range(len(memoryData[0][0])),
          'y': [
            tableSum[0][1], tableSum[1][1],
          ]
        }
      ]
    }
    
    MultipleLines().draw(data)
