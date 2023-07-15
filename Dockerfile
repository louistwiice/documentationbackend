##FROM python:3.10-alpline
#FROM python:3.9
#
## Set Environment Variable
#ENV PYTHONUNBUFFERED 1
#
##RUN apk update && apk add gcc
## ENV C_FORCE_ROOT tru
#RUN addgroup --system wizall && adduser --system --group wizall
#RUN python -m venv /opt/wizall/venv
#ENV PATH="/opt/wizall/venv/bin:$PATH"
#WORKDIR /home/wizall
#
## Update pip
#RUN pip install --upgrade pip
#
#COPY requirements.txt requirements.txt
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY ./scripts scripts
#
#RUN chmod +x /home/wizall/scripts/run_app.sh
#RUN chmod +x /home/wizall/scripts/wait_for_postgres.py
## removing temporary packages from docker and removing cache
#
#COPY src src
#
#RUN find -type d -name __pycache__ -prune -exec rm -rf {} \; && \
#    rm -rf ~/.cache/pip
#
#USER wizall
#
#ENTRYPOINT ["sh", "/home/wizall/scripts/run_app.sh"]

FROM python:3.9 AS base-builder

# Set Environment Variable
ENV PYTHONUNBUFFERED 1

RUN python -m venv /opt/wizall/venv
ENV PATH="/opt/wizall/venv/bin:$PATH"

# Update pip
RUN pip install --upgrade pip

COPY base-requirements.txt .
RUN pip install --no-cache-dir -r base-requirements.txt

WORKDIR /home/wizall

COPY ./scripts scripts

RUN chmod +x /home/wizall/scripts/run_app.sh
RUN chmod +x /home/wizall/scripts/wait_for_postgres.py

COPY  src src

RUN find -type d -name __pycache__ -prune -exec rm -rf {} \; && \
    rm -rf ~/.cache/pip


FROM python:3.9 AS runner
COPY --from=base-builder /opt/wizall/venv /opt/wizall/venv
COPY --from=base-builder /home/wizall /home/wizall

RUN addgroup --system wizall && adduser --system --group wizall

WORKDIR /home/wizall

RUN chown wizall:wizall src

ENV PATH="/opt/wizall/venv/bin:$PATH"
USER wizall

ENTRYPOINT ["sh", "/home/wizall/scripts/run_app.sh"]
