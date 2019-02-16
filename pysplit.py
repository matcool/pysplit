import core.livesplit_core as lscore

class RunEditorError(Exception): pass

class DisposedError(Exception): pass
def raisePointerError(ptr):
    if ptr == None: raise DisposedError('Pointer is none')

class Run:
    def __init__(self, name=None, category=None):
        self._run = lscore.Run.new()
        self.game_name = property(self._run.game_name,self._run.set_game_name)
        self.category_name = property(self._run.category_name,self._run.set_category_name)
        if name != None: self.game_name = name
        if category != None: self.category_name = category
        self.segments = SegmentList(self)
        self.editing = False

    def __del__(self):
        self._run.drop()

    def add_segment(self, name):
        segment = lscore.Segment.new(name)
        self.segments.append(segment)

    def edit(self):
        return RunEditor(self)

    def __str__(self):
        return f'{self.game_name} {self.category_name} run with {len(self.segments)} segments.\n\
{chr(10).join(self.segments[i].name() for i in range(len(self.segments)))}'

    def __repr__(self):
        return f'<{self.game_name} {self.category_name} run>'

class RunEditor:
    def __init__(self, run):
        self.run = run
        self.editor = None
        # self.selected = []
    
    def __enter__(self):
        self.run.editing = True
        self.editor = lscore.RunEditor.new(self.run._run)
        return self

    def __exit__(self, *args):
        self.run._run = self.editor.close()
        self.editor = None
        self.run.editing = False

    # def select(self, index, unselect=True):
    #     if unselect:
    #         self.selected = []
    #     self.selected.append(index)
    #     if unselect:
    #         self.editor.select_only(index)
    #     else:
    #         self.editor.select_additionally(index)

    def edit_segment(i,name=None,icon=None):
        self.editor.select_only(i)
        if name != None:
            self.editor.active_set_name(name)
        if icon == False:
            self.editor.active_remove_icon()
        elif icon != None:
            # not yet implemented
            # self.editor.active_set_icon(icon,icon.length()?)
            pass
    

class SegmentList:
    def __init__(self, run):
        self.run = run

    def __len__(self):
        return self.run._run.len()

    def __getitem__(self,i):
        return self.run._run.segment(i)

    def append(self,seg):
        self.run._run.push_segment(seg)