import base64
import os
import tempfile
import traceback

import numpy as np
import zmq
import logging
from keras.preprocessing import image as im
from keras.applications.inception_v3 import InceptionV3, preprocess_input

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')


def get_inception_predictions(image, model):
    img_file = tempfile.NamedTemporaryFile(delete=False)
    img_file.write(image)
    img_file.close()

    img = im.load_img(img_file.name, target_size=(299, 299))
    img = im.img_to_array(img)
    img = np.expand_dims(img, axis=0)
    img = preprocess_input(img)

    logging.info("Get predictions")
    result = model.predict(img)
    os.unlink(img_file.name)
    return result


def main():
    logging.info("Load inception model")
    model = InceptionV3()
    logging.info("Complete loading")

    context = zmq.Context()
    socket = context.socket(zmq.REP)
    socket.bind("tcp://*:1350")

    while True:
        img = socket.recv_json()["img_b64"]
        res, = get_inception_predictions(base64.b64decode(img), model)
        logging.info("Send result")
        socket.send_json({"vector": map(float, res.tolist())})


if __name__ == '__main__':
    main()
