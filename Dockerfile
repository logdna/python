FROM condaforge/miniforge3:4.12.0-0

RUN conda install -y gcc pip poetry=1.1.7 git
RUN mkdir /workdir && chmod 777 /workdir
RUN git config --global --add safe.directory /workdir
WORKDIR /workdir

