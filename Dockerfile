FROM jupyter/scipy-notebook:ubuntu-20.04

USER root
RUN apt-get update -y
RUN apt-get install -y netbase
RUN apt-get install -y graphviz
RUN apt-get install -y libmagic1
RUN apt-get clean
RUN rm -rf /var/lib/apt/lists/*

USER ${NB_USER}
RUN conda install --quiet --yes git==2.35.0
RUN conda install --quiet --yes git-annex==8.20210903
RUN conda clean -i -t -y

# install the notebook package etc.
RUN pip install --no-cache --upgrade pip
RUN pip install --no-cache notebook
RUN pip install --no-cache jupyter_contrib_nbextensions
RUN pip install --no-cache git+https://github.com/NII-cloud-operation/Jupyter-LC_run_through
RUN pip install --no-cache git+https://github.com/NII-DG/dg_Jupyter-multi_outputs.git@master
RUN pip install --no-cache datalad==0.17.6
RUN pip install --no-cache lxml==4.7.1
RUN pip install --no-cache blockdiag==3.0.0
RUN pip install --no-cache -U nbformat==5.2.0
RUN pip install --no-cache black==21.12b0
RUN pip install --no-cache snakemake
RUN pip install --no-cache boto3
RUN pip install --no-cache chardet==4.0.0
RUN pip install --no-cache panel==1.3.0
RUN pip install --no-cache python-magic==0.4.27
RUN pip install --no-cache natsort==8.3.1
RUN pip install --no-cache git+https://github.com/NII-DG/nii-dg.git@230419_8c684da
RUN pip install --no-cache git+https://github.com/NII-DG/dg-packager.git@master

RUN jupyter contrib nbextension install --user
RUN jupyter nbextensions_configurator enable --user
RUN jupyter run-through quick-setup --user
RUN jupyter nbextension install --py lc_multi_outputs --user
RUN jupyter nbextension enable --py lc_multi_outputs --user

# upgrade nbclassic ( after nbextension installed )
RUN pip install --no-cache nbclassic==0.4.8

# install Japanese-font (for blockdiag)
ARG font_deb=fonts-ipafont-gothic_00303-18ubuntu1_all.deb
RUN mkdir ${HOME}/.fonts
RUN wget -P ${HOME}/.fonts http://archive.ubuntu.com/ubuntu/pool/universe/f/fonts-ipafont/${font_deb}
RUN dpkg-deb -x ${HOME}/.fonts/${font_deb} ~/.fonts
RUN cp ~/.fonts/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf ~/.fonts/ipag.ttf
RUN rm ${HOME}/.fonts/${font_deb}
RUN rm -rf ${HOME}/.fonts/etc ${HOME}/.fonts/usr
RUN rm .wget-hsts


ARG NB_USER=jovyan
ARG NB_UID=1000

RUN rm -rf ${HOME}/work

# prepare datalad procedure dir
RUN mkdir -p ${HOME}/.config/datalad/procedures

WORKDIR ${HOME}
COPY . ${HOME}

USER root
RUN chown -R ${NB_UID} ${HOME}


##### User Custom Area [Start] ######
# Dockerfileを編集する場合は、「User Custom Area」内に記述してください。
# それ以外のエリアでの記述、また変数名：NB_USERの値は書き換えないでください。リサーチフロー機能が正常に働かなくなる可能性があります。
# root権限で実行したい場合は、"USER root"を、一般ユーザ権限で実行したい場合は、 "USER ${NB_USER}"を実行したいコマンド前に記述してください。




###### User Custom Area [End] #######

USER ${NB_USER}
# Specify the default command to run
CMD ["jupyter", "notebook", "--ip", "0.0.0.0"]
