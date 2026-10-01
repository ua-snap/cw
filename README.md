# Community Winds visualization for Alaska communities

## Data preprocessing & local development

First, clone the repo then 

```
pipenv install
```

If you need to re-process the data, [obtain station data](https://mesonet.agron.iastate.edu/request/download.phtml) and place it in `data/stations` (create this directory if necessary), then run:

```
pipenv run python preprocess.py # takes a long time, 15+ minutes
```

For local development,

```
export FLASK_APP=application.py
export FLASK_DEBUG=1
export DASH_REQUESTS_PATHNAME_PREFIX='/'
export CARTO_API_KEY='<your CARTO basemaps API key>'
pipenv run flask run
```

The project is run through Flask and will be available at [http://localhost:5000](http://localhost:5000). The map's basemap requires a valid [CARTO basemaps API key](https://carto.com/basemaps/apikey) set via the `CARTO_API_KEY` environment variable.

## Deploying to AWS Elastic Beanstalk:

Apps run via WSGI containers on AWS.

Before deploying, make sure and run `pipenv run pip freeze > requirements.txt` to lock current versions of everything.

```
eb init
eb deploy
```

It'll be necessary to set the `DASH_REQUESTS_PATHNAME_PREFIX` as appropriate on the EB instance.

Also set `CARTO_API_KEY` as an environment variable on the EB instance, or the map's basemap will fail to load.