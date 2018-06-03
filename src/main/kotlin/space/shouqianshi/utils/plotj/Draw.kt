package space.shouqianshi.utils.plotj

import net.razorvine.pyro.NameServerProxy
import net.razorvine.pyro.PyroException
import net.razorvine.pyro.PyroProxy
import net.sf.json.JSONObject
import net.sf.json.JsonConfig
import java.io.FileOutputStream
import java.io.OutputStreamWriter
import java.util.*

fun draw(configJson: Any, path: String) {
  val config: String =
    if (configJson is JSONObject)
      configJson.toString()
    else if (configJson is String)
      configJson
    else if (configJson is Config)
      JSONObject.fromObject(configJson, JsonConfig()).toString()
    else
      throw Exception("Not implemented")
  
  
  for (i in 0..5) {
    try {
      val ns = NameServerProxy.locateNS("localhost")
      val drawer = PyroProxy(ns.lookup("space.shouqianshi.utils.${path}"))
      
      try {
        drawer.call("draw", config)
      } catch (e: PyroException) {
        e.printStackTrace()
        System.err.println(e.message)
        System.err.println(e._pyroTraceback)
      }
      break
    } catch (e: Exception) {
      System.err.println("An error occurred when connecting to the Pyro server: ")
      e.printStackTrace()
    }
  }
  
  val writer = OutputStreamWriter(FileOutputStream("draw-dump-${Date().time}.txt"))
  writer.write(config)
  writer.close()
}

fun drawParallelBars(configJson: Any) {
  draw(configJson, "parallel_bars")
}

fun drawMultipleLines(configJson: Any) {
  draw(configJson, "multiple_lines")
}

fun main(args: Array<String>) {
  val config = Config("", mutableListOf<PlotConfig>(), listOf("MDT", "AODV"),
    true, true
  )
  
  config.children.add(MultipleLineConfig(
    "signalingReceiveCnt",
    yLog = true,
    
    x = listOf(1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0),
    y = listOf(listOf(300.0, 200.0, 100.0, 200.0, 300.0, 200.0, 100.0),
      listOf(100.0, 300.0, 200.0, 100.0, 200.0, 300.0, 200.0))
  ))
  
  drawMultipleLines(config)
  
  drawParallelBars("""{
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
  
  'children': [
    {
      'name': "insertion",
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
    {
      'name': "ads",
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
  ]
}
  """.trimIndent())
}