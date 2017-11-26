from copy import deepcopy
from functools import reduce
import threading
import wx
import wx.grid
import wx.lib.scrolledpanel as scrolled
import wxmplot
import numpy as np
import pydux
import math

REPLACE_INDEX_VALUE = 'REPLACE_INDEX_VALUE'
ADD_EMPTY_INDEX = 'ADD_EMPTY_INDEX'
POP_LAST_INDEX = 'POP_LAST_INDEX'
SET_DEVIATION = 'SET_DEVIATION'
SET_DO_FILTER = 'SET_DO_FILTER'
NEW_MANUAL_GRAPH = 'NEW_MANUAL_GRAPH'
NEW_ZERO_GRAPH = 'NEW_ZERO_GRAPH'
NEW_LOG_GRAPH = 'NEW_LOG_GRAPH'

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
        'zeroGraph': {},
        'logGraph': {}
    }
}

#Side 286 Mat1

def findLinearA(x_1, y_1, x_2, y_2):
    return (y_2-y_1)/(x_2-x_1)

def findLinearB(a, x_1, y_1):
    return y_1-a*x_1

def findPowerA(x_1, y_1, x_2, y_2):
    return (y_1/y_2)**(1/(x_1-x_2))

def findPowerB(a, x_1, y_1):
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

def makePowerFunction(x, a, b):
    print('function a', a)
    print('function b', b)
    return {'f': b*a**x, 'a': a, 'b': b}

def makeLinearFunction(x, a, b):
    return {'f': a*x+b, 'a': a, 'b': b}

def findPowerAcceptable(data, deviation):
    print(data)
    results = []
    tempResult = []
    prevA = 0.0
    for i in range(len(data)-1):
        ds1 = data[i]
        ds2 = data[i+1]
        a = findPowerA(ds2[0], ds2[1], ds1[0], ds1[1])
        if i is len(data)-2:
            results.append(tempResult)
        elif prevA != 0.0:
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

def findPowerFunction(data, x):
    """ returns {function, a, b}. function should be numpy"""
    aData = []
    bData = []
    prevDs = ()
    for ds in data:
        if prevDs:
            aData.append(findPowerA(ds[0], ds[1], prevDs[0], prevDs[1]))
        prevDs = ds
    if len(aData) > 1:
        a = averageA(aData)
    else:
        return None
    for ds in data:
        bData.append(findPowerB(a, ds[0], ds[1]))
    b = average(bData)
    return makePowerFunction(x, a, b)

def findLinearFunction(data, x):
    """ returns {function, a, b}. function should be numpy"""
    aData = []
    bData = []
    prevDs = ()
    for ds in data:
        if prevDs:
            aData.append(findLinearA(prevDs[0], prevDs[1], ds[0], ds[1]))
        prevDs = ds
    if len(aData) > 1:
        a = average(aData)
    else:
        return None
    for ds in data:
        bData.append(findLinearB(a, ds[0], ds[1]))
    b = average(bData)
    return makeLinearFunction(x, a, b)

def findManualGraph(data, deviation, doFilter):
    """ returns a list with {points, function}"""
    if doFilter:
        data.pop(0)
        data.pop()
    results = []
    for dl in findPowerAcceptable(data, deviation):
        results.append({'f': findPowerFunction(dl, findLinspace(dl)), 'points': dl})
    return results

def findZeroGraph(data, deviation, doFilter):
    """ takes a list of graphs """
    first = data[0]
    print('frist', first)
    data = list(map(lambda x: (x[0]-first[0], x[1]), data))
    return findManualGraph(data, deviation, doFilter)

def findLogGraph(data, deviation, doFilter):
    if doFilter:
        data.pop(0)
        data.pop()
    results = []
    for dl in findPowerAcceptable(data, deviation):
        logList = list(map(
            lambda x: (math.log10(x[0]), math.log10(x[1])), dl))
        results.append({
            'f': findLinearFunction(logList, findLinspace(logList)),
            'points': logList
        })
    return results

def findLinspace(points):
    xMin = points[len(points)-1][0]
    xMax = points[0][0]
    return np.linspace(xMin, xMax)

def graphPanel(parent, graphs):
    panel = wxmplot.PlotPanel(parent, size=(450, 450))
    print('graphs: ', graphs)
    for graph in graphs:
        print('graph: ', graph)
        if graph['f'] != None:
            xdata = findLinspace(graph['points'])
            panel.plot(xdata, graph['f']['f'])
        for point in graph['points']:
            panel.scatterplot(np.array([point[0]]), np.array([point[1]]))
    return panel



# ACTION CREATORS

def newLogGraph(logGraph):
    return {'type': NEW_LOG_GRAPH, 'logGraph': logGraph}

