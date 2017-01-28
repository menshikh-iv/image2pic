# coding=utf-8
import base64
import os
import json
import logging
import random
import numpy as np
import plotly.offline as py
import plotly.graph_objs as go
from scipy.spatial.distance import cdist
import zmq
import markdown
from flask import Flask, render_template, request, redirect, Markup


TIMEOUT_MS = 5000
ARTM_PORT = 1349
NN_PORT = 1350

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(message)s',
                    datefmt='%m-%d %H:%M:%S')

app = Flask(__name__, template_folder="templates/")

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
        to_artm["text"] = txt

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
        artm_data = artm_socket.recv_json()
        if artm_data["status"] != "ok":
            return render_template("error.html", error_text="artm service ({}: {})".format(artm_data["status"],
                                                                                           artm_data["response"]))
        artm_data, = artm_data["response"]

    else:
        logging.info("fail polling")
        return render_template("error.html", error_text="artm service")

    artm_data.pop("img_url", None)
    distances = sorted(zip(range(len(index_matr)),
                           cdist(index_matr, np.array([artm_data["topics"]]), 'cosine')),
                       key=lambda (_, dst): dst,
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

    field_name = u"Темы"
    fd = {field_name: py.plot([go.Bar(x=range(len(artm_data["topics"])),
                                      y=artm_data["topics"], text=artm_data["topics_desc"])],
                              include_plotlyjs=False, output_type='div')}
    fd_ord = [field_name]

    if artm_data.get("view", None):
        if artm_data["view"].get("classes_multinomial_params", None):
            field_name = u"Токены[нейросеть]"
            int_words = filter(lambda (_, v): v > 1, artm_data["view"]["classes_multinomial_params"].items())
            int_words.sort(key=lambda (_, v): v, reverse=True)

            fd[field_name] = "<br>".join(u"{}: {}".format(w, c) for (w, c) in int_words)
            fd_ord.append(field_name)

        if artm_data["view"].get("tokens_from_raw_text", None):
            field_name = u"Токены[текст]"
            tk_raw = sorted(artm_data["view"]["tokens_from_raw_text"].items(), key=lambda (_, v): v, reverse=True)
            fd[field_name] = "<br>".join(u"{}: {}".format(w, c) for (w, c) in tk_raw)
            fd_ord.append(field_name)

    if artm_data["modalities"].get("text", None):
        field_name = u"Модальность[текст]"
        fd[field_name] = py.plot([go.Bar(x=[w for (w, _) in artm_data["modalities"]["text"][:-1]],
                                         y=[val for (_, val) in artm_data["modalities"]["text"][:-1]])],
                                 include_plotlyjs=False, output_type='div')
        fd_ord.append(field_name)

    if artm_data["modalities"].get("classes", None):
        field_name = u"Модальность[нейросеть]"
        fd[field_name] = py.plot([go.Bar(x=[w for (w, _) in artm_data["modalities"]["classes"][:-1]],
                                         y=[val for (_, val) in artm_data["modalities"]["classes"][:-1]])],
                                 include_plotlyjs=False, output_type='div')
        fd_ord.append(field_name)

    if artm_data["modalities"].get("tag", None):
        field_name = u"Модальность[хештеги]"
        fd[field_name] = py.plot([go.Bar(x=[w for (w, _) in artm_data["modalities"]["tag"][:-1]],
                                         y=[val for (_, val) in artm_data["modalities"]["tag"][:-1]])],
                                 include_plotlyjs=False, output_type='div')
        fd_ord.append(field_name)

    return render_template("processing.html", query_text=txt,
                           img_data=base64.b64encode(img) if img else None,
                           data=fd,
                           data_order=fd_ord,
                           srch=near_obj)


@app.route('/processing', methods=["GET"])
def go_to_index():
    return redirect('/')


@app.route('/', methods=["GET"])
def index():
    return render_template('main.html')


@app.route('/about')
def about():
    with open(os.path.join(app.template_folder, "about.md")) as infile:
        md = infile.read()

    content = Markup(markdown.markdown(md.decode("utf-8")))
    return render_template('about.html', content=content)


@app.route("/info")
def info():
    context = zmq.Context()

    sc = context.socket(zmq.REQ)
    sc.connect('tcp://image2pic-artm-service:{}'.format(ARTM_PORT))
    sc.setsockopt(zmq.LINGER, TIMEOUT_MS)
    artm_poller = zmq.Poller()
    artm_poller.register(sc, zmq.POLLIN)

    sc.send_json({"command": "info"})
    if artm_poller.poll(TIMEOUT_MS):
        logging.info("artm poll ok, recv")
        artm_info = sc.recv_json()

    else:
        logging.info("fail polling")
        return render_template("error.html", error_text="artm service (info)")

    return render_template("info.html", artm_info=artm_info)


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80)
