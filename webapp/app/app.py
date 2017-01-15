import base64
import json
import logging
import random
import numpy as np
from scipy.spatial.distance import cdist
import zmq
from flask import Flask, render_template, request, send_from_directory


TIMEOUT_MS = 10000
ARTM_PORT = 1349
NN_PORT = 1350

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')

app = Flask(__name__)

logging.info("Load topic vectors to memory")

with open("dataset/topic_vectors.json") as infile:
    dataset = map(json.loads, infile)

index_matr = np.array([_["topics"] for _ in dataset])


@app.route('/processing', methods=["POST"])
def processing():
    logging.info(request.form)

    txt = request.form["search_text"]
    img = request.files.get("photo_img", None)
    preds = []

    context = zmq.Context()

    if img:
        logging.info("Image exists, go to inception")
        img = img.read()

        nn_socket = context.socket(zmq.REQ)
        nn_socket.connect('tcp://image2pic-inception-v3:{}'.format(NN_PORT))
        nn_socket.setsockopt(zmq.LINGER, TIMEOUT_MS)
        nn_poller = zmq.Poller()
        nn_poller.register(nn_socket, zmq.POLLIN)

        logging.info("send to nn")
        nn_socket.send_json({"img_b64": base64.b64encode(img)})

        if nn_poller.poll(TIMEOUT_MS):
            logging.info("nn poll ok, recv")
            preds = nn_socket.recv_json()["vector"]
        else:
            logging.info("fail polling")
            return render_template("error.html", error_text="neural network (inception)")

    to_artm = {"id": "https://{}".format(random.randint(10 ** 5, 10 ** 10))}

    if txt.strip():
        to_artm["raw_text"] = txt

    if preds:
        to_artm["classes"] = preds

    logging.info("Go to artm with data")

    artm_socket = context.socket(zmq.REQ)
    artm_socket.connect('tcp://image2pic-artm-service:{}'.format(ARTM_PORT))
    artm_socket.setsockopt(zmq.LINGER, TIMEOUT_MS)
    artm_poller = zmq.Poller()
    artm_poller.register(artm_socket, zmq.POLLIN)

    artm_socket.send_json({"command": "transform",
                           "data": [to_artm]})

    if artm_poller.poll(TIMEOUT_MS):
        logging.info("artm poll ok, recv")
        full_data, = artm_socket.recv_json()

    else:
        logging.info("fail polling")
        return render_template("error.html", error_text="artm service")

    full_data.pop("img_url", None)
    logging.info(full_data['modalities']['classes'])

    distances = sorted(zip(range(len(index_matr)),
                           cdist(index_matr, np.array([full_data["topics"]]), 'cosine')),
                       key=lambda (_, d): d,
                       reverse=False)
    distances = distances[:10]

    near_obj = []
    for (idx, d) in distances:
        q = dict()
        q["dist"], = d
        q["text"] = u", ".join(unicode(_) for _ in dataset[idx]["text"])
        q["tag"] = u", ".join(unicode(_) for _ in dataset[idx]["tag"])
        q["img_url"] = dataset[idx]["img_url"]
        near_obj.append(q)

    for key in full_data:
        if isinstance(full_data[key], list):
            full_data[key] = u", ".join(unicode(_) for _ in full_data[key])

        elif isinstance(full_data[key], dict):
            full_data[key] = u", ".join(u"{} - {}".format(name, cnt) for (name, cnt) in
                                        sorted(full_data[key].items(), key=lambda (_, cnt): cnt, reverse=True))

    return render_template("processing.html", query_text=txt,
                           img_data=base64.b64encode(img) if img else None,
                           data=full_data,
                           srch=near_obj)


@app.route('/', methods=["GET"])
def index():
    return render_template('main.html')


@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
