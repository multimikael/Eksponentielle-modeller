import wx
import wx.grid
import wxmplot
import numpy as np
import pydux

class GridFrame(wx.Frame):
    def __init__(self, parent, **kwargs):
        super(GridFrame, self).__init__(parent, **kwargs)

        self.OnCreate()

    def OnCreate(self):
        grid = wx.grid.Grid(self)
        grid.CreateGrid(10, 2)

        self.Show()
class MainFrame(wx.Frame):

    def __init__(self, parent, _store, **kwargs):
        super(MainFrame, self).__init__(parent, **kwargs)
        self.store = _store
        self.OnCreate()

    def OnCreate(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        resetItem = fileMenu.Append(wx.ID_RESET, 'Reset', 'Reset Fields')
        exitItem = fileMenu.Append(wx.ID_EXIT, 'Exit', 'Exit Application')
        helpMenu = wx.Menu()
        manualItem = helpMenu.Append(wx.ID_HELP_PROCEDURES, 'Manual', 'Manual to the program')
        aboutItem = helpMenu.Append(wx.ID_ABOUT, 'About', 'About the program')
        menubar.Append(fileMenu, '&File')
        menubar.Append(helpMenu, '&Help')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnExit, exitItem)
        
        mainPanel = wx.Panel(self)
        hboxInputGraph = wx.BoxSizer(wx.HORIZONTAL)
        graphVbox = wx.BoxSizer(wx.VERTICAL)
        inputVbox = wx.BoxSizer(wx.VERTICAL)

        dataBtn = wx.Button(mainPanel, label='View Data')
        deviationHbox = wx.BoxSizer(wx.HORIZONTAL)
        deviationText = wx.StaticText(mainPanel, label='Maximum Deviation: ')
        deviationSpinCtrl = wx.SpinCtrl(mainPanel)
        deviationSpinCtrl.SetRange(0, 100)

        deviationHbox.Add(deviationText, 0, wx.ALL)
        deviationHbox.Add(deviationSpinCtrl, 1, wx.EXPAND|wx.ALL)
        
        filterCheckBox = wx.CheckBox(mainPanel, label='Filter out first and last', style=wx.ALIGN_RIGHT)

        inputVbox.Add(dataBtn, 0, wx.EXPAND|wx.ALL, 5)
        inputVbox.Add(deviationHbox, 0, wx.EXPAND|wx.ALL, 6)
        inputVbox.Add(filterCheckBox, 0, wx.ALL)

        graphsText = wx.StaticText(mainPanel, label='Graphs', style=wx.ALIGN_CENTRE_HORIZONTAL)

        graphVbox.Add(graphsText, 0, wx.EXPAND)

        hboxInputGraph.Add(inputVbox, 3, wx.EXPAND|wx.ALL)
        hboxInputGraph.Add(graphVbox, 1, wx.EXPAND|wx.ALL)
        mainPanel.SetSizer(hboxInputGraph)
        
        self.SetTitle('Eksponentielle Modeller')
        self.Centre()
        self.Show()

    def OnExit(self, event):
        self.Close()

store = pydux.create_store(lambda state, action: True if state is None else not state)
store.subscribe(lambda: print(store.get_state()))
app = wx.App()
MainFrame(None, store)
app.MainLoop()
