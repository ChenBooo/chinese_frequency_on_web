# chinese_frequency_on_web
The project is to count the probability that each Chinese character appears on the Internet.

<h1>Init environment</h1>

You can run master and slave on different host. So I seperate master and slave requirments.txt each.
just run 
<p align="center">pip install -r requirments.txt</p>
to build the run environment.

<h1>Start</h1>

you should consider start master.py in master floder first. use
<p align="center">python master.py</p>

when you start master.py, you should alway create the "w_file" that configurable in master/cfg.json.
add some start page url to enable spiders.

after the master run. now, you can start one or more slave to do the information collection. You should
know, the slave will spiders a whole website before it response to master. so if you want to start servel
slave at the first time. Please be sure there are enough start url in master's "w_file".

you can start slave by:
<p align="center">python salve.py</p>

When you got some data, they saved in s_file, w_file and c_file. You can stop and restart anytime you want. and you will be able to continue you work as long as your s_file, w_file and c_file are fine.

Whole project build on Python3.5, so it can't run on python2.X.

And there are also some useful tools help to display the result we get.
