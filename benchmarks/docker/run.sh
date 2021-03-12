#!/bin/bash

RESULTDIR=/results
APPDIR=/appdir

pushd fio-plot/benchmark_script
    ./bench_fio -t directory -d /encrypted -s $TESTFILE_SIZE -o "$RESULTDIR" &&
    ./bench_fio -t directory -d /unencrypted -s $TESTFILE_SIZE -o "$RESULTDIR"
popd

pushd "$RESULTDIR"
    "$APPDIR"/fio-plot/fio_plot/fio_plot -i ./encrypted/* ./unencrypted/* -T test -r randread --group-bars -C
