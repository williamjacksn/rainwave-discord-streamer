FROM python:3.12-slim

RUN /usr/sbin/useradd --create-home --shell /bin/bash --user-group python

USER python
RUN /usr/local/bin/python -m venv /home/python/venv

COPY --chown=python:python requirements.txt /home/python/rainwave-discord-streamer/requirements.txt
RUN /home/python/venv/bin/python -m pip install --no-cache-dir --update pip
RUN /home/python/venv/bin/pip install --no-cache-dir pip-tools
RUN /home/python/venv/bin/pip install --no-cache-dir --requirement /home/python/rainwave-discord-streamer/requirements.txt

ENV PATH="/home/python/venv/bin:${PATH}" \
    PYTHONDONTWRITEBYTECODE="1" \
    PYTHONUNBUFFERED="1" \
    TZ="Etc/UTC"

LABEL org.opencontainers.image.authors="William Jackson <william@subtlecoolness.com>" \
      org.opencontainers.image.source="https://github.com/williamjacksn/rainwave-discord-streamer"
