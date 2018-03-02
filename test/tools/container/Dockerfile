FROM umegaya/pb3sol

RUN apt-get update && apt-get install -y nodejs npm curl git && \
	npm install -g n && n stable && \
	ln -sf /usr/local/bin/node /usr/bin/node && \
	npm install -g truffle && rm -rf /var/lib/apt/lists/*
