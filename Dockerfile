FROM bids/freesurfer:v6.0.0-5

RUN wget -qO- https://surfer.nmr.mgh.harvard.edu/pub/dist/freesurfer/6.0.0/freesurfer-Linux-centos6_x86_64-stable-pub-v6.0.0.tar.gz | tar zxv -C /opt \
    --exclude='freesurfer/*' \
    --include='freesurfer/subjects/fsaverage4'

COPY . /code/
RUN chmod +x /code/run_freesurfer_utils.py

COPY version /version

ENTRYPOINT ["/code/run_freesurfer_utils.py"]
