# Demolyzer

Demolyzer is a statistics and data library for analyzing TF2 demo files.

## Prerequisites

Python 3.10 or higher is required.

## Installation

First, clone the repository and cd into it:

```sh
git clone https://github.com/jayceslesar/demolyzer.git
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