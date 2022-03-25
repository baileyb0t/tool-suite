### Makefiles In-depth

Makefiles are extremely handy tools to maintain a directory because, when 
properly configured, they enable automated clearing and rebuilding of I/O files.
This is functionality we rely on to make sure changes to one file can be readily
reflected in downstream tasks and files, as well as ensure reproducibilty of 
our results.

There are many argument options to pass to a makefile once it's setup for a task.
This doc is intended to list and describe a selection of those options which may
be useful for our purposes. The full list can be found [here](https://www.gnu.org/software/make/manual/html_node/Options-Summary.html).

Some of these options expect or can take their own argument, for example
`--max-load`, `--old-file`. As is typical with arg handling, providing an option
with `--` in front requires an `=` to assign the arg, as in `--max-load=n` where
`n` is a float, or `--old-file=file` where `file` is the name of a specific file.
In contrast, an option called with `-` can use a space instead, as in `-l n` and
`-o file`.

#### Options
- `--debug` or `-d` tells make to print debugging information with whatever else
it's doing. There are several arguments you can provide to affect the level or  
condition for debugging, but by default all types of debug info are included.   
    - `all` or `a` tells make to include all types of debugging.                
    - `basic` or `b` tells make to print each out-of-date target and whether it 
    successfully remade the target.                                             
    - `verbose` or `v` tells make to do basic debugging plus include info about 
    which makefiles it checked, which prerequisites didn't need to be remade, etc.
    - `implicit` or `i` tells make to do basic debugging plus include info about
    rule searches for each target.                                              
    - `jobs` or `j` tells make to print info about the details of specific      
    sub-commands encountered when running multiple jobs.                        
    - `makefile` or `m` tells make to do basic debugging plus include info about
    rebuilding makefiles                                                        
    - `none` or `n` tells make to disable any debugging its currently doing     
    until requested again.
- `--help` or `-h` displays the options available to the make call.
- `--jobs` or `-j` tells make to execute multiple recipes in parallel,
via multiple "jobs". This arg may be accompanied by an integer which will be 
treated as the number of jobs to run. If no integer is provided, it will run 
with the default number of jobs which is one (as in serial).
- `--keep-going` or `-k` tells make to keep going and try to remake other targets
after one has failed. It is not best practice to use this regularly but it can 
be useful in remaking as many prerequisites as possible despite an error.
- `--max-load` or `--load-average` or `-l` tells make to limit the number of jobs it will run
based on the existing load on the system. This arg must be accompanied by a
floating point number which will be treated as the load limit, such that `-l n`
will stop `make` from running in parallel when the average system load is above
`n`.
- `--check-symlink-times` or `-L` tells make to consider timestamps of symbolic
links as well as their corresponding files, and use the most recent timestamp
as the modification time for the target file.
- `--recon` or `--dry-run` or `--just-print` or `-n` tells make to print the
recipe that would be executed but do not execute it.
- `--assume-old` or `--old-file` or `-o` tells make to effectively ignore a 
specified file even if its older than its prerequisites. Must provide the file 
as an argument to the option.
- `--output-sync` or `-O`
- `--print-data-base` or `-p` tells make
- `--question` or `-q` tells make
- `--quiet` or `--silent` or `-s` tells make to execute a target without 
printing the recipe.
- `--touch` or `-t` effectively marks files as up-to-date to fool future
make calls, but does not actually execute the target's recipe.
- `--trace` shows the make execution trace, as well as makefile name, recipe
lines in the makefile, and target rebuild reason info.

# done. 
