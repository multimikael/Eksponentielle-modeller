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
        self.store.subscribe(self.OnStoreChange)
        self.OnCreate()

    def OnCreate(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        quitItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit Application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)

        mainPanel = wx.Panel(self)
        vbox = wx.BoxSizer(wx.VERTICAL)

        self._plotPanel = wxmplot.plotpanel.PlotPanel(mainPanel, size=(1, 1))

        btnPanel = wx.Panel(mainPanel)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        popupBtn = wx.Button(btnPanel, label='Popup')
        drawBtn = wx.Button(btnPanel, label='Draw')
        hbox.Add(popupBtn, 1, wx.EXPAND)
        hbox.Add(drawBtn, 1, wx.EXPAND)
        btnPanel.SetSizer(hbox)

        popupBtn.Bind(wx.EVT_BUTTON, self.OnPopupButton)
        drawBtn.Bind(wx.EVT_BUTTON, self.OnDrawButton)

        vbox.Add(self._plotPanel, 3, wx.EXPAND)
        vbox.Add(btnPanel, 1, wx.EXPAND)
        mainPanel.SetSizer(vbox)
        self.SetTitle('Eksponentielle Modeller')
        self.Centre()
        self.Show()

    def OnQuit(self, event):
        self.Close()

    def OnPopupButton(self, event):
        GridFrame(self)

    def OnDrawButton(self, event):
        self.store.dispatch({'type': ''})

    def OnStoreChange(self):
        x = np.linspace(0.0, 10.0, 100.0)
        self._plotPanel.plot(x, np.exp(x**2.0), title='Expo test', xmax=10.0, ymax=10.0)

store = pydux.create_store(lambda state, action: True if state is None else not state)
store.subscribe(lambda: print(store.get_state()))
app = wx.App()
MainFrame(None, store)
app.MainLoop()
