"""
controller server implementation
"""
import logging

import grpc

import csi_pb2
import csi_pb2_grpc

class ControllerServer(csi_pb2_grpc.ControllerServicer):
    """
    ControllerServer object is responsible for handling host
    volume mount and PV creation.
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("ControllerServer")

    def ControllerGetCapabilities(self, request, context):
        self.logger.debug("Received request: ControllerGetCapabilities")
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

    def ValidateVolumeCapabilities(self, request, context):
        # TODO
        pass

    def CreateVolume(self, request, context):
        self.logger.debug("Received request: CreateVolume")
        context.set_code(grpc.StatusCode.RESOURCE_EXHAUSTED)
        return csi_pb2.CreateVolumeResponse()

    def DeleteVolume(self, request, context):
        self.logger.debug("Received request: DeleteVolume")
        return csi_pb2.DeleteVolumeResponse()
