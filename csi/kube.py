import kubernetes
import pathlib
import jinja2, yaml, json
import logging
from . import MODULE_PATH

class ApiClient:
    def __init__(self, kubelet_dir: pathlib.Path, node_name: str):
        self.logger = logging.getLogger("ApiClient")
        kubernetes.config.load_incluster_config()
        self.namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()

        self.client = kubernetes.client.ApiClient()
        self.kubelet_dir = pathlib.Path(kubelet_dir)
        self.node_name = node_name

        templateLoader = jinja2.FileSystemLoader(searchpath=str(MODULE_PATH / "templates"))
        self.templateEnv = jinja2.Environment(loader=templateLoader, autoescape=False)

    def create_encrypter(
                        self,
                        name: str,
                        volume_id: str,
                        capacity_bytes: int,
                        backend_class: str=''
                    ):
        template = self.templateEnv.get_template("gocrypt-pvc.yaml")
        rendered = template.render(
            encrypterName=name,
            kubeletDir=self.kubelet_dir,
            backendClaimName=f"lcrypt-backend-{volume_id}",
            backendStorageClass=backend_class,
            backendCapacity=capacity_bytes,
            nodeName=self.node_name,
            imageName="busybox", # debugging
            volumeId=volume_id,
        )
        for obj in yaml.safe_load_all(rendered):
            try:
                kubernetes.utils.create_from_dict(
                    self.client,
                    obj,
                    namespace=self.namespace
                )
            except kubernetes.utils.FailToCreateError as e:
                body = json.loads(e.api_exceptions[0].body)
                if body['reason'] == "AlreadyExists":
                    self.logger.info(body['message'])
                    continue
                else:
                    raise
