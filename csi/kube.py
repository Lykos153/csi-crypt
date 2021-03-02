import kubernetes
import pathlib
import jinja2, yaml, json
import logging

class ApiClient:
    def __init__(self, kubelet_dir: pathlib.Path):
        self.logger = logging.getLogger("ApiClient")
        kubernetes.config.load_incluster_config()
        self.namespace = open("/var/run/secrets/kubernetes.io/serviceaccount/namespace").read()

        self.client = kubernetes.client.ApiClient()
        self.kubelet_dir = pathlib.Path(kubelet_dir)
        self.pods_dir = self.kubelet_dir / "pods"

        templateLoader = jinja2.FileSystemLoader(searchpath="csi/templates/")
        self.templateEnv = jinja2.Environment(loader=templateLoader, autoescape=False)

    def create_encrypter(
                        self,
                        pvc_name: str,
                        capacity_bytes: int,
                        backend_class: str=None
                    ):
        template = self.templateEnv.get_template("gocrypt-pvc.yaml")
        rendered = template.render(
            encrypterName="lcrypt-gocrypt-pvc",
            kubeletDir=self.kubelet_dir,
            backendClaimName="lcrypt-backend",
            backendStorageClass=backend_class,
            backendCapacity=capacity_bytes,
        )
        for obj in yaml.safe_load_all(rendered):
            try:
                kubernetes.utils.create_from_dict(
                    self.client,
                    obj,
                    namespace=self.namespace
                )
            except kubernetes.utils.FailToCreateError as e:
                # reason = json.loads(e.api_exceptions[0].body)['reason']
                raise
