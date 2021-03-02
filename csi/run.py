"""
Starting point of CSI driver GRP server
"""
import os
import time
import concurrent
import logging

import grpc

from . import csi_pb2_grpc
from .identityserver import IdentityServer
from .controllerserver import ControllerServer
from .nodeserver import NodeServer


_ONE_DAY_IN_SECONDS = 60 * 60 * 24


def main():
    """
    Register Controller Server, Node server and Identity Server and start
    the GRPC server in required endpoint
    """
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

    try:
        node_name = os.environ["NODE_NAME"]
        endpoint = os.environ["CSI_ENDPOINT"]
        csi_role = os.environ["CSI_ROLE"]
        kubelet_dir = os.environ["KUBELET_DIR"]
    except KeyError as e:
        logger.error(f"{e.args[0]} environment variable not set")
        raise SystemExit
    if len(node_name) > 128:
        logger.info(
            "NODE_NAME exceeds 128 bytes. It will be truncated when"
            " sending NodeGetInfoResponse"
        )

    server = grpc.server(concurrent.futures.ThreadPoolExecutor(max_workers=10))
    csi_pb2_grpc.add_IdentityServicer_to_server(IdentityServer(), server)
    if csi_role == "nodeplugin":
        csi_pb2_grpc.add_NodeServicer_to_server(NodeServer(node_name, kubelet_dir), server)
    elif csi_role == "provisioner":
        csi_pb2_grpc.add_ControllerServicer_to_server(ControllerServer(), server)

    server.add_insecure_port(endpoint)
    logger.info("Server started")
    server.start()
    try:
        while True:
            time.sleep(_ONE_DAY_IN_SECONDS)
    except KeyboardInterrupt:
        server.stop(0)


if __name__ == '__main__':
    if os.environ.get("DEBUG", "false") == "true":
        import pdb
        debugger = pdb.Pdb()
        debugger.rcLines.extend("continue")
        debugger.runcall(main)
    else:
        main()
