`run` command and `Runfile`
====

`run` command and `Runfile` is similar to `make` command and `Makefile`, but for tasks.

# features
- run functions/tasks in `Makefile`
- list task names;
- generate sample `Runfile`;
- supports command completion with TAB key;
- 3 versions: python(most updated), javascript and bash

# install
```bash
# python version
curl -OL https://raw.githubusercontent.com/simpzan/run/main/run.py && python3 run.py .install
# js version
curl -OL https://raw.githubusercontent.com/simpzan/run/main/js/run.js && bun run.js .install
# bash version
curl -OL https://raw.githubusercontent.com/simpzan/run/main/sh/run.sh && bash run.sh
```

# use
## create Runfile file
If there's no `Runfile` in current directory, run `run` command will create the file.

## list tasks in `Runfile`
If there is `Runfile` in current directory, run `run` command will list the tasks.
Or just run `./Runfile`.

## run a task
run `run help` to run the `help` task in `Runfile`.
Or just run `./Runfile help`.

## auto complete task name
When cursor is at the end of `run `, press Tab button will auto complete task names
