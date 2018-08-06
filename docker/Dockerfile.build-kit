FROM univa/tortuga-builder

COPY entrypoint.build-kit /entrypoint.sh
RUN chmod 0755 /entrypoint.sh

ADD tortuga-*/python-tortuga/tortuga_core-*.whl /

RUN . /opt/rh/rh-python36/enable && \
    bash -c 'pip install wheel awscli /tortuga_core-*.whl'

WORKDIR /kit-src

CMD [ "bash", "-c", "build-kit clean && build-kit" ]
