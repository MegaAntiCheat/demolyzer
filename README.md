# Demolyzer

Demolyzer is a statistics and data library for analyzing TF2 demo files. The main goal is to transform demo files into csv files and provide more downstream transformations to make it easier to analyze and plot data. After following the installation instructions below, basic usage is as follows:

```py
from demolyzer.stats import DemoAnalyzer

my_demoanalyzer = DemoAnalyzer("path_to_my_demo.dem")

# see methods in `DemoAnalyzer` for more information..

my_demoanalyzer.players
my_demoanalyzer.num_players

death_stats = my_demoanalyzer.death_stats()
print(death_stats)
```

## Prerequisites

Python 3.10 or higher is required.

## Installation

First, clone the repository and cd into it:

```sh
git clone https://github.com/MegaAntiCheat/demolyzer.git
cd demolyzer
```

Next, create a virtual environment:

```sh
python3 -m venv venv
```

Then activate it

On Unix and MacOS:
```sh
source venv/bin/activate
```

On Windows:
```sh
.\venv\Scripts\activate
```

## Development
For development, additional dependencies are needed:
```sh
pip install -e ".[dev]"
```

## Formatting
```sh
isort demolyzer tests
black demolyzer tests
```
