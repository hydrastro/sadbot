FROM alpine:3.13
ENV PATH /usr/local/bin:$PATH
ENV LANG C.UTF-8
# ENV TOKEN placeholder
RUN apk add --no-cache python3 py3-requests
WORKDIR /usr/src/app
COPY sadbot/* /usr/src/app/sadbot/
COPY * /usr/src/app/
ENV PYTHONPATH .
CMD ["python3", "-m", "sadbot"]
