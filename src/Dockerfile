FROM python:2-slim

ENV PROTOC_VERSION 3.5.1
ENV PY_SIX_VERSION 1.11.0

RUN apt-get update && apt-get install -y wget unzip && \
	# install protoc
	wget https://github.com/google/protobuf/releases/download/v$PROTOC_VERSION/protoc-$PROTOC_VERSION-linux-x86_64.zip && \
    unzip protoc-$PROTOC_VERSION-linux-x86_64.zip -d protoc3 && \
    mv protoc3/bin/* /usr/local/bin/ && mv protoc3/include/* /usr/local/include/ && \

    # install six (python3)
    # wget https://pypi.python.org/packages/16/d8/bc6316cf98419719bd59c91742194c111b6f2e85abac88e496adefaf7afe/six-1.11.0.tar.gz#md5=d12789f9baf7e9fb2524c0c64f1773f8 && \
    # tar -zxvf six-$PY_SIX_VERSION.tar.gz && cd six-$PY_SIX_VERSION && python setup.py install && cd / && \

    # install python protobuf
	wget https://github.com/google/protobuf/releases/download/v$PROTOC_VERSION/protobuf-python-$PROTOC_VERSION.zip && \
    unzip protobuf-python-$PROTOC_VERSION.zip && \
    cd protobuf-$PROTOC_VERSION/python && python setup.py build && python setup.py install && cd / && \

    # cleanup
    apt-get purge -y wget unzip && rm protoc-$PROTOC_VERSION-linux-x86_64.zip protobuf-python-$PROTOC_VERSION.zip && \
    rm -rf proto3 proto3_python six-$PY_SIX_VERSION* && rm -rf /var/lib/apt/lists/*

ADD protoc /protoc
