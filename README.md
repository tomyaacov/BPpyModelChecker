# BPpyModelChecker

<b>Note: the project was implemented and tested on Python 3.7.16</b>

## Installation and Usage

1. Clone the project :
    ```shell
    git clone https://github.com/tomyaacov/BPpyModelChecker.git
    ```

2. Set an anvironment to run the code. There are 2 options:
    1. Using docker:
        ```shell
            docker pull tomyaacov/bppy-pynusmv:latest
        ```
    2. Using a virtual environment:
        ```shell
            cd BPpyModelChecker
            python -m venv env 
            source env/bin/activate
            pip install --upgrade pip
            pip install -r requirements.txt
        ```
3. Run the hot cold example liveness verification:
    ```shell
    python bp_model_checker.py
    ```