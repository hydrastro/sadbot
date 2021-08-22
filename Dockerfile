FROM python:3.8-slim-buster
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
ENV TOKEN placeholder
WORKDIR /usr/src/app
COPY . .
RUN pip3 install -r requirements.txt
ENV PYTHONPATH .
CMD ["python3", "-m", "sadbot"]
