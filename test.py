from pysplit import *

run = Run(name='Something',category='Any%')

to_type = ['Hello','World']
for i in to_type:
    run.segments.append(Segment(name='Type '+i))

timer = Timer(run)
def do_run():
    timer.start()
    for i in to_type:
        msg = ''
        while msg != i:
            msg = input(f'QUICK!!! Type {i}: ')
        timer.split()

    print(f'Congratulations! You took {format_time(timer.time())}s to type: {", ".join(to_type)}')
    timer.reset()
    print('\n'.join(f'{i.name} - {i.history[-1]}' for i in run.segments))

do_run()
run.save('test.json')