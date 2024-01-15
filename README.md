# Basic API
An API I made using [Flask](https://flask.palletsprojects.com/) and Flask extensions.<br>
This isn't meant to show off my skills, it's just a simple API I made for fun in my free time.

## Information
This is protected against anything I could think of like:
- Timing attacks
- Brute force attacks
- SQL injection
- XSS
- CSRF
- Session hijacking
- More...

## Environment Variables
Place these in a `.env` file in the root directory of the project.
| Variable | Description |
| ---: | :--- |
| `FLASK_APP` | The name of the Flask app. Default: `app.py` |
| `FLASK_ENV` | The environment of the Flask app. Default: `development` |
| `FLASK_DEBUG` | Whether or not to enable debug mode. Default: `0` |
| `FLASK_RUN_PORT` | The port to run the Flask app on. Default: `5000` |
| `PEPPER` | The pepper to use for hashing passwords. Default: `None` |
| `SECRET_KEY` | The secret key to use for the Flask app. Default: `None` |

## Usage
### 1. Creating the Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Installing the Dependencies
```bash
pip install -r requirements.txt
```

### 3. Running the Flask App (to create the database)
```bash
python3 src/run.py
```

### 4. Running the Flask App (to run the app)
```bash
flask run
```

