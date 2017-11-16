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
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        grid = wx.grid.Grid(panel)
        grid.CreateGrid(10, 2)
        grid.SetColLabelValue(0, 'X')
        grid.SetColLabelValue(1, 'Y')

        inputHbox = wx.BoxSizer(wx.HORIZONTAL)
        plusBtn = wx.Button(panel, label='+')
        minusBtn = wx.Button(panel, label='-')
        plus10Btn = wx.Button(panel, label='+10')
        minus10Btn = wx.Button(panel, label='-10')
        resetBtn = wx.Button(panel, label='Reset')

        plusBtn.Bind(wx.EVT_BUTTON, lambda event: grid.InsertRows(numRows=1))
        minusBtn.Bind(
            wx.EVT_BUTTON,
            lambda event: grid.DeleteRows(numRows=1) if grid.GetNumberRows() > 3 else False)
        plus10Btn.Bind(wx.EVT_BUTTON, lambda event: grid.InsertRows(numRows=10))
        minus10Btn.Bind(
            wx.EVT_BUTTON,
            lambda event: grid.DeleteRows(numRows=10) if grid.GetNumberRows() > 12 else False)

        inputHbox.AddMany([
            (plusBtn, 0, wx.ALL),
            (minusBtn, 0, wx.ALL),
            (plus10Btn, 0, wx.ALL),
            (minus10Btn, 0, wx.ALL),
            (resetBtn, 0, wx.ALL)
        ])

        vbox.Add(grid, 1, wx.EXPAND)
        vbox.Add(inputHbox, 0, wx.ALL)

        panel.SetSizer(vbox)
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
        dataBtn.Bind(wx.EVT_BUTTON, self.OnDataBtn)

        deviationHbox = wx.BoxSizer(wx.HORIZONTAL)
        deviationText = wx.StaticText(mainPanel, label='Maximum Deviation: ')
        deviationSpinCtrl = wx.SpinCtrl(mainPanel)
        deviationSpinCtrl.SetRange(0, 100)

        deviationHbox.Add(deviationText, 0, wx.ALL)
        deviationHbox.Add(deviationSpinCtrl, 1, wx.EXPAND|wx.ALL)

        filterCheckBox = wx.CheckBox(
            mainPanel,
            label='Filter out first and last',
            style=wx.ALIGN_RIGHT)

        inputVbox.Add(dataBtn, 0, wx.EXPAND|wx.ALL, 5)
        inputVbox.Add(deviationHbox, 0, wx.EXPAND|wx.ALL, 6)
        inputVbox.Add(filterCheckBox, 0, wx.ALL)

        graphsText = wx.StaticText(mainPanel, label='Graphs', style=wx.ALIGN_CENTRE_HORIZONTAL)
        graphScroll = wx.ScrolledWindow(mainPanel)

        graphVbox.Add(graphsText, 0, wx.EXPAND, 8)
        graphVbox.Add(graphScroll, 1, wx.EXPAND, 8)

        hboxInputGraph.Add(inputVbox, 3, wx.EXPAND|wx.ALL)
        hboxInputGraph.Add(graphVbox, 1, wx.EXPAND|wx.ALL)
        mainPanel.SetSizer(hboxInputGraph)

        self.SetTitle('Eksponentielle Modeller')
        self.Centre()
        self.Show()

    def OnDataBtn(self, event):
        GridFrame(self)

    def OnExit(self, event):
        self.Close()

store = pydux.create_store(lambda state, action: True if state is None else not state)
store.subscribe(lambda: print(store.get_state()))
app = wx.App()
MainFrame(None, store)
app.MainLoop()
