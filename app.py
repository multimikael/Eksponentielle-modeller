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
