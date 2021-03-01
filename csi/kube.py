from kubernetes import client, config
from pathlib import Path

config.load_kube_config()
#config.load_incluster_config()

kube_client = client.CoreV1Api()
app_client = client.AppsV1Api()
# current_namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()
current_namespace = "testspace"

storage_backend_class = "local-path"
backend_capacity = "5Mi"
kubelet_dir = Path("/var/lib/kubelet")
pods_dir = kubelet_dir / "pods"


source_pvc = client.V1PersistentVolumeClaim(
    metadata=client.V1ObjectMeta(
        name="lcrypt-source-pvc"
    ),
    spec=client.V1PersistentVolumeClaimSpec(
        storage_class_name=storage_backend_class,
        resources=client.V1ResourceRequirements(
            requests={
                "capacity": backend_capacity
            }
        )
    )
)

stateful_set = client.V1StatefulSet(
    api_version = 'v1',
    kind = "StatefulSet",
    metadata=client.V1ObjectMeta(
        name="lcrypt-pvc-123",
        namespace=current_namespace
    ),
    spec = client.V1StatefulSetSpec(
        replicas = 1,
        template = client.V1PodTemplateSpec(
            spec = client.V1PodSpec(
                containers = [
                    client.V1Container(
                        name="encrypter",
                        image="busybox",
                        stdin=True, # for debugging
                        tty=True, # debugging
                        security_context=client.V1SecurityContext(
                            privileged=True
                        ),
                        volume_mounts=[
                            client.V1VolumeMount(
                                name="asdf",
                                mount_path=str(pods_dir),
                                mount_propagation=True
                            )
                        ],
                    ),
                ],
                volumes = [
                    client.V1PersistentVolumeClaimVolumeSource(
                        claim_name=source_pvc.metadata.name
                    ),
                    client.V1HostPathVolumeSource(
                        path=str(pods_dir),
                        type="Directory"
                    )
                ]
            )
        )
    ),
)


api_response = app_client.create_namespaced_stateful_set(current_namespace, stateful_set, pretty="true", dry_run="true", field_manager="test")
print(api_response)
