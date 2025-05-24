# Hot Wheels Collection

A Flask app to manage your Hot Wheels collection.

## Setup

```bash
git clone <YOUR_REPO_URL>
cd <YOUR_REPO_NAME>
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration

- Set a production secret key:
  ```bash
  export SECRET_KEY="your_production_secret"
  ```

### Development

```bash
export FLASK_APP=app.py
export FLASK_ENV=development
flask run
```

### Production

```bash
gunicorn --workers 3 --bind 127.0.0.1:8000 app:app
```

## Deployment

Use the provided `install_hotwheels.sh` script for a production-ready setup on a Raspberry Pi.
