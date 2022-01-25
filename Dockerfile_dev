FROM python:3.7-slim-buster

# install debian package (datalad-cli etc.)
RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get install -y datalad \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# install the notebook package etc.
RUN pip install --no-cache --upgrade pip \
    && pip install --no-cache notebook jupyterlab \
    && pip install --no-cache datalad==0.15.4 \
    && pip install --no-cache papermill==2.3.3 \
    && pip install --no-cache black==21.12b0

# create user with a home directory
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

WORKDIR ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
USER ${NB_USER}
