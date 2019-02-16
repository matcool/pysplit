from pysplit import *

run = Run(name='Something',category='Any%')

to_type = ['Hello','World']
for i in to_type:
    run.segments.append(Segment(name='Type '+i))

timer = Timer(run)
timer.start()
for i in to_type:
    msg = ''
    while msg != i:
        msg = input(f'QUICK!!! Type {i}: ')
    timer.split()

print(f'Congratulations! You took {formatTime(timer.time())}s to type: {", ".join(to_type)}')
timer.reset()
print('\n'.join(f'{i.name} - {i.best}' for i in run.segments))