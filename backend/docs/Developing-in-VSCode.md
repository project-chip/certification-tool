# Developing Matter TH Backend in VSCode

This guide will explain the most basic development 

### Run in debbugger
- Backend can be started in debug mode via the green play button in 
Run and Debug tab in sidebar. (Also with <kbd>F5</kbd>)
- <kbd>⌘ Command</kbd> + <kbd>⇧ Shift</kbd> + <kbd>F5</kbd> will restart the process
- breakpoints can be set by clicking to the left of a python line


### Use git in VSCode
You can use git integration in VSCode, from inside the container.

**Note:** if you get an error with public key denied, you need to share your ssh key
with ssh-agent. See platform specific guide here: 
(https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials)[https://code.visualstudio.com/remote/advancedcontainers/sharing-git-credentials]

## Testing

Tests are implemented with `pytest` and stored in `tests` folder in the root of the 
project.

- VSCode will automatically discover tests in the project
- Tests can be run from the Testing tab in the sidebar or individually by clicking the 
testing icon in the code view, to the left of the line number, on the line declaring the
test.
- Tests also be run in debug mode by right-clicking and selecting `Debug Test`.

To run all tests and generate code coverage report run shell script `scripts/test.sh`.

## Linting, formatting and type checking

The project is configured to be 
- linted with `flake8`
- autoformated via `black` and `isort`, 
- type checked with `mypy`
- spell checked with `cspell`

All of these are automatically running on save-file in VSCode, and problems identified
will be shown in the PROBLEMS tab (<kbd>⌘ Command</kbd> + <kbd>⇧ Shift</kbd> + <kbd>M</kbd>).

- Linting is also available via shell script in `scripts/lint.sh`
- Autoformatting is also available via shell script in `scripts/format.sh`


## Reset DB
-   Run the `scripts/reset_db.py` file to drop and create a database, and run all the database migrations.