import time
import json
from enum import Enum
# constants
TIMING_FUNCTION = time.perf_counter
DECIMAL_ACCURACY = 7

class TimerState(Enum):
    NOTHING = 0
    RUNNING = 1
    ENDED = 2
    # not yet implemented
    PAUSED = 3

def format_time(s, force_unused=False, decimal_places=DECIMAL_ACCURACY):
    decimal = str(float(s)).split('.')[1]
    s = int(s)
    hours, minutes = divmod(s, 3600)
    minutes, seconds = divmod(minutes, 60)
    pad = lambda x: '0'[len(str(x))-1:]+str(x)
    pad_decimal = lambda x: x[:decimal_places]+('0'*decimal_places)[len(x):]
    return f"{pad(hours)+':' if force_unused else str(hours)+':' if hours != 0 else ''}\
{pad(minutes)+':' if any((hours,force_unused)) else str(minutes)+':' if minutes != 0 else ''}\
{pad(seconds) if any((hours,minutes,force_unused)) else seconds}.{pad_decimal(decimal)}"

class Timer:
    def __init__(self, run=None):
        self.start_time = None
        self.end_time = None
        self.run = run
        self.times = []
        self.state = TimerState.NOTHING
        self.start_offset = 0

    def start(self, force=False):
        if not force and self.state != TimerState.NOTHING:
            raise Exception(f'Timer is currently {self.state.name.lower()}, please reset, finish the run or pass in force=True')
        self.start_time = TIMING_FUNCTION() + self.start_offset
        self.end_time = None
        self.times = []
        self.last_time = 0
        self.state = TimerState.RUNNING

    def time(self, force=False):
        if self.state == TimerState.NOTHING:
            if force:
                return self.start_offset
            else:
                raise Exception('Timer is not currently running.')
        return round((self.end_time if self.state == TimerState.ENDED else TIMING_FUNCTION()) - self.start_time,DECIMAL_ACCURACY)

    def split(self):
        if self.state != TimerState.RUNNING:
            raise Exception('Please start the timer before splitting.')
        t = self.time()
        self.times.append(t - self.last_time)
        self.last_time = t
        if self.run == None or len(self.run.segments) == 0 or len(self.times) == len(self.run.segments):
            self.state = TimerState.ENDED
            self.end_time = t + self.start_time
            if self.run != None:
                self.run.attempts += 1

    def reset(self, save=True):
        if save and self.run != None and len(self.run.segments) > 0:
            for i,t in enumerate(self.times):
                self.run.segments[i].add_time(t)

        if self.state != TimerState.ENDED and self.run != None:
            self.run.attempts += 1

        self.state = TimerState.NOTHING
        self.times = []
        self.start_time = None
        self.end_time = None

class Run:
    def __init__(self, name='', category=''):
        self.name = name
        self.category = category
        self.segments = []
        self.attempts = 0

    def sum_of_best(self):
        if len(self.segments) == 0 or any(map(lambda x: x.best == None,self.segments)): return None
        else: return sum(map(lambda x: x.best, self.segments))

    def save(self, path, lss=False):
        if lss:
            # to be implemented
            return
        else:
            final = self.__dict__.copy()
            final['segments'] = [i.__dict__ for i in self.segments]
            with open(path,'w',encoding='utf-8') as file:
                json.dump(final,file,indent=4)

    @classmethod
    def from_json(cls, path):
        with open(path,encoding='utf-8') as file:
            j = json.load(file)
            run = Run()
            run.__dict__.update(j)
            for j,i in enumerate(run.segments):
                s = Segment()
                s.__dict__.update(i)
                run.segments[j] = s
            return run

class Segment:
    def __init__(self, name=''):
        self.name = name
        self.history = []
        self.best = None

    def add_time(self, time):
        if self.best == None or time < self.best:
            self.best = time
        self.history.append(time)