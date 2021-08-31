FROM ubuntu:18.04

RUN apt-get update && apt-get -y upgrade
RUN apt-get install -y python3 python3-dev python3-pip
RUN DEBIAN_FRONTEND=noninteractive apt-get install -y \
  python3-requests python3-numpy python3-pandas

# Some tools are in perl or java
RUN apt-get install -y perl default-jre-headless

# Use pip to install less-stable dependencies
RUN pip3 install --no-cache-dir scikit-learn==0.19.0

# xgboost build requires cmake
RUN apt-get install -y cmake
RUN pip3 install --no-cache-dir xgboost==0.90

RUN pip3 install joblib depedit

WORKDIR /usr/src/coptic-nlp

COPY . .

# Additional non-python dependencies
RUN apt-get install -y foma-bin
RUN ln -s /usr/bin/flookup bin/foma/
RUN apt-get install -y wget
RUN echo '456548f7cc7b84aec6b639826d9a3ca76ad72b310247bf744780b8f6a28c1aee  maltparser-1.8.tar.gz' > bin/maltparser-1.8.sha2
RUN cd bin && wget http://maltparser.org/dist/maltparser-1.8.tar.gz
RUN cd bin && shasum -c maltparser-1.8.sha2
RUN cd bin && tar xf maltparser-1.8.tar.gz
RUN cp bin/coptic.mco bin/maltparser-1.8/coptic.mco

RUN python3 run_tests.py

CMD [ "python3", "coptic_nlp.py" ]
