import wx
import pysplit
import copy

class configMenu(wx.Frame):
    def __init__(self, run, *args, **kw):
        super(configMenu, self).__init__(*args, **kw)
        self.run = run
        self.panel = wx.Panel(self)

        w, h = self.GetSize()

        btn_ok = wx.Button(self.panel, label='Ok', size=(80,30), pos=(w-200,h-80))
        btn_ok.Bind(wx.EVT_BUTTON,self.close)

        btn_cancel = wx.Button(self.panel, label='Cancel', size=(80,30), pos=(w-110,h-80))
        def _cancel(evt):
            self.run = None
            self.close(evt)
        btn_cancel.Bind(wx.EVT_BUTTON,_cancel)

        label_category = wx.StaticText(self.panel, pos=(10,45), label='Category name')
        self.text_category = wx.TextCtrl(self.panel, pos=(20+label_category.GetSize()[0],40), value=self.run.category)

        label_name = wx.StaticText(self.panel, pos=(10,15), label='Game name')
        self.text_name = wx.TextCtrl(self.panel, pos=(20+label_category.GetSize()[0],10), value=self.run.name)

        label_attempts = wx.StaticText(self.panel, pos=(10,75), label='Attempts')
        self.text_attempts = wx.TextCtrl(self.panel, pos=(20+label_category.GetSize()[0],70), value=str(self.run.attempts), size=(45,23))

        label_offset = wx.StaticText(self.panel, pos=(10,105), label='Timer Offset')
        self.text_offset = wx.TextCtrl(self.panel, pos=(20+label_category.GetSize()[0],100), value=str(self.run.start_offset), size=(45,23))

        # segments
        self.segments = copy.deepcopy(self.run.segments)

        btn_addseg = wx.Button(self.panel, label='Add Segment', pos=(5,150), size=(110,23))
        btn_addseg.Bind(wx.EVT_BUTTON,self.add_segment)

        btn_remseg = wx.Button(self.panel, label='Remove Segment', pos=(5,180), size=(110,23))
        btn_remseg.Bind(wx.EVT_BUTTON,self.remove_segment)

        btn_editseg = wx.Button(self.panel, label='Edit Segment', pos=(5,210), size=(110,23))
        btn_editseg.Bind(wx.EVT_BUTTON,self.edit_segment)

        btn_moveu = wx.Button(self.panel, label='Move Up', pos=(5,240), size=(110,23))
        btn_moveu.Bind(wx.EVT_BUTTON,self.move)

        btn_moved = wx.Button(self.panel, label='Move Down', pos=(5,270), size=(110,23))
        btn_moved.Bind(wx.EVT_BUTTON,lambda x: self.move(down=True))

        self.list_segments = wx.ListCtrl(self.panel, pos=(120,150), style=wx.LC_REPORT|wx.LC_EDIT_LABELS, size=(w-200,h-300))
        self.update_segments()
        
    def close(self, *args):
        if self.run != None:
            self.run.name = self.text_name.GetLineText(0)
            self.run.category = self.text_category.GetLineText(0)
            self.run.attempts = int(self.text_attempts.GetLineText(0))
            self.run.start_offset = pysplit.parse_time(self.text_offset.GetLineText(0))
            self.run.segments = self.segments
        self.Close()

    def add_segment(self, *args):
        i = self.list_segments.GetFocusedItem() + 1
        if i == 0: i = len(self.segments)
        self.segments.insert(i, pysplit.Segment())
        self.segments[i].pb = 0
        self.segments[i].best = 0
        d = SegmentEditor(self, title='Segment Editor', segment=self.segments[i], callback=self.update_segments)
        d.Show()

    def select_one(self):
        if self.list_segments.GetSelectedItemCount() != 1:
            wx.MessageBox('Please select (only) one segment')
            return None
        return self.list_segments.GetFocusedItem()

    def remove_segment(self, *args):
        i = self.select_one()
        if i == None: return
        self.segments.pop(i)
        self.update_segments()

    def edit_segment(self, *args):
        i = self.select_one()
        if i == None: return
        d = SegmentEditor(self, title='Segment Editor', segment=self.segments[i], callback=self.update_segments)
        d.Show()

    def move(self, *a, down=False):
        i = self.select_one()
        if i == None: return
        t = i+1 if down else i-1
        t %= len(self.segments)
        self.segments[t], self.segments[i] = self.segments[i], self.segments[t]
        self.update_segments()
        # doesnt work for some reason
        self.list_segments.Select((t) % len(self.segments))

    def update_segments(self):
        self.list_segments.ClearAll()
        for i in ('Name','Personal Best','Best Time'): self.list_segments.AppendColumn(i)
        for i in self.segments:
            self.list_segments.Append((i.name,pysplit.format_time(i.pb,decimal_places=2),pysplit.format_time(i.best,decimal_places=2)))

    @classmethod
    def open(cls, timer):
        app = wx.App()
        # disable the dumb warning you get when closing
        app.SetAssertMode(wx.APP_ASSERT_SUPPRESS)
        frame = cls(timer, None, title='Pysplit Config', size=(800,600))
        frame.Show()
        app.MainLoop()

class SegmentEditor(wx.Dialog):
    def __init__(self, parent, title, segment, callback):
        super(SegmentEditor, self).__init__(parent, title=title)
        self.segment = segment
        self.callback = callback
        self.panel = wx.Panel(self)

        w,h = self.GetSize()

        label_name = wx.StaticText(self.panel, pos=(5,10), label='Name')
        label_pb = wx.StaticText(self.panel, pos=(5,40), label='PB Time')
        label_best = wx.StaticText(self.panel, pos=(5,70), label='Best Time')

        self.name = wx.TextCtrl(self.panel, pos=(100,10), value=self.segment.name)
        self.pb = wx.TextCtrl(self.panel, pos=(100,40), value=pysplit.format_time(self.segment.pb,decimal_places=2))
        self.best = wx.TextCtrl(self.panel, pos=(100,70), value=pysplit.format_time(self.segment.best,decimal_places=2))

        btn_ok = wx.Button(self.panel, label='Ok', pos=(w//2-50,h-100))
        btn_ok.Bind(wx.EVT_BUTTON,self.on_close)

        self.Bind(wx.EVT_CLOSE, self.on_close)

    def on_close(self, event):
        self.segment.name = self.name.GetLineText(0)
        self.segment.pb = pysplit.parse_time(self.pb.GetLineText(0))
        self.segment.best = pysplit.parse_time(self.best.GetLineText(0))
        self.callback()
        self.Destroy()