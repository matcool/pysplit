import time
import json
from enum import Enum
import xml.etree.ElementTree as ElTree
# constants
TIMING_FUNCTION = time.perf_counter
DECIMAL_ACCURACY = 7

class TimerState(Enum):
    NOTHING = 0
    RUNNING = 1
    ENDED = 2
    # not yet implemented
    PAUSED = 3

def format_time(s, force_unused=False, decimal_places=None):
    if s == None:
        return '-'
    prefix = '-' if s < 0 else ''
    s = abs(s)
    if decimal_places == None: decimal_places = DECIMAL_ACCURACY
    decimal = s % 1
    s = int(s)
    hours, minutes = divmod(s, 3600)
    minutes, seconds = divmod(minutes, 60)
    pad = lambda x: '0'[len(str(x))-1:]+str(x)
    pad_decimal = lambda x: str(x)[:decimal_places]+('0'*decimal_places)[len(str(x)):]
    return f"{prefix}{pad(hours)+':' if force_unused else str(hours)+':' if hours != 0 else ''}\
{pad(minutes)+':' if any((hours,force_unused)) else str(minutes)+':' if minutes != 0 else ''}\
{pad(seconds) if any((hours,minutes,force_unused)) else seconds}{'.' + pad_decimal(decimal) if decimal_places != False else ''}"

def parse_time(s):
    s = s.split(':')
    t = float(s[-1])
    s.pop(-1)
    for i,s in enumerate(reversed(s)):
        t += int(s)*(60**(i+1))
    return t

class Timer:
    def __init__(self, run=None):
        self.start_time = None
        self.end_time = None
        self.run = run
        self.times = []
        self.state = TimerState.NOTHING
        self.start_offset = 0 if self.run == None else self.run.start_offset

    def start(self, force=False):
        if not force and self.state != TimerState.NOTHING:
            raise Exception(f'Timer is currently {self.state.name.lower()}, please reset, finish the run or pass in force=True')
        self.start_time = TIMING_FUNCTION() + self.start_offset
        self.end_time = None
        self.times = []
        self.last_time = 0
        self.state = TimerState.RUNNING
        if self.run != None:
            self.run.attempts += 1

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

    def reset(self, save=True):
        if save and self.run != None and len(self.run.segments) > 0:
            pb = self.run.pb_time()
            segments = self.run.segments
            for i,t in enumerate(self.times):
                segments[i].add_time(t)
                if self.state == TimerState.ENDED and (segments[i].pb == None or pb > self.time()):
                    segments[i].pb = t

        self.state = TimerState.NOTHING
        self.times = []
        self.start_time = None
        self.end_time = None

    def __repr__(self):
        return f'<Timer currently {self.state.name}>'

class Run:
    def __init__(self, name='', category=''):
        self.name = name
        self.category = category
        self.segments = []
        self.attempts = 0
        self.start_offset = 0

    def sum_of_best(self):
        if len(self.segments) == 0 or any(map(lambda x: x.best == None,self.segments)): return None
        else: return sum(map(lambda x: x.best, self.segments))

    def pb_time(self):
        s = 0
        for i in self.segments:
            if i.pb == None:
                return None
            s += i.pb
        return s

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

    @classmethod
    def from_lss(cls, path, time='RealTime'):
        run = Run()
        tree = ElTree.parse(path).getroot()
        alias = [('GameName','name'),('CategoryName','category'),('Offset','start',parse_time),('AttemptCount','attempts',int)]
        for i in alias:
            e = tree.find(i[0]).text
            if len(i) == 3: e = i[2](e)
            setattr(run, i[1], e)

        p = 0
        for seg in tree.find('Segments'):
            s = Segment(seg.find('Name').text)
            for i in seg.find('SegmentHistory'):
                s.add_time(parse_time(i.find(time).text))
            t = parse_time(seg.find('SplitTimes')[0].find(time).text)
            s.pb = t-p
            p = t
            run.segments.append(s)

        return run

    def __repr__(self):
        return f'<{self.name} {self.category} run with {len(self.segments)} segments>'

class Segment:
    def __init__(self, name=''):
        self.name = name
        self.history = []
        self.best = None
        self.pb = None

    def add_time(self, time):
        if self.best == None or time < self.best:
            self.best = time
        self.history.append(time)

    def __repr__(self):
        return f'<{self.name} Segment>'