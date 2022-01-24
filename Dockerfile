FROM python:3.7-slim-buster
# install the notebook package
RUN pip install --no-cache --upgrade pip && \
    pip install --no-cache notebook jupyterlab

RUN apt-get update -y \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get install -y datalad \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# # 必要なdebianライブラリのインストール
# RUN apt-get install -y gettext \
#     libcurl4-gnutls-dev \
#     libexpat1-dev \
#     libghc-zlib-dev \
#     libssl-dev \
#     make \
#     wget

# # gitアップグレード（datalad対応のため）
# RUN wget https://github.com/git/git/archive/v2.33.1.tar.gz \
#     && tar -xzf v2.33.1.tar.gz \
#     && cd git-* \
#     && make prefix=/usr/local all \
#     && make prefix=/usr/local instal

# create user with a home directory
ARG NB_USER=jovyan
ARG NB_UID=1000
ENV USER ${NB_USER}
ENV HOME /home/${NB_USER}

RUN adduser --disabled-password \
    --gecos "Default user" \
    --uid ${NB_UID} \
    ${NB_USER}
WORKDIR ${HOME}
USER ${USER}


# install datalad, papermill & dependencies
RUN pip install datalad==0.15.4
RUN pip install papermill==2.3.3
RUN pip install black==21.12b0
