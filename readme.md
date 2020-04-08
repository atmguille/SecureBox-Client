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

## Configuration
To interact with the server, you will need a token. Once you have the token, the script will ask you to write it through stdin and will then initialize the `bundle.ini`. If you want to use another token, just remove this file and the script will ask it again. TODO: comentar algo de create_id o...?

Our configuration is the following: ID = 383112, TOKEN = E83A7d29D0aCFcB6. The file `bundle.ini` contains this configuration, along with the private key.

To upload the requested file (prueba2.txt), we have run the following command:
```bash
python3 main.py --upload prueba2.txt --dest_id e281430
```
That returns the file Id, which is dA4Fc1f6 TODO: actualizar si cambiamos cualquier cosa
To download it, you must run:
```bash
python3 main.py --download dA4Fc1f6 --source_id 383112
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

Downloaded files will be stored in `received` directory.