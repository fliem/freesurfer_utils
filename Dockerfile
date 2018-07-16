FROM bids/freesurfer:v6.0.0-5

RUN echo 'export PATH=/usr/local/anaconda:$PATH' > /etc/profile.d/conda.sh && \
    wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-4.5.4-Linux-x86_64.sh -O anaconda.sh && \
    /bin/bash anaconda.sh -b -p /usr/local/anaconda && \
    rm anaconda.sh

ENV PATH=/usr/local/anaconda/bin:$PATH

RUN conda install -y pandas
RUN conda install -y scipy
RUN pip install pybids
RUN pip install nibabel
RUN pip install patsy


COPY . /code/
RUN chmod +x /code/run_freesurfer_utils.py

COPY version /version

ENTRYPOINT ["/code/run_freesurfer_utils.py"]