def newZeroGraph(zeroGraph):
    return {'type': NEW_ZERO_GRAPH, 'zeroGraph': zeroGraph}

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
    elif action['type'] is NEW_ZERO_GRAPH:
        return assignNewDict(state, {
            'graphs': {
                'zeroGraph': action['zeroGraph']
            }
        })
    elif action['type'] is NEW_LOG_GRAPH:
        return assignNewDict(state, {
            'graphs': {
                'logGraph': action['logGraph']
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
        result = self.method(*self.targetArgs)
        if self.callback != None:
            self.callback(result)

class GraphsPanel(scrolled.ScrolledPanel):
    def __init__(self, parent, graphs):
        super().__init__(parent)
        self.graphs = graphs
        self.OnCreate()

    def OnCreate(self):
        self.vBox = wx.BoxSizer(wx.VERTICAL)
        self.SetSizer(self.vBox)
        self.SetupScrolling(scroll_x=False)

    def removeVBoxChildren(self):
        self.vBox.Clear()

    def AddGraphsToVBox(self, graphs):
        for graph in graphs:
            if graphs[graph] != {}:
                self.vBox.Add(GPanelWithButton(self, graphs[graph]), 0, wx.EXPAND)

    def Update(self, graphs):
        super().Update()
        self.removeVBoxChildren()
        self.AddGraphsToVBox(graphs)
        self.Layout()

class GPanelWithButton(wx.Panel):
    def __init__(self, parent, graph, **kwargs):
        super().__init__(parent, **kwargs)

        self.graph = graph
        self.OnCreate()
    
    def OnCreate(self):
        vbox = wx.BoxSizer(wx.VERTICAL)
        
        g = graphPanel(self, self.graph)
        btn = wx.Button(self, label='Expand')
        btn.Bind(wx.EVT_BUTTON, lambda event: GraphFrame(self, self.graph))

        vbox.Add(g, 0, wx.EXPAND)
        vbox.Add(btn, 0, wx.EXPAND)
        
        self.SetSizer(vbox)

class GraphFrame(wx.Frame):

    def __init__(self, parent, graph, **kwargs):
        super().__init__(parent, **kwargs)

        self.graph = graph
        self.SetMinSize(wx.Size(1280, 720))
        self.OnCreate()
        self.Fit()
        self.Centre()

    def OnCreate(self):
        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)

        gPanel = graphPanel(panel, self.graph)
        vbox = wx.BoxSizer(wx.VERTICAL)

        statisticsLabel = wx.StaticText(panel, label='Statistics', style=wx.ALIGN_CENTRE_HORIZONTAL)

        vbox.Add(statisticsLabel, 0, wx.EXPAND)

        for g in self.graph:
            gridSizer = wx.FlexGridSizer(3, 2, 8, 8)
            if g['f'] != None:
                aLabel = wx.StaticText(panel, label='a: ')
                aVal = wx.StaticText(panel, label=str(g['f']['a']), style=wx.ALIGN_RIGHT)
                bLabel = wx.StaticText(panel, label='b: ')
                bVal = wx.StaticText(panel, label=str(g['f']['b']), style=wx.ALIGN_RIGHT)
            pointsLabel = wx.StaticText(panel, label='points: ')
            pointsString = ""
            for point in g['points']:
                pointsString = pointsString + "(%f, %f) \n" % (point[0], point[1])
            pointsVal = wx.StaticText(panel, label=pointsString, style=wx.ALIGN_RIGHT)
            gridSizer.AddMany([
                (aLabel, 1, wx.EXPAND), (aVal, 0, wx.ALL), 
                (bLabel, 1, wx.EXPAND), (bVal, 0, wx.ALL),
                (pointsLabel, 1, wx.EXPAND), (pointsVal, 0, wx.ALL)
            ])
            vbox.Add(gridSizer, 0, wx.EXPAND)

        hbox.Add(gPanel, 3, wx.EXPAND)
        hbox.Add(vbox, 1, wx.ALL)

        panel.SetSizer(hbox)

        self.Show()
        

class GridFrame(wx.Frame):
    ROWS = 10

    def __init__(self, parent, store, **kwargs):
        super().__init__(parent, **kwargs)

        self.store = store
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
        self.store = store
        self.SetMinSize(wx.Size(1280, 720))
        self.OnCreate()
        self.Layout()
        self.Fit()
        self.Centre()

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

        filterCheckBox.Bind(wx.EVT_CHECKBOX, self.OnFilterCB)

        inputVbox.Add(dataBtn, 0, wx.EXPAND|wx.ALL, 5)
        inputVbox.Add(deviationHbox, 0, wx.EXPAND|wx.ALL, 6)
        inputVbox.Add(filterCheckBox, 0, wx.ALL)

        #Graphs
        graphsText = wx.StaticText(mainPanel, label='Graphs', style=wx.ALIGN_CENTRE_HORIZONTAL)
        self.graphsPanel = GraphsPanel(mainPanel, self.store.get_state()['graphs']['manualGraph'])

        self.graphVbox.Add(graphsText, 0, wx.EXPAND, 8)
        self.graphVbox.Add(self.graphsPanel, 1, wx.EXPAND, 8)

        hboxInputGraph.Add(inputVbox, 3, wx.EXPAND|wx.ALL)
        hboxInputGraph.Add(self.graphVbox, 1, wx.EXPAND|wx.ALL)
        mainPanel.SetSizer(hboxInputGraph)

        self.SetTitle('Eksponentielle Modeller')
        self.Show()

    def OnFilterCB(self, event):
        self.store.dispatch(setDoFilter(event.IsChecked()))
        self.NewGraph()

    def OnDeviationBtn(self, event):
        self.store.dispatch(setDeviation(event.GetPosition()))
        self.NewGraph()

    def OnDataBtn(self, event):
        GridFrame(self, self.store)

    def NewGraph(self):
        self.store.dispatch(newManualGraph(
            findManualGraph(self.store.get_state()['data'],
                self.store.get_state()['options']['deviation'], 
                self.store.get_state()['options']['doFilter'])))
        self.store.dispatch(newZeroGraph(
            findZeroGraph(self.store.get_state()['data'],
                self.store.get_state()['options']['deviation'], 
                self.store.get_state()['options']['doFilter'])))
        self.store.dispatch(newLogGraph(
            findLogGraph(self.store.get_state()['data'],
                self.store.get_state()['options']['deviation'], 
                self.store.get_state()['options']['doFilter'])))
        self.graphsPanel.Update(self.store.get_state()['graphs'])

    def OnExit(self, event):
        self.Close()

_store = pydux.create_store(reducer)
_store.subscribe(lambda: print(_store.get_state()))
app = wx.App()
MainFrame(None, _store)
app.MainLoop()
