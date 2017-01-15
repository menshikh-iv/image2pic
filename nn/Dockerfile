FROM debian
MAINTAINER Ivan Menshikh <menshikh.iv@gmail.com>

RUN apt-get update && \
    apt-get install -yq --no-install-recommends python python-pip python-setuptools nano make cmake build-essential \
                                                libboost-all-dev python-dev libblas-dev liblapack-dev \
                                                libatlas-base-dev python-pip

RUN pip install --upgrade pip
RUN pip install numpy scipy zmq h5py tensorflow keras pillow

COPY .keras/ /root/.keras
COPY nn_app.py .

ENTRYPOINT python nn_app.py
