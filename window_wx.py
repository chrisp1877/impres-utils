import wx.py as wx

class Frame(wx.Frame):
    def __init__(self, title):
        wx.Frame.__init__(self, None, title=title, size=(350,200))
        self.Bind(wx.EVT_CLOSE, self.OnClose)

    def OnClose(self, event):
        dlg = wx.MessageDialog(self, 
            "Do you really want to close this application?",
            "Confirm Exit", wx.OK|wx.CANCEL|wx.ICON_QUESTION)
        result = dlg.ShowModal()
        dlg.Destroy()
        if result == wx.ID_OK:
            self.Destroy()

    '''
        self.fg_locx_entry = Entry(Root)
        self.fg_locy_entry = Entry(Root)
        self.bg_locx_entry = Entry(Root)
        self.bg_locy_entry = Entry(Root)
        self.labelFrame = LabelFrame(self, text = "Open File")

        self.fg_locx_entry.grid(row=0, column=0)
        self.fg_locy_entry.grid(row=0, column=1)
        self.bg_locx_entry.grid(row=0, column=0)
        self.bg_locy_entry.grid(row=0, column=1)
        '''