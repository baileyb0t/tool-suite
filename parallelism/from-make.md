### Parallelism from Makefiles

GNU enables Makefiles to run scripts in parallel instead of serial by 
providing certain arguments to the `make` call. This doc is intended to 
summarize this functionality, explain those argument options, and provide sample
commands.

It's important to note that while the capability to run in parallel will always
exist, the number of parallel executions commanding resources can kill a system
for other users, so you should always know the number of cores available on a 
system and consider how many are in use before letting make consume all those 
available resources. This can inform either or both of the arguments provided
to `--jobs` and `--max-load`.

#### Functionality
Makefiles are already equipped to run scripts and compile targets as executed.
In addition, certain arguments can be provided to a `make` call to enable more
advanced compiling. See the full set of options [here](https://www.gnu.org/software/make/manual/html_node/Options-Summary.html).
These are useful when you have a strong understanding of what work a script is
doing and how it will access the filesystem, so you can optimize that usage.

#### Options
- `--jobs` or just `-j` tells make to execute multiple recipes in parallel,
via multiple "jobs". This arg may be accompanied by an integer which will be 
treated as the number of jobs to run. If no integer is provided, it will run 
with the default number of jobs which is one (as in serial).
- `--max-load` or `-l` tells make to limit the number of jobs it will run
based on the existing load on the system. This arg must be accompanied by a
floating point number which will be treated as the load limit, such that `-l n`
will stop make from running in parallel when the average system load is above
 `n`.
- `--output-sync` or `-O` tells make to print output from multiple recipes in
one uninterrupted sequence. By default, the output will be grouped by target,
but `line` can also be used to group by target line instead of target. 
This is handy when a target logs or display info.

#### Examples
To tell make to execute target-name using 5 jobs and to sync the output, run:
    `make target-name -j 5 -O`
To tell make to execute target-name in parallel without pushing the average 
system load past 5, run:
    `make target-name --max-load=5`
To tell make to execute target-name using 5 jobs, without pushing the average
system load past 8.5 jobs, and sync the output by line while doing so, run:
    `make target-name -j 5 -l 8.5 --output-sync=line`

##### done.
