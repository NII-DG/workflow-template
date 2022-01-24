# FROM alpine:${ALPINE_VERSION}
FROM python:3.7.12-alpine3.14

# install bash
RUN apk add --no-cache bash

# install hg-evolve (Mercurial extensions)
# RUN pip3 install hg-evolve --user --no-cache-dir

# pip upgrade
RUN pip install -U pip

# prepare jupyter
RUN pip install --no-cache-dir notebook
RUN pip install --no-cache-dir jupyterhub

ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV NB_UID ${NB_UID}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}

# Make sure the contents of our repo are in ${HOME}
COPY . ${HOME}
USER root
RUN chown -R ${NB_UID} ${HOME}
USER ${NB_USER}

# install datalad, papermill & dependencies
RUN pip install datalad==0.15.4
RUN pip install papermill==2.3.3
RUN pip install black==21.12b0

# install repo2docker
# COPY --from=0 /tmp/wheelhouse /tmp/wheelhouse
# RUN pip3 install --no-cache-dir /tmp/wheelhouse/*.whl \
#  && pip3 list

# add git-credential helper
COPY ./docker/git-credential-env /usr/local/bin/git-credential-env
RUN git config --system credential.helper env

# add entrypoint
COPY ./docker/entrypoint /usr/local/bin/entrypoint
RUN chmod +x /usr/local/bin/entrypoint
ENTRYPOINT ["/usr/local/bin/entrypoint"]

# Used for testing purpose in ports.py
EXPOSE 52000
