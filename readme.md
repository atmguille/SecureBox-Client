# SecureBox Client

## Installation
Using a virtual environment is highly recommended. To do so:
- Install `virtualenv` if you do not have it already by running:
  ```bash
  sudo pip3 install virtualenv
  ```
- Create a virtual environment in the desired location and with the desired name (venv in the example):
  ```bash
  virtualenv venv
  ```
  To specify Python3 as the interpreter (required for this project), create the environment running:
  ```bash
  virtualenv --python=python3 venv
  ```
- Activate your virtual environment:
  ```bash
  source venv/bin/activate
  ```
- Deactivate it if wanted:
  ```bash
  deactivate
  ```
 
## Requirements
All the required libraries are indicated in `requirements.txt`. It is recommended to install them in the virtual environment. To do so, after activating it, just run:
```bash
pip install -r requirements.txt
```

## Execution
To run the program, you will need to use Python3 as the interpreter (at least version 3.6). If you have already set it in the virtual environment, just run:
```bash
python main.py
```
If not, you must run it as follows:
```bash
python3 main.py
```
To display the program usage, run it with `-h` or `--help`.