"""
Starting point of CSI driver GRP server
"""
import os
import time
import concurrent
import logging

import grpc

import csi_pb2_grpc
from identityserver import IdentityServer
from controllerserver import ControllerServer
from nodeserver import NodeServer


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def main():
    """
    Register Controller Server, Node server and Identity Server and start
    the GRPC server in required endpoint
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    logger.addHandler(h)

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    csi_pb2_grpc.add_ControllerServicer_to_server(ControllerServer(), server)
    csi_pb2_grpc.add_NodeServicer_to_server(NodeServer(), server)
    csi_pb2_grpc.add_IdentityServicer_to_server(IdentityServer(), server)

    endpoint = os.environ.get("CSI_ENDPOINT", None)
    if endpoint is None:
        logger.error("CSI_ENDPOINT environment variable not set")
        raise SystemExit
    server.add_insecure_port(endpoint)
    logger.info("Server started")
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    main()
