`run` command and `Runfile`
====

`run` command and `Runfile` is similar to `make` command and `Makefile`, but for shell tasks.

# features
- implemented in simple bash, no dependencies;
- supports bash and zsh;
- supports command completion with TAB key;
- list task names;
- generate sample `Runfile`;

# install
```bash
curl https://raw.githubusercontent.com/simpzan/run/main/Runfile.rc -o `mktemp` && bash $_
```

# use
## create Runfile file
If there's no `Runfile` in current directory, run `run` command will create the file.

## list tasks in `Runfile`
If there is `Runfile` in current directory, run `run` command will list the tasks.
Or just run `./Runfile`.

## auto complete task name
When cursor is at the end of `run `, press Tab button will auto complete task names

## run a task
run `run hello` to run the `hello` task in `Runfile`.
Or just run `./Runfile hello`.

# Runfile
see [Runfile](Runfile) for an example.
