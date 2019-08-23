# Community Winds visualization for Alaska communities

## Data preprocessing & local development

After cloning this template, obtain station data and place it in `data/stations` (create this directory if necessary), then run:

```
pipenv install
pipenv run python preprocess.py # takes a long time, 15+ minutes
export FLASK_APP=application.py
export FLASK_DEBUG=1
export REQUESTS_PATHNAME_PREFIX='/'
pipenv run flask run
```

The project is run through Flask and will be available at [http://localhost:5000](http://localhost:5000).

## Deploying to AWS Elastic Beanstalk:

Apps run via WSGI containers on AWS.

Before deploying, make sure and run `pipenv run pip freeze > requirements.txt` to lock current versions of everything.

```
eb init
eb deploy
```

It'll be necessary to set the `REQUESTS_PATHNAME_PREFIX`, `GTAG_ID` and `MAPBOX_ACCESS_TOKEN` as appropriate on the EB instance.