ARG BUILD_FROM
FROM $BUILD_FROM

RUN \
  apk add --no-cache \
    python3 py3-pip
RUN \
    pip install -I git+https://github.com/NickWaterton/samsung-tv-ws-api.git
# Copy data for add-on
#COPY run.sh /
#COPY art.py /


#RUN chmod a+x /run.sh

#CMD [ "/run.sh" ]
