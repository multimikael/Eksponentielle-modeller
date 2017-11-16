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
        quitItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit Application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)

        mainPanel = wx.Panel(self)
        
        self.SetTitle('Eksponentielle Modeller')
        self.Centre()
        self.Show()

    def OnQuit(self, event):
        self.Close()

store = pydux.create_store(lambda state, action: True if state is None else not state)
store.subscribe(lambda: print(store.get_state()))
app = wx.App()
MainFrame(None, store)
app.MainLoop()
