import pcbnew
import wx
import os

class test_plugin(pcbnew.ActionPlugin):
    """Class that gathers the actionplugin stuff"""
    def defaults(self):
        self.name = "test"
        self.category = "Export PCB"
        self.description = "Export PCB to format used by DAPE models"
        self.show_toolbar_button = True
        self.icon_file_name = os.path.join(os.path.dirname(__file__), 'icon.png')

    def Run(self):
        board: pcbnew.BOARD = pcbnew.GetBoard()

        if board.IsEmpty():
            dlg = wx.MessageDialog(None,
                'Hello KiCad',
                'Demo',
                wx.OK
            )
            dlg.ShowModal()
            dlg.Destroy()
            return

        return


        # app = wx.App(False)
        #
        # frame = wx.Frame(None, wx.ID_ANY, "Test_plugin")
        # frame.SetSize(wx.Size(250, 100))
        #
        # label = wx.StaticText(frame, label="Hello KiCad")
        #
        # sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(label, 0, wx.ALL, 5)
        #
        # frame.SetSizer(sizer)
        #
        # frame.Show()
        # app.MainLoop()

