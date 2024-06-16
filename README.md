# Bitespeed Backend Task: Identity Reconciliation

This API helps us to Identtify the Person using multiple Email's and Phone Numbers, sorry to upload whole Git Repository at once.

## Setup & Installation

First, ensure you have Python & Docket is installed on your system.

* Initializing Virtual Environment &  Cloning Github Repository:

```bash
git clone 'https://github.com/devalhere2/identify-api.git'
cd identify-api
python3 -m venv venv
source venv/bin/activate
 ```
* Installing Libraries
```bash
pip install Fastapi[all]
pip install requests
pip install psycopg2-binary
 ```
* Docker 
```bash
docker run --name demoapi -e POSTGRES_PASSWORD=1234 -p 5432:5432 -d postgres:alpine
 ```

* Running Api
```bash
uvicorn main:app --reload
 ```
* Run Test.py , i have added some sample data and generated response.json file for it
* Use http://159.65.157.100:8000/docs for trying out the API before 25 June
