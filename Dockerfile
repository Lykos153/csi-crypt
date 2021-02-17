# FROM python:alpine as builder

# RUN apk add --no-cache alpine-sdk linux-headers
# RUN pip install --upgrade pip
# COPY requirements.txt /
# RUN pip install -r /requirements.txt

FROM python
RUN mkdir -p /appdir

RUN pip install --upgrade pip
COPY requirements.txt /appdir
RUN pip install -r /appdir/requirements.txt
COPY Makefile /appdir
COPY csi /appdir/csi
RUN make -C /appdir

ENV CSI_ENDPOINT unix:///csi.sock

CMD ["python",  "/appdir/csi/run.py"]
