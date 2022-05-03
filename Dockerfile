FROM condaforge/miniforge3:4.12.0-0

RUN conda install -y pip poetry=1.1.7 pytest
RUN pip install tap.py


