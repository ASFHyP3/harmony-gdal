FROM mambaorg/micromamba:latest

WORKDIR /home/mambauser

COPY --chown=$MAMBA_USER:$MAMBA_USER . /harmony-gdal-adapter/

RUN micromamba install -y -n base -f /harmony-gdal-adapter/environment.yml && \
    micromamba install -y -n base git && \
    micromamba clean --all --yes

ARG MAMBA_DOCKERFILE_ACTIVATE=1
RUN python -m pip install -e /harmony-gdal-adapter/

ENTRYPOINT ["/usr/local/bin/_entrypoint.sh", "python", "-m", "harmony_gdal_adapter.harmony_service"]
