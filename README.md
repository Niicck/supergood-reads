# Django Flex Reviews

🚧 Under construction 🚧

This is a django app that allows users to write film reviews. Unlike other review sites, flex-reviews allows you to customize the rating schema that you use to rate movies. You can use rating strategies based on popular rating sites (like goodreads or letterboxd) as well as create your own custom schemas.

From a technical standalone, this app is also a demonstration of how to create modern UX experiences with django forms - using the best parts of django server-side rendering while also incorporating modern client-side interactivity and development tooling.

We're going to cover some of the most common challenges that developers face when building advanced django forms. These include:

- autocomplete dropdown fields
- support for GenericForeignKeys
- conditional form sections
- custom field widgets
- TailwindCSS for styling
- modern js tooling: typescript, linting, bundling with Vitejs
- an inevitable datepicker


Table of Contents:

- [Installation](#installation)
- [Development Guide](#development-guide)


## Installation

To your `INSTALLED_APPS` add:

- `django.contrib.contenttypes`
- `django_flex_reviews`

## Development Guide

1. Install nox: `pip install --user --upgrade nox`

(To be continued)
