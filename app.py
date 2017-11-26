from copy import deepcopy
from functools import reduce
import threading
import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled
import wxmplot
import numpy as np
import pydux

REPLACE_INDEX_VALUE = 'REPLACE_INDEX_VALUE'
ADD_EMPTY_INDEX = 'ADD_EMPTY_INDEX'
POP_LAST_INDEX = 'POP_LAST_INDEX'
SET_DEVIATION = 'SET_DEVIATION'
SET_DO_FILTER = 'SET_DO_FILTER'
NEW_MANUAL_GRAPH = 'NEW_MANUAL_GRAPH'

INITIALSTATE = {
    'data': [(0, 15), (20, 16), (40, 18), (60, 19),
             (80, 22), (100, 24), (140, 31), (160, 42),
             (180, 49), (200, 67), (220, 78), (240, 90),
             (260, 105), (280, 109), (300, 122), (320, 125)],
    'options': {
        'deviation': 0,
        'doFilter': False
    },
    'graphs': {
        'manualGraph': {},
        'manualStartingInZero': {},
        'manualLog': {},
        'autoGraph': {},
        'autoStartingInZero': {},
        'autoLog': {}
    }
}

#Side 286 Mat1
def findA(x_1, y_1, x_2, y_2):
    return (y_1/y_2)**(1/(x_1-x_2))

def findB(a, x_1, y_1):
    return y_1/(a**x_1)

def averageA(data):
    print('data A: ', data)
    product = 0
    for ds in data:
        if ds != ():
            if product is 0:
                product = ds
            else:
                product = product*ds
    return product**(1/len(data))

def average(data):
    _sum = reduce(lambda x, y: x+y, data)
    return _sum/len(data)

def findDeviation(obs, tabel):
    return (obs-tabel)/tabel

def numeric(x):
    if x >= 0.0:
        return x
    else:
        return x*-1.0

def makeFunction(x, a, b):
    print('function a', a)
    print('function b', b)
    return {'f': b*a**x, 'a': a, 'b': b}

def findAcceptable(data, deviation):
    print(data)
    results = []
    tempResult = []
    prevA = 0.0
    for i in range(len(data)-1):
        ds1 = data[i]
        ds2 = data[i+1]
        a = findA(ds2[0], ds2[1], ds1[0], ds1[1])
        if i is len(data)-2:
            results.append(tempResult)
        elif prevA != 0.0:
            print(numeric(findDeviation(a, prevA)))
            if numeric(findDeviation(a, prevA)) <= deviation/100:
                print(True)
                if tempResult is []:
                    tempResult.append(ds1)
                tempResult.append(ds2)
            else:
                results.append(tempResult)
        else:
            prevA = a
    print(results)
    return results

def findFunction(data, x):
    """ returns {function, a, b}. function should be numpy"""
    print('data: ', data)
    aData = []
    bData = []
    prevDs = ()
    for ds in data:
        if prevDs:
            aData.append(findA(ds[0], ds[1], prevDs[0], prevDs[1]))
        prevDs = ds
    if len(aData) > 1:
        a = averageA(aData)
    else:
        return None
    for ds in data:
        bData.append(findB(a, ds[0], ds[1]))
    b = average(bData)
    return makeFunction(x, a, b)

def findManualGraph(data, deviation):
    """ returns a list with {points, function}"""
    results = []
    for dl in findAcceptable(data, deviation):
        results.append({'f': findFunction(dl, findLinspace(dl)), 'points': dl})
    return results

def findStaringInZero(graphs, x):
    """ takes a list of graphs """
    results = []
    for graph in graphs:
        bData = []
        for point in graph['points']:
            bData.append(findB(graph['f']['a'], point[0], point[1]))
        results.append(makeFunction(x, graph['f']['a'], average(bData)))
    return results

def findLinspace(points):
    xMin = points[len(points)-1][0]
    xMax = points[0][0]
    print("xMin: ", xMin)
    print('xMax: ', xMax)
    return np.linspace(xMin, xMax)

def manualGraphPanel(parent, manualGraphs):
    print('manualGraphs: ', manualGraphs)
    panel = wxmplot.PlotPanel(parent, size=(450, 450))
    if manualGraphs != {}:
        for graph in manualGraphs:
            print('graph: ', graph)
            if graph['f'] != None:
                xdata = findLinspace(graph['points'])
                panel.plot(xdata, graph['f']['f'])
            for point in graph['points']:
                print('point: ', point)
                panel.scatterplot(np.array([point[0]]), np.array([point[1]]))
    return panel



# ACTION CREATORS

