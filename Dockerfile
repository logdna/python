FROM condaforge/miniforge3:4.12.0-0

RUN conda install -y gcc pip poetry=1.1.7
RUN mkdir /workdir




