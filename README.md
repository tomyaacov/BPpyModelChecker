# BPpyModelChecker

<b>Note: the project was implemented and tested on Python 3.7.16</b>

## Installation and Usage

1. Clone the project :

```shell
git clone https://github.com/tomyaacov/BPpyModelChecker.git
```

2. Create a virtual environment and activate it:

```shell
cd BPpyModelChecker
python -m venv env 
source env/bin/activate
```

3. Update pip and install all dependencies:

```shell
pip install --upgrade pip
pip install -r requirements.txt
```

4. Run the hot cold example liveness verfiication:
 
```shell
python bp_model_checker.py
```