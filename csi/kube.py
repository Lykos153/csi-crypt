import kubernetes
import pathlib
import jinja2, yaml, json
import logging
from . import MODULE_PATH

class ApiClient:
    def __init__(self):
        self.logger = logging.getLogger("ApiClient")
        kubernetes.config.load_incluster_config()
        self.namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()

        self.client = kubernetes.client.ApiClient()

        templateLoader = jinja2.FileSystemLoader(searchpath=str(MODULE_PATH / "templates"))
        self.templateEnv = jinja2.Environment(loader=templateLoader, autoescape=False)

    def _create_from_template(self, template_name: str, **kwargs):
        template = self.templateEnv.get_template(template_name)
        rendered = template.render(**kwargs)
        self._create_from_yaml(rendered)

    def _create_from_yaml(self, rendered_yaml: str):
        for obj in yaml.safe_load_all(rendered_yaml):
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


class NodeApiClient(ApiClient):
    def __init__(self, kubelet_dir: pathlib.Path, node_name: str):
        super().__init__()
        self.kubelet_dir = pathlib.Path(kubelet_dir)
        self.node_name = node_name

    def create_encrypter(
                        self,
                        name: str,
                        volume_id: str,
                        backendClaimName: str
                    ):
        self._create_from_template(
            "encrypter.yaml",
            encrypterName=name,
            kubeletDir=self.kubelet_dir,
            nodeName=self.node_name,
            imageName="busybox", # debugging
            volumeId=volume_id,
            backendClaimName=backendClaimName,
        )

class ControllerApiClient(ApiClient):
    def create_pvc(
                    self, 
                    name: str,
                    capacity_bytes: int,
                    backend_class: str=''
                ):
        self._create_from_template(
            "pvc.yaml",
            backendClaimName=name,
            backendStorageClass=backend_class,
            backendCapacity=capacity_bytes,
        )
