"""
Identity Server implementation
"""
import logging

from . import csi_pb2
from . import csi_pb2_grpc

from . import __version__ as DRIVER_VERSION
from . import DRIVER_NAME
from .utils import log_request_and_reply

class IdentityServer(csi_pb2_grpc.IdentityServicer):
    """
    IdentityServer object is responsible for providing
    CSI driver's identity
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.logger = logging.getLogger("IdentityServer")

    @log_request_and_reply
    def GetPluginInfo(self, request, context):
        return csi_pb2.GetPluginInfoResponse(
            name=DRIVER_NAME,
            vendor_version=DRIVER_VERSION
        )

    @log_request_and_reply
    def GetPluginCapabilities(self, request, context):
        # using getattr to avoid Pylint error
        capability_type = getattr(
            csi_pb2.PluginCapability.Service, "Type").Value

        # using getattr to avoid Pylint error
        volume_expansion_type = getattr(
            csi_pb2.PluginCapability.VolumeExpansion, "Type").Value

        return csi_pb2.GetPluginCapabilitiesResponse(
            capabilities=[
                {
                    "service": {
                        "type": capability_type("CONTROLLER_SERVICE")
                    }
                },
                {
                    "service": {
                        "type": capability_type("VOLUME_ACCESSIBILITY_CONSTRAINTS")
                    }
                },
                {
                    "volume_expansion": {
                        "type": volume_expansion_type("UNKNOWN")
                    }
                }
            ]
        )

    @log_request_and_reply
    def Probe(self, request, context):
        return csi_pb2.ProbeResponse()
