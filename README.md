# Cómo construir una aplicación web completa con Python y SQLite3

Ejecutamos por este orden:

> python3.8 -m venv venv

👉 Set Up for Unix

> $ virtualenv venv
> $ source venv/bin/activate
> $ pip3 install -r requirements.txt

🛠️ Set Up Flask Environment

> $ export FLASK_APP=run.py
> $ export FLASK_ENV=development
> $ export FLASK_DEBUG=true

👉 Set Up for Windows

Install modules via VENV (windows)

> $ virtualenv venv
> $ .\venv\Scripts\activate
> $ pip3 install -r requirements.txt

🛠️ Set Up Flask Environment

> $ # CMD
> $ set FLASK_APP=run.py
> $ set FLASK_ENV=development
> $
> $ # Powershell
> $ $env:FLASK_APP = ".\run.py"
> $ $env:FLASK_ENV = "Development"  --dEPRECATED
> $ $env:FLASK_DEBUG = "true"

🛠️ Start the app

> $ flask run

At this point, the app runs at <http://127.0.0.1:5000/>.

## ✨ Start the app in Docker

> **Step 1** - Download the code from the GH repository (using `GIT`)

```bash
# Get the code
git clone https://sourcerepository-tc.shared-nonprod.cloud.si.orange.es/servconfigmanagement/dashboardsonar-application-python.git
cd dashboardsonar-application-python
```

> **Step 2** - Edit `.env` and set `DEBUG=True`. This will activate the `SQLite` persistance.

```bash
DEBUG=True
```

> **Step 3** - Start the APP in `Docker`

```bash
docker-compose up --build 
```

Visit `http://localhost:5085` in your browser. The app should be up & running.

(venv) python -m pytest --setup-show --cov=apps --cov-report=html

ultimas modificaciones

lanzar test_measures.ipynb para extraer los datos del proyecto de sonar.
Esos datos se transforman y se creand dos nuevos ficheros; historico.csv y metricas.csv

Posteriormente se lanza init_db.py para recrear la bbdd y cargar los csv (historico, metrica y proveedores)

## Install pre-commit

$ pre-commit --version
$ pre-commit install
$ pre-commit run --all-files
$ pre-commit uninstall

## Connfiguración

mkdir datos

configurar .env

DEBUG=True

FLASK_APP=run.py
FLASK_ENV=development
FLASK_DEBUG=False

ASSETS_ROOT=/static/assets

DATABASE = "db.sqlite3"
DATOS_CSV = "sonar_salida_measure_etl_tc.csv"
HISTORICO_CSV = "sonar_salida_historico_etl_tc.csv"

## How to Apply Migrations Using Flask-Migrate

Before we can seed our database, we need to set up database migrations using Flask-Migrate. This tool helps us manage database changes, such as creating tables and altering schemas, systematically.

Initialize the migrations folder by running the following command in your project directory:

> flask db init

This command creates a migrations directory in our project, which will store migration scripts.

Generate a migration script that creates the necessary database tables based on your models:

> flask db migrate -m "Initial migration"

This command scans your models and generates a new migration script in the migrations folder.

Apply the migration to create the tables in your database:

> flask db upgrade

This command executes the migration script, creating the tables defined by your models in the database. Post this step, you will see an instance/db.sqlite file created.

## test

> python -m pytest --setup-show
> python -m pytest --setup-show --cov=apps --cov-report=html
