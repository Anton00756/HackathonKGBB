FROM python:3.11-alpine

ENV TZ=Europe/Moscow
ENV PYTHONPATH=/work_dir

RUN mkdir work_dir
WORKDIR /work_dir
COPY components components
COPY grafana_dashboard.json grafana_dashboard.json
COPY sources.json sources.json
COPY requirements.txt requirements.txt

RUN addgroup -g 1000 user && adduser -h /home/user -u 1000 -G user -s /bin/sh -D user
RUN addgroup -g 1001 docker && addgroup user docker
RUN chown -R user:user /var
RUN chown -R user:user /work_dir

RUN ln -sf /proc/1/fd/1 /var/log/container_logs.log

USER user

RUN pip install wheel setuptools pip --upgrade
RUN pip install -r requirements.txt