# image2pic
![logo](https://raw.githubusercontent.com/menshikh-iv/image2pic/master/webapp/app/static/images/i2p-logo.jpg)
## Image topic modeling.

We are two students: [Ivan Menshikh](https://github.com/menshikh-iv) && [Gennady Shtekh](https://github.com/ShT3ch).
This repo is created to complete project assignment for one of master degree courses in IMCS UrFU.
The idea of the project was to use pictures from some social network in some parallel way. We decided to create search-annotation engine based on cutting edge topic modeling technique called Additive Regularization of Topic Models(ARTM).
Long story short: ARTM allows us to tie different discrete features of "documents" together, e.g. text tokens, some hashtags and discrete image descriptors can be used for describing of one post in a social network. With ARTM it is possible to find a stochastic-matrix-based connection between text tokens and discreet image descriptors. We use this feature for:
 - Search similar(by semantic) posts and images for given posts and images(works well now)
 - Give some term-based description for given photo(works badly now)
 - Search pictures for given descriptions(works badly now)

The Plan:
 - [x] To collect posts with photo and text description(long enough)
 - [x] Clean them from ad posts
 - [x] Find a way to build discrete image descriptors(based on inception-v3 now)
 - [x] Build a textual preprocessing pipeline(based on nltk, pymorphy2 and some custom solutions, now it supports english and russian via stemming)
 - [x] Combine text and image date together with topic modeling framework called BigARTM
 - [x] Build a search index for fast search in semantic space(It is simple linear search now)
 - [x] Build a demo website with our search
 - [x] Pack the app into Docker-Compose


 We are almost done but we need to crawl more data for finer tuning of the model.


## Links:
 - [ARTM paper](https://s3-eu-west-1.amazonaws.com/artm/Voron15aist.pdf)
 - [More ARTM papers](https://github.com/bigartm/bigartm/wiki/Publications)
 - [BigARTM](https://github.com/bigartm/bigartm)
 - [Inception keras-based implementation](https://keras.io/applications/)
