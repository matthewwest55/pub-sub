ARG AZLINUX_BASE_VERSION=master

# Base stage with python-build-base
FROM quay.io/cdis/python-nginx-al:${AZLINUX_BASE_VERSION} AS base

RUN yum -y install nano

ENV appname=pub_sub

COPY --chown=gen3:gen3 /src/${appname} /${appname}

WORKDIR /${appname}

# Builder stage
FROM base AS builder

USER gen3

COPY poetry.lock pyproject.toml /${appname}/

# RUN python3 -m venv /env && . /env/bin/activate &&
RUN poetry install -vv --no-interaction --without dev

COPY --chown=gen3:gen3 . /${appname}
#COPY --chown=gen3:gen3 ./deployment/wsgi/wsgi.py /${appname}/wsgi.py

RUN poetry install -vv --no-interaction --without dev

ENV PATH="$(poetry env info --path)/bin:$PATH"

# Final stage
FROM base

COPY --from=builder /${appname} /${appname}

COPY --chown=gen3:gen3 /src/${appname} /${appname}

# RUN pip install fastapi uvicorn

#COPY poetry.lock pyproject.toml /${appname}/

#RUN poetry install -vv --no-interaction --without dev

#COPY --chown=gen3:gen3 . /${appname}
# COPY --chown=gen3:gen3 ./deployment/wsgi/wsgi.py /${appname}/wsgi.py

#RUN poetry install -vv --no-interaction --without dev

#ENV  PATH="$(poetry env info --path)/bin:$PATH"

CMD ["poetry", "run", "uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
