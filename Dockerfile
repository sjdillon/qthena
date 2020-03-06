FROM python:3

RUN pip install virtualenv
RUN pip install tox
RUN apt-get update
RUN curl -sL https://deb.nodesource.com/setup
RUN apt-get install -yq nodejs build-essential
RUN apt-get install -yq npm
RUN npm install -g serverless
