from copy import deepcopy
import wx
import wx.grid
import wxmplot
import numpy as np
import pydux

REPLACE_INDEX_VALUE = 'REPLACE_INDEX_VALUE'
ADD_EMPTY_INDEX = 'ADD_EMPTY_INDEX'
POP_LAST_INDEX = 'POP_LAST_INDEX'
SET_DEVIATION = 'SET_DEVIATION'
SET_DO_FILTER = 'SET_DO_FILTER'

INITIALSTATE = {
    'data': [],
    'options': {
        'deviation': 0,
        'doFilter': False
    }
}

def assignNewDict(before, newVals):
    after = deepcopy(before)
    for key in newVals:
        if isinstance(newVals[key], dict):
            after[key] = assignNewDict(after[key], newVals[key])
        else:
            after[key] = newVals[key]
    return after

def replaceIndexValue(index, val1, val2):
    return {'type': REPLACE_INDEX_VALUE, 'index': index, 'val1': val1, 'val2': val2}

def addEmptyIndex(amount):
    return {'type': ADD_EMPTY_INDEX, 'amount': amount}

def popLastIndex(amount):
    return {'type': POP_LAST_INDEX, 'amount': amount}

def setDeviation(value):
    return {'type': SET_DEVIATION, 'value': value}

def setDoFilter(boolean):
    return {'type': SET_DO_FILTER, 'boolean': boolean}

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
    elif action['type'] is POP_LAST_INDEX:
        data = state['data']
        for i in range(action['amount']):
            data.pop()
        return assignNewDict(state, {'data': data})
    elif action['type'] is SET_DEVIATION:
        return assignNewDict(state, {'options': {'deviation': action['value']}})
    elif action['type'] is SET_DO_FILTER:
        return assignNewDict(state, {'options': {'doFilter': action['boolean']}})
    else:
        return state

class GridFrame(wx.Frame):
    ROWS = 10

    def __init__(self, parent, store, **kwargs):
        super(GridFrame, self).__init__(parent, **kwargs)

        self.store = store
        self.store.dispatch(addEmptyIndex(self.ROWS))
        self.OnCreate()

    def OnCreate(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.grid.Grid(panel)
        self.grid.CreateGrid(self.ROWS, 2)
        self.grid.SetColLabelValue(0, 'X')
        self.grid.SetColLabelValue(1, 'Y')

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

        plusBtn.Bind(wx.EVT_BUTTON, self.OnPlusBtn)
        minusBtn.Bind(wx.EVT_BUTTON, self.OnMinusBtn)
        plus10Btn.Bind(wx.EVT_BUTTON, self.OnPlus10Btn)
        minus10Btn.Bind(wx.EVT_BUTTON, self.OnMinus10Btn)

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

    def OnPlusBtn(self, event):
        self.grid.InsertRows(pos=self.grid.GetNumberRows(), numRows=1)
        self.store.dispatch(addEmptyIndex(1))

    def OnPlus10Btn(self, event):
        self.grid.InsertRows(pos=self.grid.GetNumberRows(), numRows=10)
        self.store.dispatch(addEmptyIndex(10))

    def OnMinusBtn(self, event):
        if self.grid.GetNumberRows() > 3:
            self.grid.DeleteRows(pos=self.grid.GetNumberRows()-1, numRows=1)
            self.store.dispatch(popLastIndex(1))

    def OnMinus10Btn(self, event):
        if self.grid.GetNumberRows() > 12:
            self.grid.DeleteRows(pos=self.grid.GetNumberRows()-10, numRows=10)
            self.store.dispatch(popLastIndex(10))



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

        deviationSpinCtrl.Bind(wx.EVT_SPINCTRL,
            lambda event: self.store.dispatch(setDeviation(event.GetPosition())))

        deviationHbox.Add(deviationText, 0, wx.ALL)
        deviationHbox.Add(deviationSpinCtrl, 1, wx.EXPAND|wx.ALL)

        filterCheckBox = wx.CheckBox(
            mainPanel,
            label='Filter out first and last',
            style=wx.ALIGN_RIGHT)

        filterCheckBox.Bind(wx.EVT_CHECKBOX, 
            lambda event: self.store.dispatch(setDoFilter(event.IsChecked())))

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
