# EBM DataLab's default notebook environment

![status](https://github.com/ebmdatalab/custom-docker/workflows/Notebook%20checks/badge.svg)

This is a skeleton project for creating a reproducible, cross-platform
analysis notebook, using Docker.  It also includes:

* configuration for `jupytext`, to support easier code review
* cross-platform startup scripts
* best practice folder structure and documentation

## Start and configure your new project

To get started, [create a new
repository](https://github.com/organizations/ebmdatalab/repositories/new)
using this repo as a template, and clone it to your local machine.

Your new repo's name should end with `-notebook`, to make it clear what it
is.

Then replace this front matter with information about your project. You should:
   1.  keep the rest of the contents to help other users of this package
   2.  keep the status badge at the top, changing
     `custom-docker` to the name of your repo
   3. edit the URL of the "quick start" button and the "nbviewer"
     link below to match the name of your new repo

Notebooks live in the `notebooks/` folder (with an `ipynb`
extension). You can most easily view them [on
nbviewer](https://nbviewer.jupyter.org/github/ebmdatalab/seb-docker-test/tree/master/notebooks/),
though looking at them in Github should also work.

You can view *and interact* with any notebooks in the `notebooks/`
folder by launching the notebook in the free online service,
[![Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/ebmdatalab/custom-docker/master).

Any changes you make there won't be saved; to do development work,
you'll need to set up a local jupyter server and git repository.

## Structure of repo

Each repo will have this basic folder structure. For more information, please see our [Open Analytics Manifesto](https://docs.google.com/document/d/1LD5hVjFOWx1AptbXkdTS135ureLkxd8kCumgl8mxzaA/)

```bash
├── code
│   └── custom_functions.py
├── config
│   └── jupyter_notebook_config
├── data
├── notebooks
├── tests
├── .gitattributes
├── .gitignore
├── Dockerfile
├── README.md
├── requirements.in
├── requirements.txt
├── run.bat
├── run.sh
└── run_tests.sh

```

By convention, all Jupyter notebooks live in `notebooks/`.

When notebooks look like they will contain more than a few lines of Python,
the Python is separated into a separate module, in `code/`, and
imported from the notebook.

Data, including raw and processed data, should be stored within the `data/` folder. Paths can be created easily with
the `os` module. For more information, see [teaching resources]().

Tests live in `tests/` folder. Tests are run automatically with [pytest](https://docs.pytest.org/en/latest/). This library
will find any python files called `test_*.py` and then find any functions called `test_*()`.  Tests also verify
that notebooks are runnable with identical output.

`config/` contains the configuration required to run the Notebook; you
shouldn't have to touch this.

## Developing notebooks

There are two ways of getting started with a development environment:
with Docker, or using Python virtual environments.

Docker allows you to run identical software on all platforms. In
Windows, in particular, there are challenges ensuring all python
packages are exactly the same as those available on other platforms.

### Docker enviroment

#### Installation

Follow installation instructions
[here](https://docs.docker.com/install/). Docker Desktop is generally preferred over Docker Toolbox. If running on Windows, you
may find it useful first to refer to our own installation notes
[here](https://github.com/ebmdatalab/custom-docker/issues/4) which cover Desktop/Toolbox and other installation questions.

Windows users who log into an Active Directory domain (i.e. a network
login) may find they lack permissions to start Docker correctly. If
so, follow [these
instructions](https://github.com/docker/for-win/issues/785#issuecomment-344805180).

#### Start notebook

The first time you do this, it may take some time, as the (large) base
Docker image must be downloaded. On Linux or OS X:

    ./run.sh

On Windows, double-click `run.bat`.

This will start a Jupyter Lab server in a Docker container. You will
be able to access this in your web browser at http://localhost:8888/.
Changes made in the Docker container will appear in your own
filesystem, and can be committed as usual.

### Running without Docker

If you want to execute notebooks without Docker, set up a [virtual
environment](https://docs.python.org/3/tutorial/venv.html) for the
Python version in question (you can infer this from the first line of
the `Dockerfile` in the root of this repo). See the teaching resources [here]( ) on virtual environments.

Next, install dependencies that are normally automatically included by
Docker:

    pip install jupyter jupytext pip-tools

...and install this notebook's dependencies:

    pip install -r requirements.txt

Activate our custom ipython kernel:

    jupyter kernelspec install config/ --user --name="python3"

Finally, run jupyter in the same way it's started in the Docker image:

    PYTHONPATH=$(pwd) jupyter notebook --config=config/jupyter_notebook_config.py


## Development best practices

### Using a specific base image

The `Dockerfile` is a way of telling Docker what environment to start
for you. The first line should be something like:

    FROM ebmdatalab/datalab-jupyter:python3.8.1-d92ad681ed6b16c3c3e0dc5cc21517614bb45d5b

The part before the colon tells docker which "base image" to use (if
you need to see it, the code for our base Docker image can be found
[here](https://github.com/ebmdatalab/datalab-jupyter)).

The part after the colon is a docker `tag`, and specifies which
version of that image to use.

Our tags are of the form `python<version>-<git-commit>`. The
`<version>` is self-explanatory, and the thing you'll usually care
about; `<git-commit>` is the specific commit used to build it. To
ensure your environment is exactly reproducible, you should always use a specific commit.

You can see all the available tags [here](
https://hub.docker.com/repository/docker/ebmdatalab/datalab-jupyter/tags?page=1).

### Installing new packages

Best practice is to ensure all your python dependencies are pinned to
specific versions. To ensure this, while still supporting upgrading
individual packages in a sane way, we use
[pip-tools](https://github.com/jazzband/pip-tools).

The workflow is:

* When you want to install a new package, add it to `requirements.in`
* Run `pip-compile` to generate a `requirements.txt` based on that file
* Run `pip-sync` to ensure your installed packages exactly match those in `requirements.txt`
* Commit both `requirements.in` and `requirements.txt` to your git repo

To *upgrade* a specific package:

    pip-compile --upgrade-package <packagename>

To upgrade everything:

    pip-compile --upgrade

Don't forget to run `pip-sync` after running
any upgrade command.

To execute these within your dockerised environment, start a new Bash
console in Jupyter Lab (from the same menu you would create a new
notebook).

You can then run whatever shell commands you like, by typing them and
hitting Shift + Enter to execute.

### Testing

At a minimum, we expect all notebooks must be runnable from start to
finish, and that the output of code cells matches that saved in the
notebook.  We assert this using the
[nbval](https://github.com/computationalmodelling/nbval) pytest
plugin, which we have set up as a Github Actions workflow (see the
`.github/` folder). Any other pytest-style tests found are also run as
part of this workflow.

### Jupytext and diffing

The Jupyter Lab server is packaged with Jupytext, which automatically
synchronises edits you make in a notebook with a pure-python version
in a subfolder at `notebooks/diffable_python`. This skeleton is also
set up with a `.gitattributes` file which means `ipynb` files are
ignored in Github Pull Requests, making it easier to do code reviews
against changes.

## How to invite people to cite

Once a project is completed, please use the instructions [here](https://guides.github.com/activities/citable-code/) to deposit a copy of your code with Zenodo. You will need a Zenodo free account to do this. This creates a DOI. Once you have this please add this in the readme.

If there is a paper associated with this code, please change the 'how to cite' section to the citation and DOI for the paper. This allows us to build up citation credit.
