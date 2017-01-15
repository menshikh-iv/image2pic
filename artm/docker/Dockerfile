FROM ubuntu
MAINTAINER gennady Shtekh <sht3ch@skydns.ru>


RUN apt-get update && \
    apt-get install -yq --no-install-recommends python python-pip python-setuptools ssh nano git make cmake build-essential libboost-all-dev python-dev libblas-dev liblapack-dev libatlas-base-dev && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN git clone --branch=stable https://github.com/bigartm/bigartm.git &&\
	cd bigartm && git checkout v0.8.1 &&\
	mkdir build && \
	cd build && \
	cmake .. && \
	make && \
	make install

RUN cd bigartm/3rdparty/protobuf/python && \
	python setup.py install
RUN cd bigartm/python && \
	python setup.py install
ENV ARTM_SHARED_LIBRARY=/bigartm/build/src/artm/libartm.so

RUN pip install --upgrade pip && pip install --no-cache-dir --no-cache pandas numpy nltk pymorphy2 zmq

RUN mkdir /data
ADD dict.filtered /data
ADD big_model.artm.mtx /data
ADD insception-classes.tsv /data

RUN mkdir /code
ADD model_application.py /code
ADD utils.py /code

WORKDIR /code

EXPOSE 1349

ENTRYPOINT python model_application.py
