import wx
import wx.grid
import wxmplot
import numpy as np
import pydux
from copy import deepcopy

REPLACE_INDEX_VALUE = 'REPLACE_INDEX_VALUE'
ADD_EMPTY_INDEX = 'ADD_EMPTY_INDEX'

INITIALSTATE = {
    'data': [],
    'options': {
        'deviation': 0,
        'filter': False
    }
}

def assignNewDict(before, newVals):
    after = deepcopy(before)
    for key in newVals:
        after[key] = newVals[key]
    return after

def replaceIndexValue(index, val1, val2):
    return {'type': REPLACE_INDEX_VALUE, 'index': index, 'val1': val1, 'val2': val2}

def addEmptyIndex(amount):
    return {'type': ADD_EMPTY_INDEX, 'amount': amount}

def reducer(state, action):
    if state is None:
        return INITIALSTATE
    if action['type'] is REPLACE_INDEX_VALUE:
        data = state['data']
        data.pop(action['index'])
        data.insert(action['index'], (action['val1'], action['val2']))
        return assignNewDict(state, {'data': data})
    elif action['type'] is ADD_EMPTY_INDEX:
        data = state['data']
        for i in range(action['amount']):
            data.append(())
        return assignNewDict(state, {'data': data})
    else:
        return state

class GridFrame(wx.Frame):
    ROWS = 10
    COL = 2

    def __init__(self, parent, store, **kwargs):
        super(GridFrame, self).__init__(parent, **kwargs)

        self.store = store
        self.OnCreate()

    def OnCreate(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.grid.Grid(panel)
        self.grid.CreateGrid(self.ROWS, self.COL)
        self.grid.SetColLabelValue(0, 'X')
        self.grid.SetColLabelValue(1, 'Y')

        self.store.dispatch(addEmptyIndex(self.ROWS))

        self.grid.Bind(wx.grid.EVT_GRID_CELL_CHANGED,
            lambda event: self.store.dispatch(replaceIndexValue(event.GetRow(),
                self.grid.GetCellValue(event.GetRow(), 0),
                self.grid.GetCellValue(event.GetRow(), 1)
        )))

        inputHbox = wx.BoxSizer(wx.HORIZONTAL)
        plusBtn = wx.Button(panel, label='+')
        minusBtn = wx.Button(panel, label='-')
        plus10Btn = wx.Button(panel, label='+10')
        minus10Btn = wx.Button(panel, label='-10')
        resetBtn = wx.Button(panel, label='Reset')

        plusBtn.Bind(wx.EVT_BUTTON, lambda event: self.grid.InsertRows(numRows=1))
        minusBtn.Bind(
            wx.EVT_BUTTON,
            lambda event: self.grid.DeleteRows(numRows=1) if self.grid.GetNumberRows() > 3 else False)
        plus10Btn.Bind(wx.EVT_BUTTON, lambda event: self.grid.InsertRows(numRows=10))
        minus10Btn.Bind(
            wx.EVT_BUTTON,
            lambda event: self.grid.DeleteRows(numRows=10) if self.grid.GetNumberRows() > 12 else False)

        inputHbox.AddMany([
            (plusBtn, 0, wx.ALL),
            (minusBtn, 0, wx.ALL),
            (plus10Btn, 0, wx.ALL),
            (minus10Btn, 0, wx.ALL),
            (resetBtn, 0, wx.ALL)
        ])

        vbox.Add(self.grid, 1, wx.EXPAND)
        vbox.Add(inputHbox, 0, wx.ALL)

        panel.SetSizer(vbox)
        self.Show()

class MainFrame(wx.Frame):

    def __init__(self, parent, store, **kwargs):
        super(MainFrame, self).__init__(parent, **kwargs)
        self.store = store
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
        GridFrame(self, self.store)

    def OnExit(self, event):
        self.Close()

_store = pydux.create_store(reducer)
_store.subscribe(lambda: print(_store.get_state()))
app = wx.App()
MainFrame(None, _store)
app.MainLoop()
