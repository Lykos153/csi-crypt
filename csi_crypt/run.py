"""
Starting point of CSI driver GRP server
"""
import os
import time
import concurrent
import logging
import signal

import grpc

from . import csi_pb2_grpc
from .identityserver import IdentityServer
from .controllerserver import ControllerServer
from .nodeserver import NodeServer
from .utils import env_required

server = None


def handler_stop_signals(signum, frame):
    logger.info(f"Received signal {signum}")
    global server
    server.stop(0)
    raise SystemExit

def main():
    """
    Register Controller Server, Node server and Identity Server and start
    the GRPC server in required endpoint
    """

    global server
    server = grpc.server(concurrent.futures.ThreadPoolExecutor(
        max_workers=int(env_required("MAX_CONCURRENT_WORKERS"))
    ))
    csi_pb2_grpc.add_IdentityServicer_to_server(IdentityServer(), server)

    csi_role = env_required("CSI_ROLE") #TODO: Rename variable. CSI_ prefix is reserved by CSI spec
    if csi_role == "nodeplugin":
        node_name = env_required("NODE_NAME")
        if len(node_name) > 128: #TODO: Increase when switching to newer proto
            logger.info(
                "NODE_NAME exceeds 128 bytes. It will be truncated when"
                " sending NodeGetInfoResponse"
            )
        csi_pb2_grpc.add_NodeServicer_to_server(
            NodeServer(
                node_name,
                env_required("KUBELET_DIR"),
                env_required("ENCRYPTER_IMAGE_NAME"), #TODO make configurable via StorageClass
                env_required("ENCRYPTER_IMAGE_PULL_SECRET") #TODO shouldn't be required
            ),
            server
        )
    elif csi_role == "provisioner":
        csi_pb2_grpc.add_ControllerServicer_to_server(
            ControllerServer(env_required("BACKEND_STORAGE_CLASS")), #TODO: Make configurable vis StorageClass
            server
        )

    server.add_insecure_port(env_required("CSI_ENDPOINT"))
    server.start()
    logger.info("Server started")
    
    signal.signal(signal.SIGINT, handler_stop_signals)
    signal.signal(signal.SIGTERM, handler_stop_signals)

    _ONE_DAY_IN_SECONDS = 60 * 60 * 24
    while True:
        time.sleep(_ONE_DAY_IN_SECONDS)


if __name__ == '__main__':
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    h = logging.StreamHandler()
    h.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(h)

    if os.environ.get("DEBUG", "false") == "true":
        logger.debug("Running in debugger mode")
        import pdb
        debugger = pdb.Pdb()
        debugger.rcLines.extend("continue")
        debugger.runcall(main)
    else:
        main()
