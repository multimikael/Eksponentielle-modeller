import wx

class mainFrame(wx.Frame):

    def __init__(self, *args, **kwargs):
        super(mainFrame, self).__init__(*args, **kwargs)

        self.OnCreate()

    def OnCreate(self):
        menubar = wx.MenuBar()
        fileMenu = wx.Menu()
        quitItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit Application')
        menubar.Append(fileMenu, '&File')
        self.SetMenuBar(menubar)

        self.Bind(wx.EVT_MENU, self.OnQuit, quitItem)

        panel = wx.Panel(self)
        hbox = wx.BoxSizer(wx.HORIZONTAL)
        popupButton = wx.Button(panel, label='Popup')
        drawButton = wx.Button(panel, label='Draw')
        hbox.Add(popupButton, 1, wx.EXPAND)
        hbox.Add(drawButton, 1, wx.EXPAND)
        panel.SetSizer(hbox)

        self.SetTitle('Eksponentielle Modeller')
        self.Centre()
        self.Show()

    def OnQuit(self, event):
        self.Close()

app = wx.App()
mainFrame(None)
app.MainLoop()
