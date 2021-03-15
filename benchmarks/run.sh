#!/bin/bash
set -x

pushd fio-plot/benchmark_script &&
    ./bench_fio -t directory -d /encrypted -s $TESTFILE_SIZE -o "$RESULTDIR" --numjobs $NUMJOBS --iodepth $IODEPTH $@ &&
    ./bench_fio -t directory -d /unencrypted -s $TESTFILE_SIZE -o "$RESULTDIR" --numjobs $NUMJOBS --iodepth $IODEPTH $@ &&
popd &&

pushd "$RESULTDIR" &&
    "$APPDIR"/fio-plot/fio_plot/fio_plot -i ./encrypted/* ./unencrypted/* -T test -r randread --group-bars -C &&
    "$APPDIR"/fio-plot/fio_plot/fio_plot -i ./encrypted/* ./unencrypted/* -T test -r randwrite --group-bars -C
