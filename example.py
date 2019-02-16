from pysplit import *

run = Run(name='Pysplit',category='Something%')
run.add_segment('test')

# set game and category name
with run.edit() as editor:
    pass

with run.timer() as timer:
    print(timer.time())
    timer.start()
    input('Hey bro')
    timer.split()
    print(timer.time())

run.save('test.lss')


# reference:

# timer = Timer.new(run)
# timer.start()
# input('type:')
# timer.split()
# print(f'that took {timer.current_time().real_time().total_seconds()}s')
# timer.reset(True)