FROM ubuntu
MAINTAINER gennady Shtekh <sht3ch@skydns.ru>


RUN apt-get update && \
    apt-get install -yq --no-install-recommends python python-pip python-setuptools ssh nano git make cmake build-essential libboost-all-dev python-dev libblas-dev liblapack-dev libatlas-base-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && \
    pip install --no-cache-dir --no-cache pandas numpy nltk pymorphy2 zmq tqdm protobuf==3.0.0

RUN git clone --branch v0.8.2 --depth=1 https://github.com/bigartm/bigartm.git &&\
	cd bigartm && \
	mkdir build && \
	cd build && \
	cmake .. && \
	make -j2 && \
	make install

RUN cd /bigartm/3rdparty/protobuf-3.0.0/python && \
	python setup.py install
RUN cd bigartm/python && \
	python setup.py install
ENV ARTM_SHARED_LIBRARY=/usr/local/lib/libartm.so

RUN mkdir /models
ADD big_model.artm.mtx /models
RUN mkdir /resourses
ADD insception-classes.tsv /resourses

RUN mkdir /code
ADD model_application.py /code
ADD utils.py /code

ARG zmq_port=1349
ARG loglevel=20
ARG logfile=artm.log

ENV LOGLEVEL=${loglevel}
ENV LOGFILE=${logfile}
ENV ZMQPORT=${zmq_port}

RUN mkdir /data
WORKDIR /code

EXPOSE ${zmq_port}

ENTRYPOINT python model_application.py
