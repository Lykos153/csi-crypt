FROM python
RUN mkdir -p /appdir

RUN pip install --upgrade pip
COPY requirements.txt /appdir
RUN pip install -r /appdir/requirements.txt
COPY csi_crypt /appdir/csi_crypt
RUN make -C /appdir/csi_crypt

ENV CSI_ENDPOINT unix:///csi.sock
ENV KUBELET_DIR /var/lib/kubelet
ENV BACKEND_STORAGE_CLASS ""
ENV MAX_CONCURRENT_WORKERS 10
ENV DEBUG false
ENV PYTHONPATH /appdir

#TODO: Clean cache and temp files

CMD ["python",  "-m", "csi_crypt.run"]
