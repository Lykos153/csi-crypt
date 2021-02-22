"""
controller server implementation
"""
import logging

import grpc

from . import csi_pb2
from . import csi_pb2_grpc
from .utils import log_request_and_reply

class ControllerServer(csi_pb2_grpc.ControllerServicer):
    """
    ControllerServer object is responsible for handling host
    volume mount and PV creation.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("ControllerServer")

    @log_request_and_reply
    def ControllerGetCapabilities(self, request, context):
        # using getattr to avoid Pylint error
        capability_type = getattr(
            csi_pb2.ControllerServiceCapability.RPC, "Type").Value

        return csi_pb2.ControllerGetCapabilitiesResponse(
            capabilities=[
                {
                    "rpc": {
                        "type": capability_type("CREATE_DELETE_VOLUME")
                    }
                },
            ]
        )

    @log_request_and_reply
    def ValidateVolumeCapabilities(self, request, context):
        # TODO
        pass

    @log_request_and_reply
    def CreateVolume(self, request, context):
        context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
        return csi_pb2.CreateVolumeResponse()

    @log_request_and_reply
    def DeleteVolume(self, request, context):
        return csi_pb2.DeleteVolumeResponse()
