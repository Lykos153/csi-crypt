FROM python
RUN mkdir -p /appdir
ARG package_dir

RUN pip install --upgrade pip
COPY requirements.txt /appdir
RUN pip install -r /appdir/requirements.txt
COPY ${package_dir} /appdir/csi
RUN make -C /appdir/csi

ENV CSI_ENDPOINT unix:///csi.sock
ENV KUBELET_DIR /var/lib/kubelet
ENV BACKEND_STORAGE_CLASS ""
ENV MAX_CONCURRENT_WORKERS 10
ENV DEBUG false
ENV PYTHONPATH /appdir

CMD ["python",  "-m", "csi.run"]
