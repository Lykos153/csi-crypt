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

        self.api_client = kubernetes.client.ApiClient()

        template_dir = MODULE_PATH / "templates"
        self.logger.debug(f"template_dir={template_dir}")
        templateLoader = jinja2.FileSystemLoader(searchpath=str(template_dir))
        self.templateEnv = jinja2.Environment(loader=templateLoader, autoescape=False)

    def _create_from_template(self, template_name: str, **kwargs):
        self.logger.debug(f"Rendering template {template_name}")
        template = self.templateEnv.get_template(template_name)
        rendered = template.render(**kwargs)
        self.logger.debug(f"\n{rendered}")
        self._create_from_yaml(rendered)

    def _create_from_yaml(self, rendered_yaml: str):
        for obj in yaml.safe_load_all(rendered_yaml):
            try:
                kubernetes.utils.create_from_dict(
                    self.api_client,
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

        #TODO: Possibility to add own labels?   
        v1 = kubernetes.client.CoreV1Api(self.api_client)
        #TODO: Maybe use all labels instead of just hostname
        self.node_hostname = v1.list_node(
            field_selector=f"metadata.name={node_name}"
            ).items[0].metadata.labels['kubernetes.io/hostname']
        self.logger.debug(f"node_hostname={self.node_hostname}")
        if len(
            v1.list_node(
                label_selector \
                    = f'kubernetes.io/hostname={self.node_hostname}'
            ).items) != 1:
            errmsg = f"node_hostname={self.node_hostname} is not unique"
            self.logger.error(errmsg)
            raise Exception(errmsg) #TODO: Use specific exception
        #TODO: Watch for updates

    def create_encrypter(
                        self,
                        name: str,
                        image_name: str,
                        volume_id: str,
                        backendClaimName: str,
                        target_path: pathlib.Path,
                        encryption_key: str,
                        pull_secret: str=None
                    ):
        self._create_from_template(
            "encrypter.yaml",
            encrypterName=name,
            kubeletDir=self.kubelet_dir,
            nodeHostname=self.node_hostname,
            imageName=image_name,
            volumeId=volume_id,
            backendClaimName=backendClaimName,
            pullSecret=pull_secret,
            secretName=name,
            encryptionKey=encryption_key,
            targetPath=target_path
        )

        #TODO: Right now we're just checking if the encryptor is running. We want to have proper communication at some point
        watch = kubernetes.watch.Watch()
        core_v1 = kubernetes.client.CoreV1Api(self.api_client)
        for event in watch.stream(
                        func=core_v1.list_namespaced_pod,
                        namespace=self.namespace,
                        label_selector=f"lcrypt.silvio-ankermann.de/volume-id={volume_id}",
                        # field_selector=f"metadata.name={name}"
                        ):
            if event["object"].status.phase == "Running":
                watch.stop()
            if event["type"] == "DELETED":
                watch.stop()
                errmsg = f"{name} deleted before it started"
                self.logger.error(errmsg)
                raise Exception(errmsg) #TODO: Specific error message

    def delete_encrypter(self, name: str):
        aps_v1_api = kubernetes.client.AppsV1Api(self.api_client)
        try:
            aps_v1_api.delete_namespaced_deployment(
                name,
                self.namespace
            )
        except kubernetes.client.ApiException as e:
            if e.reason == "Not Found":
                self.logger.info(f"Deployment {name} didn't exist when trying to delete it")
            else:
                raise

        core_v1_api = kubernetes.client.CoreV1Api(self.api_client)
        try:
            core_v1_api.delete_namespaced_secret(
                name,
                self.namespace
            )
        except kubernetes.client.ApiException as e:
            if e.reason == "Not Found":
                self.logger.info(f"Secret {name} didn't exist when trying to delete it")
            else:
                raise

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

    def delete_pvc(self, name: str):
        api = kubernetes.client.CoreV1Api(self.api_client)
        try:
            api.delete_namespaced_persistent_volume_claim(
                name,
                self.namespace
            )
        except kubernetes.client.ApiException as e:
            if e.reason == "Not Found":
                self.logger.info(f"{name} didn't exist when trying to delete it")
            else:
                raise
