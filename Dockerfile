FROM python:3.12-alpine

RUN addgroup --gid 1500 droppler && \
    adduser --home /home/droppler --uid 1500 --shell /usr/bin/bash --ingroup droppler --system droppler && \
    mkdir /home/droppler/runtime && \
    chown droppler:droppler /home/droppler/runtime

WORKDIR /home/droppler/runtime
COPY --chown=droppler:droppler . .

USER droppler
RUN pip install -r requirements.txt

ENTRYPOINT ["python", "/home/droppler/runtime/main.py"]
