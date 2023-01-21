from setuptools import setup, find_packages

version = "0.1.0"

install_requires = [
    'Django>=3.2',
]

extras_require = {
    "testing": [
        "pre-commit>=2.20.0",
        "black>=22.10.0",
        # leave isort pinned - it tends to change rules between patch releases
        "isort==5.8.0", 
        "flake8>=5.0.4",
        "mypy>=0.991",
        "pytest>=7.2.0",
        "debugpy>=1.6.4",
    ],
}

description = "Create a flex review schema."
long_description = "Create a flex review schema."

setup(
    name='django-flex-reviews',
    version=version, 
    description=description,
    author="Nick Ivons",
    url="https://github.com/niicck/django_flex_reviews",
    packages=find_packages(),
    include_package_data=True,
    license="MIT",
    long_description=long_description,
    classifiers=[
        "Development Status :: 1 - Planning",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        'Natural Language :: English',
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Django",
        "Framework :: Django :: 3.2",
        "Framework :: Django :: 4.0",
        "Framework :: Django :: 4.1",
        "Framework :: Wagtail",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: News/Diary",
    ],
    python_requires=">=3.7",
    install_requires=find_packages(exclude=['tests', 'tests.*']),
    extras_require=extras_require,
)
