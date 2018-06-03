package space.shouqianshi.utils.plotj

open class Config(
  val name: String = "",
  val children: MutableList<PlotConfig>,
  
  val solutionList: List<String>,
  
  val display: Boolean = true,
  val output: Boolean = true,
  
  val figWidth: Double = 6.0,
  val figHeight: Double = 3.5,
  val legendLoc: String = "best",
  val legendColumn: Int = 1,
  
  val xTitle: String = "",
  val yTitle: String = "",
  
  val mainColors: List<String> = mutableListOf("#0072bc", "#d85119", "#edb021")
)

interface PlotConfig

class ParallelBarConfig(
  val name: String = "",
  val solutionList: List<String>,
  
  val yLog: Boolean = false,
  val yGrid: Boolean = false,
  
  val y: List<List<Double>> = listOf(),
  val yLimit: List<Double> = listOf(),
  val yrange: List<List<Pair<Double, Double>>> = listOf(),
  
  val environmentList: List<String>,
  
  val display: Boolean = true,
  val output: Boolean = true,
  
  val figWidth: Double = 6.0,
  val figHeight: Double = 3.5,
  val legendLoc: String = "best",
  val legendColumn: Int = 1,
  
  val xTitle: String = "",
  val yTitle: String = "",
  
  val mainColors: List<String> = mutableListOf("#0072bc", "#d85119", "#edb021"),
  
  val paddingLeft: Double = 0.2,
  val paddingRight: Double = 0.0,
  val margin: Double = 0.4,
  val marginMiddle: Double = 0.02
) : PlotConfig

class MultipleLineConfig(
  val name: String = "",
  
  val solutionList: List<String> = listOf(),
  val x: List<Double>,
  val y: List<List<Double>>,
  
  val xLog: Boolean = false,
  val xGrid: Boolean = false,
  val yLog: Boolean = false,
  val yGrid: Boolean = false,
  
  val xLimit: List<Double> = listOf(),
  val xrange: List<List<Double>> = listOf(),
  
  val yLimit: List<Double> = listOf(),
  val yrange: List<List<Double>> = listOf(),
  
  val display: Boolean = true,
  val output: Boolean = true,
  
  val figWidth: Double = 6.0,
  val figHeight: Double = 3.5,
  val legendLoc: String = "best",
  val legendColumn: Int = 1,
  
  val xTitle: String = "",
  val yTitle: String = "",
  
  val mainColors: List<String> = mutableListOf("#0072bc", "#d85119", "#edb021"),
  
  val markersize: Int = 8,
  val linewidth: Int = 2
) : PlotConfig