def newManualGraph(manualGraph):
    return {'type': NEW_MANUAL_GRAPH, 'manualGraph': manualGraph}

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
        if action['index']:
            data.pop(action['index'])
        print('index', action['index'])
        print('val1', action['val1'])
        print('val2', action['val2'])
        data.insert(action['index'], (float(action['val1']), float(action['val2'])))
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
    elif action['type'] is NEW_MANUAL_GRAPH:
        return assignNewDict(state, {
            'graphs': {
                'manualGraph': action['manualGraph']
            }
        })
    else:
        return state

class ThreadWithCallback(threading.Thread):
    def __init__(self, callback=None, targetArgs=None, *args, **kwargs):
        super().__init__(target=self.targetAndCallback, *args, **kwargs)
        self.callback = callback
        self.targetArgs = targetArgs

    def setCallback(self, callback):
        self.callback = callback

    def setTarget(self, target):
        self.method = target

    def setTargetArgs(self, args):
        self.targetArgs = args

    def targetAndCallback(self):
        print('lol')
        result = self.method(*self.targetArgs)
        if self.callback != None:
            self.callback(result)

class GraphsPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, graphs):
        super().__init__(parent)
        self.graphs = graphs
        self.graphPanels = []
        self.OnCreate()

    def OnCreate(self):
        self.vBox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vBox)
        self.SetupScrolling(scroll_x=False)

    def removeVBoxChildren(self):
        self.vBox.Clear()
        self.Layout()
        self.graphPanels = []

    def AddGraphsToVBox(self, graphs):
        self.vBox.Add(manualGraphPanel(self, graphs), 0, wx.EXPAND)
        self.Layout()
        self.graphPanels.append(manualGraphPanel(self, graphs))

    def Update(self, graphs):
        super().Update()
        self.removeVBoxChildren()
        self.AddGraphsToVBox(graphs)


class GridFrame(wx.Frame):
    ROWS = 10

    def __init__(self, parent, store, **kwargs):
        super().__init__(parent, **kwargs)

        self.store = store
        #self.store.dispatch(addEmptyIndex(self.ROWS))
        self.OnCreate()

    def OnCreate(self):
        panel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)
        self.grid = wx.grid.Grid(panel)
        self.grid.CreateGrid(self.ROWS, 2)
        self.grid.SetColLabelValue(0, 'X')
        self.grid.SetColLabelValue(1, 'Y')
        self.grid.SetColFormatFloat(0)
        self.grid.SetColFormatFloat(1)

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
        self.SetMinSize(wx.Size(1280, 720))
        self.store = store
        self.OnCreate()
        self.Layout()
        self.Fit()
        self.Centre()
        self.workThread = ThreadWithCallback()

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
        self.graphVbox = wx.BoxSizer(wx.VERTICAL)
        inputVbox = wx.BoxSizer(wx.VERTICAL)

        dataBtn = wx.Button(mainPanel, label='View Data')
        dataBtn.Bind(wx.EVT_BUTTON, self.OnDataBtn)

        deviationHbox = wx.BoxSizer(wx.HORIZONTAL)
        deviationText = wx.StaticText(mainPanel, label='Maximum Deviation: ')
        deviationSpinCtrl = wx.SpinCtrl(mainPanel)
        deviationSpinCtrl.SetRange(0, 100)

        deviationSpinCtrl.Bind(wx.EVT_SPINCTRL, self.OnDeviationBtn)

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

        #Graphs
        graphsText = wx.StaticText(mainPanel, label='Graphs', style=wx.ALIGN_CENTRE_HORIZONTAL)
        graphsPanel = GraphsPanel(mainPanel, self.store.get_state()['graphs']['manualGraph'])

        self.store.subscribe(lambda: graphsPanel.Update(self.store.get_state()['graphs']['manualGraph']))

        self.graphVbox.Add(graphsText, 0, wx.EXPAND, 8)
        self.graphVbox.Add(graphsPanel, 1, wx.EXPAND, 8)

        hboxInputGraph.Add(inputVbox, 3, wx.EXPAND|wx.ALL)
        hboxInputGraph.Add(self.graphVbox, 1, wx.EXPAND|wx.ALL)
        mainPanel.SetSizer(hboxInputGraph)

        self.SetTitle('Eksponentielle Modeller')
        self.Show()

    def OnDeviationBtn(self, event):
        self.store.dispatch(setDeviation(event.GetPosition()))
        self.workThread.setTarget(findManualGraph)
        self.workThread.setTargetArgs((self.store.get_state()['data'],
            self.store.get_state()['options']['deviation']))
        self.workThread.setCallback(lambda results: self.store.dispatch(newManualGraph(results)))
        self.workThread.start()

    def OnDataBtn(self, event):
        GridFrame(self, self.store)

    def OnExit(self, event):
        self.Close()

_store = pydux.create_store(reducer)
_store.subscribe(lambda: print(_store.get_state()))
app = wx.App()
MainFrame(None, _store)
app.MainLoop()
