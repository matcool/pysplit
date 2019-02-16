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

    def __str__(self):
        return f'{self.game_name} {self.category_name} run with {len(self.segments)} segments.\n\
{chr(10).join(self.segments[i].name() for i in range(len(self.segments)))}'

    def __repr__(self):
        return f'<{self.game_name} {self.category_name} run>'

    def update_editor(self):
        name = self.game_name
        category = self.category_name
        with self.edit() as editor:
            editor._editor.set_game_name(name)
            editor._editor.set_category_name(category)

    def add_segment(self, name):
        segment = lscore.Segment.new(name)
        self.segments.append(segment)

    def edit(self):
        return RunEditor(self)

    def timer(self):
        return Timer(self)

    def save(self,path):
        with open(path,'w',encoding='utf-8') as file:
            file.write(self._run.save_as_lss())

class RunEditor:
    def __init__(self, run):
        self.run = run
        self._editor = None
        # self.selected = []
    
    def __enter__(self):
        self.run.editing = True
        game_name = self.run.game_name
        category_name = self.run.category_name
        self._editor = lscore.RunEditor.new(self.run._run)
        self._editor.set_game_name(game_name)
        self._editor.set_category_name(category_name)
        return self

    def __exit__(self, *args):
        self.run._run = self._editor.close()
        self._editor = None
        self.run.editing = False

    # def select(self, index, unselect=True):
    #     if unselect:
    #         self.selected = []
    #     self.selected.append(index)
    #     if unselect:
    #         self._editor.select_only(index)
    #     else:
    #         self._editor.select_additionally(index)

    def edit_segment(i,name=None,icon=None):
        self._editor.select_only(i)
        if name != None:
            self._editor.active_set_name(name)
        if icon == False:
            self._editor.active_remove_icon()
        elif icon != None:
            # not yet implemented
            # self._editor.active_set_icon(icon,icon.length()?)
            pass
    
class SegmentList:
    def __init__(self, run):
        self.run = run

    def __len__(self):
        return self.run._run.len()

    def __getitem__(self,i):
        if i < 0:
            i += len(self)
        if i >= len(self) or i < 0:
            raise IndexError(f'Index out of range: {i}')
        return self.run._run.segment(i)

    def append(self,seg):
        self.run._run.push_segment(seg)

class Timer:
    def __init__(self, run):
        self.run = run
        self._timer = None
        self.update_splits = True

    def __enter__(self):
        self._timer = lscore.Timer.new(self.run._run)
        return self

    def __exit__(self, *args):
        self.run._run = self._timer.into_run(self.update_splits)

    def start(self):
        self._timer.start()

    def split(self):
        self._timer.split()

    def pause(self):
        self._timer.toggle_pause()

    def time(self, timing=None):
        if timing == None:
            timing = self._timer.current_timing_method()
        return self._timer.current_time().index(timing).total_seconds()