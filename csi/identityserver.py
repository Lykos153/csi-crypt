"""
Identity Server implementation
"""
import csi_pb2
import csi_pb2_grpc


DRIVER_NAME = "csi-luks"
DRIVER_VERSION = "0.0.1"


class IdentityServer(csi_pb2_grpc.IdentityServicer):
    """
    IdentityServer object is responsible for providing
    CSI driver's identity
    Ref:https://github.com/container-storage-interface/spec/blob/master/spec.md
    """
    def GetPluginInfo(self, request, context):
        return csi_pb2.GetPluginInfoResponse(
            name=DRIVER_NAME,
            vendor_version=DRIVER_VERSION
        )

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

    def Probe(self, request, context):
        return csi_pb2.ProbeResponse()
