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
To interact with the server, you will need a token. The first time the client is run, the token, a username and an email will be requested. Then, a private key will be generated and you will be registered into the server. You ID, token and private key will be stored in a file called bundle. You will be asked for a password in order to cipher this file. Note that if you don't want to bother typing it every time you use the client you can leave it blank. If you ever want to change the token (because it gets outdated for instance) you can just delete the `bundle.ini` (or `bundle.crypt`) file and this whole process will start over. 

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