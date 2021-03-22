FROM python
ARG FIO_PLOT_VERSION=1.0.8

RUN apt-get update && apt-get upgrade -y
RUN apt-get install -y curl fio

RUN mkdir -p /appdir
WORKDIR /appdir

RUN curl -LO "https://github.com/louwrentius/fio-plot/archive/v$FIO_PLOT_VERSION.tar.gz" && \
    tar xf "v$FIO_PLOT_VERSION.tar.gz" && \
    rm "v$FIO_PLOT_VERSION.tar.gz" && \
    mv "fio-plot-$FIO_PLOT_VERSION" "fio-plot"

RUN pip install -r fio-plot/benchmark_script/requirements.txt \
                -r fio-plot/fio_plot/requirements.txt

RUN mkdir /encrypted /unencrypted
