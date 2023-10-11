# Supergood Reads

<p align="left">
  <img src="./docs/app.png" width="600">
</p>

[reads.supergood.site](https://reads.supergood.site)

## Table of Contents
- [Table of Contents](#table-of-contents)
- [Welcome](#welcome)
  - [Here's what we got inside](#heres-what-we-got-inside)
  - [It's also got some interesting stuff going on with Vue](#its-also-got-some-interesting-stuff-going-on-with-vue)
- [Installation](#installation)
- [Running Locally](#running-locally)
- [Development Guide](#development-guide)
  - [Extra Installation steps](#extra-installation-steps)
  - [Useful Commands](#useful-commands)
  - [Add new MediaItem types and ReviewStrategies](#add-new-mediaitem-types-and-reviewstrategies)
- [Thanks](#thanks)

## Welcome

Finally, one review site to rule them all! Use any rating schema to review anything.

This is a fun little Django + Vue.js demo project. It's an MVP containing all the features that I'd want to see in a production-ready web application.

### Here's what we got inside

- Modern Python tooling: type-checking with mypy, packaging with Poetry, multi-environment testing with nox, linting with pre-commit
- Modern JavaScript tooling with Vitejs: TypeScript and Vue.js compilation, linting, bundling
- TailwindCSS, HeadlessUI, and PostCSS for styling
- Containerization with Docker
- Python testing suite with Pytest
- Browser testing with jest and puppeteer

### It's also got some interesting stuff going on with Vue

One of the purposes of this project was to experiment with integrating Vue.js with Django templates and forms. The theory was that this could be the ultimate web framework combination -- all the simplicity and development velocity of Django matched with all of the power of a full JavaScript framework.

It did not turn out to be the ultimate web framework of my dreams. There are way too many gotchas and edge cases and complexity for me to really recommend this approach to anyone else (I'll write a more complete postmortem in the future). But the integration does work! And it might serve as inspiration for the next developer who wants to give it a shot.

Some of those fun vue/django integrations are:

- Vue SFC (Single File Componets) rendered as django templates
- Autocomplete dropdown form fields
- Support for Generic Model Relations in Django ModelForms
- Conditional form sections
- And of course, a datepicker

## Installation
1. Install Python
   - I recommend using [pyenv](https://github.com/pyenv/pyenv) to manage installations of python. Pyenv allows you to install and use multiple versions of python on the same computer.
   - After pyenv is installed, run `pyenv local` inside this directory to install the version of python3 specified by the `.python-version` file.
   - If you really don't want to use pyenv, any version of python 3.x should work fine.
2. Install Poetry
   - Poetry is the python dependency manager that this project uses. It can be installed [here](https://python-poetry.org/).
3. Install python packages with Poetry.
   - `make install`
4. Create a .env file.
   - `make .env`
5. Install Nodejs
   - I recommend using [nvm](https://github.com/nvm-sh/nvm) to manage installations of node. nvm (node version manager) allows you to install and use multiple versions of nodejs on the same computer.
   - After nvm is installed, run `nvm use` inside this directory to install the version of nodejs specified by the `.nvmrc` file.
7. Install Nodejs packages
   - `npm install`
8. Run initial data migrations
   - `poetry run python manage.py migrate`
9. Install seed data
   - `poetry run python manage.py supergood_reads_load_test_data`

## Running Locally
Now that your dependencies have been installed, you're ready to run the app.

1. Start the django server.
   - `make up`
2. In a separate terminal window, start the nodejs server.
   - `make vite`
   - Note: both servers must be running at the same time for the app to function.
3. Navigate to `http://localhost:8000/app/review` to try out the form.
4. The app is not yet complete. The only thing that is finished is the review form itself -- there isn't yet a page that renders all of the reviews you've inputted. But you can inspect the raw data:
   - `make shell`
   - Once inside the shell, you can look at your raw django data. Example: `Review.objects.all()`

## Development Guide

### Extra Installation steps

If you want to make contributions to the project, you need to run one additional installation step.

1. Install nox
   - `pip install --upgrade nox`
   - [Nox](https://nox.thea.codes/en/stable/index.html) is used to manage the execution of this test suite. Nox is useful for testing reuseable external libraries that require testing across multiple versions of python or django.
2. Install pre-commit
   - https://pre-commit.com/#install to install the pre-commit program itself.
   - `pre-commit install` to install the pre-commit hooks for this particular project.

### Useful Commands

1. Run the python test suite.
   - `make pytest`
2. Run the javascript test suite.
   - `make jest`
3. Run linting for all files of the project.
   - `make lint`
4. Check for vulnerabilities in external packages.
   - `make safety`
5. Check for type errors in python code.
   - `make mypy`

You can find more commands in the Makefile.

[TODO: Add docs about running on docker]

### Add new MediaItem types and ReviewStrategies

SupergoodReads is fully extensible and allows developers to seemlessly add new review strategies and media types by adding their own custom [SupergoodReadsConfig](./supergood_reads/utils/engine.py).

[TODO: finish this section.]

## Thanks

Test data was provided by these datasets:
- ["7k books" from Kaggle](https://www.kaggle.com/datasets/dylanjcastillo/7k-books-with-metadata)
- ["IMDB Top 1000 movies" from Kaggle](https://www.kaggle.com/datasets/arthurchongg/imdb-top-1000-movies)
- [BFI 2022 Greatest Films of All Time](https://www.bfi.org.uk/sight-and-sound/greatest-films-all-time)
- [BFI 2022 Greatest Films of All Time (Director's Poll)](https://www.bfi.org.uk/sight-and-sound/directors-100-greatest-films-all-time)
