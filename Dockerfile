FROM python:3.10

WORKDIR /usr/src/app

# install deps
# --build-arg 'pip-args=--dev'
ARG pip_args="" 
RUN pip install pipenv
RUN mkdir -p .venv
ADD Pipfile .
ADD Pipfile.lock .
RUN pipenv install $pip_args 

# copy main files
# make sure these arent't cached from the base build in case of delete/renaming in app image
RUN rm -rf bin app tests config
COPY ./bin bin
COPY ./app app
COPY ./tests tests
COPY ./config config
COPY pytest.ini .

ENV PYTHONUNBUFFERED=1 
ENV PYTHONPATH "/usr/src/app:/usr/src/app/.venv/lib/python3.10/site-packages"
ENV PATH "/usr/src/app/.venv/bin:$PATH:bin"
CMD [ "ddtrace-run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--forwarded-allow-ips", "*", "--proxy-headers", "--no-date-header", "--no-server-header", "--no-access-log" ]
