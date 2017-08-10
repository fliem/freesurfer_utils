FROM bids/freesurfer:v6.0.0-5

COPY . /code/
RUN chmod +x /code/run_freesurfer_utils.py

COPY version /version

ENTRYPOINT ["/code/run_freesurfer_utils.py"]
