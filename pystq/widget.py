import numpy as np
import ipywidgets as pywidgets
import pystq.score as score
import pystq.sites as sites
import pystq.materials as materials
# From imports
from pystq.detector import Detector
from IPython.display import display
from ipywidgets import interactive
# From imports for Bokeh
from bokeh.models import Legend, Label
from bokeh.io import push_notebook, show, output_notebook
from bokeh.plotting import figure
# Select a palette for plotting
from bokeh.palettes import Dark2_8 as palette
from bokeh.palettes import Category20_20 as palettelight
from bokeh.models.formatters import TickFormatter, NumeralTickFormatter
output_notebook(hide_banner=True)


# Set up 'Space-Time Quest'-like game class
class spaceTimeQuest:

   # Initialise the game
   def __init__(self, init_vals={}):
      # Interactive detector
      self.detector = Detector(init_vals)
      # Detector parameter keys
      self.keys = list(self.detector.parameters.keys())
      # Informative names to print on widgets
      self.names = self.detector.names
      # Score calculator used in game
      self.scorecalculator = score.ScoreCalculator(self.detector)
      # Initial y-axis limits
      self.yLo = 1E-25
      self.yHi = 1E-21
      # Initialise plot
      self.initPlot()
      # Initialise widgets
      self.pyw = self.initWidgets()
      # Initialise both styles of interaction:
      # Accordion-style widget container
      self.accordion = self.Accordion()
      # Drop-down menu style widget container
      self.dropdown = self.DropDown()
      # Drop-down menu style widget container
      self.tabs = self.Tabs()
      
   # Calculate percentage of budget blown
   def budgetMsg(self):
      print(str(int(score.CalcCost(self.detector)/self.detector.parameters['site'].budget*100.0)) +\
            "% of budget blown")

   # Print everything calculated about the capabilities of the detector
   def printscore(self):
      self.budgetMsg()
      s = self.scorecalculator.CalcScore()

      print("""
        Score: {score} Mpc
            - NSNS Range: {nsnsr:.2f} Mpc
            - BHBH Range: {bhbhr:.2f} Mpc
            - No. NSNS: {nsns:.0f} ({nsnsm} of these missed)
            - No. BHBH: {bhbh:.0f} ({bhbhm} of these missed)
            - No. Nova: {nova:.0f} ({novam} of these missed)
        """.format(
         score=s.score,
         nsns=s.nsns,
         nsnsm=s.nsnsMissed,
         nsnsr=s.nsnsRange,
         bhbh=s.bhbh,
         bhbhm=s.bhbhMissed,
         bhbhr=s.bhbhRange,
         nova=s.supernovae,
         novam=s.supernovaeMissed))

      print("Cost: ${:.0f} (${:.0f} remaining)".format(score.CalcCost(self.detector), \
           (self.detector.parameters['site'].budget - score.CalcCost(self.detector))))
      print("Complexity: {:.2f}".format(score.CalcComplex(self.detector)))

   # Set y-limits of the plot
   def setPlotYLim(self, hLo, hHi):
      self.plot.y_range.start = hLo
      self.plot.y_range.end = hHi

   # Define the style and position of the plot legend
   def layoutLegend(self, legends):
      legend = Legend(items=legends, location=(15, 60))
      self.plot.add_layout(legend, 'right')
      self.plot.legend.background_fill_alpha = 0.4
      self.plot.legend.label_text_font_size = '9pt'
      self.plot.legend.orientation = "vertical"
      self.plot.legend.padding = 0
      self.plot.legend.label_width = 130
      self.plot.legend.glyph_width = 7

   # Initialise the plot embedded in the Jupyter notebook
   def initPlot(self):
      # TODO adf 14022018, added this for bokeh workaround, remoave after fixing
      import warnings
      warnings.filterwarnings('ignore')
      TickFormatter
      self.plot = figure(
         plot_height=350,
         plot_width=750,
         x_axis_type='log',
         y_axis_type='log',
         title='Detector Noise',
         y_axis_label='h [1/\u221AHz]',
         x_axis_label='f [Hz]',
         toolbar_location='right',
         toolbar_sticky=False,
         tools="ypan, save, reset")
      self.setPlotYLim(self.yLo, self.yHi)
      self.plot.title.offset = self.plot.plot_width * (2 / 3)
      self.plot.yaxis.major_label_orientation = 'horizontal'
      #self.plot.axis.axis_label_text_font = 'italic'
      self.plot.axis.axis_label_text_font_size = '11pt'
      self.plot.axis.major_label_text_font_size = '10pt'
      fi = self.detector.parameters['freqrange'][0]
      ff = self.detector.parameters['freqrange'][1]
      self.scorecalculator.SetFreqRange(fi, ff)
      x, y, self.names = self.scorecalculator.GetNoiseCurves()
      self.legends = []
      self.colours = {}
      self.lines = {}
      for i, yi in enumerate(y):
         self.colours[self.names[i]] = palette[i]
         # TODO: fix this, adf 14.02.2018
         # the following is a workaround for a Bokeh bug which
         # causes lines to not be clipped at the X/Y limits
         # See: https://github.com/bokeh/bokeh/issues/6787
         yi=np.array(yi)
         x=np.array(x)
         idxs = np.nonzero((yi<=self.yHi) & (yi>=self.yLo))[0]
         self.lines[self.names[i]] = self.plot.line(x[idxs], yi[idxs], color=palette[i], \
                                                    line_width=3)
         self.legends.append((self.names[i], [self.lines[self.names[i]]]))
      self.layoutLegend(self.legends)
      # show freq axis as 1 10 ... 10k
      self.plot.xaxis.formatter=NumeralTickFormatter(format="0 a")
      self.plot.output_backend = "svg"
      self.handle = show(self.plot, notebook_handle=True)

   # Update the existing plot
   def drawToPlot(self):
      fi = self.detector.parameters['freqrange'][0]
      ff = self.detector.parameters['freqrange'][1]
      self.scorecalculator.SetFreqRange(fi, ff)
      x, y, names = self.scorecalculator.GetNoiseCurves()
      for i, yi in enumerate(y):
         # TODO: fix this, adf 14.02.2018
         # the following is a workaround for a Bokeh bug which
         # causes lines to not be clipped at the X/Y limits
         # See: https://github.com/bokeh/bokeh/issues/6787
         yi=np.array(yi)
         x=np.array(x)
         idxs = np.nonzero((yi<=self.yHi) & (yi>=self.yLo))[0]

         if names[i] not in self.names:
            self.colours[names[i]] = palettelight[i]
            self.lines[names[i]] = self.plot.line(x[idxs], yi[idxs], color=palettelight[i], \
                                                  line_width=10)
            label = Label(x=x[int(len(x)/2)], y=yi[int(len(yi)/2)],
                          text=names[i], x_offset=7, y_offset=3, level='glyph', \
                          render_mode='canvas', text_color=palettelight[i], \
                          text_font_size='8pt')
            self.plot.add_layout(label)
         else:
            self.lines[names[i]].data_source.data['x'] = x[idxs]
            self.lines[names[i]].data_source.data['y'] = yi[idxs]
      for nm in self.names:
         if nm not in names:
            self.lines[nm].data_source.data['x'] = x
            self.lines[nm].data_source.data['y'] = [0] * len(x)
      push_notebook()

   # Initialise all of the widgets
   def initWidgets(self):
      rangerList = []
      sliderList = []
      choiceList = []
      for key in self.keys:
         if type(self.detector.parameters[key]) == tuple:
            rangerList.append(key)
         elif key in self.detector.limits:
            sliderList.append(key)
         else:
            choiceList.append(key)

      w = {}

      for key in rangerList:
         w[key] = pywidgets.FloatRangeSlider(
            value=self.detector.parameters[key],
            min=self.detector.limits[key][0],
            max=self.detector.limits[key][1],
            step=0.1,
            description=' ',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='')

      for key in sliderList:
         w[key] = pywidgets.FloatSlider(
            value=self.detector.parameters[key],
            min=self.detector.limits[key][0],
            max=self.detector.limits[key][1],
            step=0.1,
            description=' ',
            disabled=False,
            continuous_update=False,
            orientation='horizontal',
            readout=True,
            readout_format='')
         if key == 'sus_stages':
            w[key].step = 1

      for key in choiceList:
         str_value = str(self.detector.parameters[key])
         str_value = str_value.split('\'')[1]
         str_value = str_value.split('.')[-1]
         w[key] = pywidgets.ToggleButtons(
            options=self.detector.options[key],
            value=str_value,
            description=' ',
            disabled=False,
            continuous_update=False)

      # Set up boolean widgets for dictating which noise curves are calculated
      for key in self.names:
         w[key] = pywidgets.Checkbox(
            value=True, description=str(key), disabled=False)
      return w

   # Update detector
   def updateDetector(self):
      for key in self.keys:
         self.detector.parameters[key] = self.pyw[key].value
      for key in self.names:
         if key != 'Total':
            self.scorecalculator.SetNoiseUsed(key, self.pyw[key].value)

      if ("Jungle" in str(self.detector.parameters['site'])):
         self.detector.parameters['site'] = sites.Jungle
      elif ("Desert" in str(self.detector.parameters['site'])):
         self.detector.parameters['site'] = sites.Desert
      elif ("City" in str(self.detector.parameters['site'])):
         self.detector.parameters['site'] = sites.City
      elif ("Island" in str(self.detector.parameters['site'])):
         self.detector.parameters['site'] = sites.Island
      else:
         print("Unrecognised location")

      if ("Silicon" in str(self.detector.parameters['material'])):
         self.detector.parameters['material'] = materials.Silicon
      elif ("Silica" in str(self.detector.parameters['material'])):
         self.detector.parameters['material'] = materials.Silica
      elif ("Sapphire" in str(self.detector.parameters['material'])):
         self.detector.parameters['material'] = materials.Sapphire
      elif ("Crystal" in str(self.detector.parameters['material'])):
         self.detector.parameters['material'] = materials.Crystal
      else:
         print("Unrecongnised material")

   # Set up the tasks that each widget controls
   def configureWidgetTasks(self):
      # Link pywidgets to updating plot
      def u(widge):
         self.updateDetector()
         self.drawToPlot()
         self.budgetMsg()

      # Link check boxes to updating plot
      def c(widge):
         self.updateDetector()
         self.drawToPlot()

      # Science run button function
      def b(widge):
         print('Fetching score...')
         self.updateDetector()
         self.printscore()

      # Y-axis limit change slider
      def y(widge):
         self.setPlotYLim(pow(10, widge[0]), pow(10, widge[1]))
         self.drawToPlot()

      # Set up science run button
      button = pywidgets.Button(
         description='Run',
         disabled=False,
         button_style='',
         tooltip='Science Run',
         icon='check')
      button.on_click(b)

      # Set up y-axis scaling range slider
      yrange = pywidgets.FloatRangeSlider(
         value=(np.log10(self.yLo), np.log10(self.yHi)),
         min=-27,
         max=-18,
         step=1,
         description=' ',
         disabled=False,
         continuous_update=False,
         orientation='horizontal',
         readout=True,
         readout_format='')

      nList = list(self.pyw[key] for key in self.names[0:-1])
      actionList_n = [pywidgets.interactive(c, widge=w) for w in nList]
      checkBoxedHi = pywidgets.HBox(actionList_n[:int(len(actionList_n) / 4)])
      checkBoxedM1 = pywidgets.HBox(
         actionList_n[int(len(actionList_n) / 4):int(len(actionList_n) / 2)])
      checkBoxedM2 = pywidgets.HBox(actionList_n[int(
         len(actionList_n) / 2):int(3 * len(actionList_n) / 4)])
      checkBoxedLo = pywidgets.HBox(
         actionList_n[int(3 * len(actionList_n) / 4):])
      checkBoxed = pywidgets.VBox(
         [checkBoxedHi, checkBoxedM1, checkBoxedM2, checkBoxedLo])

      actionDict = {}
      actionDict['Noise Curve Options'] = checkBoxed
      actionDict['h-range [1/\u221AHz]'] = pywidgets.interactive(
         y, widge=yrange)
      actionDict['Science Run'] = button

      for key in self.keys:
         actionDict[self.detector.names[key]] = pywidgets.interactive(
            u, widge=self.pyw[key])

      return actionDict

     # Set up Accordion-style widget container
   def Tabs(self):
      actions = self.configureWidgetTasks()
      tabs = pywidgets.Tab(children=[actions[k] for k in actions])
      for i, key in enumerate(actions):
         tabs.set_title(i, key)
      return tabs


   # Set up Accordion-style widget container
   def Accordion(self):
      actions = self.configureWidgetTasks()
      accordion = pywidgets.Accordion(children=[actions[k] for k in actions])
      for i, key in enumerate(actions):
         accordion.set_title(i, key)
      return accordion

   # Set up drop-down menu-style widget container
   def DropDown(self):
      actions = self.configureWidgetTasks()

      def printwidget(wid):
         display(wid)

      choices = pywidgets.Dropdown(
         options=actions,
         description='Action: ',
         disabled=False,
      )

      dropdown = pywidgets.interactive(printwidget, wid=choices)

      return dropdown
