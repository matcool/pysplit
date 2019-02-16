# disclaimer
i might discontinue this and just make my own shitty version of livesplit because livesplit-core sucks since its made to be used specifically for livesplit and nothing else<br>
examples:
### editing a segment
make a RunEditor with your current run<br>
select it *(make sure you dont select anything else after or that'll become the active segment)*<br>
change the name<br>
close the runeditor<br>
replace your old run with the one runeditor returns
### setting the run game/category name
this should be simple right?<br>
you could use the `run.set_(game,category)_name(thing)` methods right?<br>
well nope, if you do that and then save your run to an .lss file you'll find that they're nowhere to be found!<br>
to do it properly you have to:<br>
make a runeditor with your current run<br>
set the game/category name icons there<br>
close the editor and replace your old run<br>
<br><br>
PS: I'm not saying livesplit itself is bad, it's just that a lot of stuff that should've just been in the main program is implemented in the core

# pysplit
"pythonic" module built on top of the livesplit-core bindings
<br><br>
extremely not recommended to use in it's current state
# setup
download the bindings from [here](https://github.com/LiveSplit/livesplit-core/releases) *or build it yourself*<br>
then copy the livesplit_core.*dll,so,lib,whatever* and the bindings/livesplit_core.py to a folder named core
