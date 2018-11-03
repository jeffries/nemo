FROM ubuntu:bionic

ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update
RUN apt-get install -y gnupg ca-certificates
ADD https://dl.yarnpkg.com/debian/pubkey.gpg /tmp/yarnpkg.pub.gpg
RUN cat /tmp/yarnpkg.pub.gpg | apt-key add -
RUN rm /tmp/yarnpkg.pub.gpg
RUN echo "deb https://dl.yarnpkg.com/debian/ stable main" | tee /etc/apt/sources.list.d/yarn.list
RUN apt-get update
RUN apt-get install -y python3 python3-pip postgresql libpq-dev yarn

RUN mkdir -p /var/nemo/marlin
WORKDIR /var/nemo

# Add server code
COPY requirements.txt ./
RUN pip3 install -r requirements.txt
COPY nemo ./nemo
COPY setup.py ./

# Add client code
COPY marlin ./marlin
WORKDIR /var/nemo/marlin
RUN rm -rf node_modules
RUN yarn

# Copy runtime executables 
WORKDIR /var/nemo
COPY bin ./bin

EXPOSE 5000
EXPOSE 5001

CMD /var/nemo/bin/entrypoint.sh
