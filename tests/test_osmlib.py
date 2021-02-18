import unittest
from opslib.osm import (
    Validator,
    ValidationError,
    AttributeErrorTypes,
    validator,
    IngressResourceV3Builder,
    FilesV3Builder,
    ContainerV3Builder,
    PodSpecV3Builder,
)
from typing import Optional, List, Dict, Tuple, Set


MANDATORY_ATTRS = [
    "boolean",
    "integer",
    "string",
    "tuple_attr",
    "set_attr",
    "list_int",
    "list_str",
    "dict_str_int",
    "dict_int_str",
]

VALUES = {
    "boolean": False,
    "integer": 2,
    "string": "1",
    "tuple_attr": (1, 2),
    "set_attr": {1, 2},
    "list_int": [1, 2],
    "list_str": ["1", "2"],
    "dict_str_int": {"1": 1, "2": 2},
    "dict_int_str": {1: "1", 2: "2"},
}


class ExampleModel(Validator):
    boolean: bool
    integer: int
    string: str
    tuple_attr: Tuple[int]
    set_attr: Set[int]
    list_int: List[int]
    list_str: List[str]
    dict_str_int: Dict[str, int]
    dict_int_str: Dict[int, str]
    opt_boolean: Optional[bool]
    opt_integer: Optional[int]
    opt_string: Optional[str]
    opt_tuple_attr: Optional[Tuple[int]]
    opt_set_attr: Optional[Set[int]]
    opt_list_int: Optional[List[int]]
    opt_list_str: Optional[List[str]]
    opt_dict_str_int: Optional[Dict[str, int]]
    opt_dict_int_str: Optional[Dict[int, str]]


class TestValidator(unittest.TestCase):
    def test_validator_all_success(self):
        data = {attr: VALUES[attr] for attr in MANDATORY_ATTRS}
        data.update({f"opt_{attr}": VALUES[attr] for attr in MANDATORY_ATTRS})
        model = ExampleModel(**data)
        for attr, value in data.items():
            self.assertEqual(model.__getattribute__(attr), value)

    def test_validator_mandatory_success(self):
        data = {attr: VALUES[attr] for attr in MANDATORY_ATTRS}
        model = ExampleModel(**data)
        for attr, value in data.items():
            self.assertEqual(model.__getattribute__(attr), value)

    def test_validator_mandatory_with_dash_success(self):
        data = VALUES
        model = ExampleModel(**data)
        for attr, value in data.items():
            self.assertEqual(model.__getattribute__(attr.replace("-", "_")), value)

    def test_validator_wrong(self):
        testing_data = {attr: None for attr in MANDATORY_ATTRS}
        testing_data.update({f"opt_{attr}": None for attr in MANDATORY_ATTRS})
        for testing_key in testing_data:
            testing_data[testing_key] = [
                wrong_value
                for key, wrong_value in VALUES.items()
                if key != testing_key and f"opt_{key}" != testing_key
            ]

        for i in range(len(VALUES) - 1):
            data = {k: v.pop() for k, v in testing_data.items()}
            raised = False
            try:
                ExampleModel(**data)
            except ValidationError as e:
                raised = True
                self.assertTrue(
                    all(
                        key in e.attribute_errors
                        and e.attribute_errors[key] == AttributeErrorTypes.INVALID_TYPE
                        for key in data
                        if not ("integer" in key and isinstance(data[key], bool))
                    )
                )
            self.assertTrue(raised)

    def test_validator_missing(self):
        data = {}
        raised = False
        try:
            ExampleModel(**data)
        except ValidationError as e:
            raised = True
            self.assertTrue(
                all(
                    key in e.attribute_errors
                    and e.attribute_errors[key] == AttributeErrorTypes.MISSING
                    for key in data
                )
            )
        self.assertTrue(raised)


class TestPodSpecBuilder(unittest.TestCase):
    def test_all_success(self):
        app_name = "prometheus"
        hostname = "hostname"
        port = 9090
        image_info = {
            "imagePath": "registrypath",
            "username": "username",
            "password": "password",
        }
        files_builder = FilesV3Builder()
        files_builder.add_file(
            "prometheus.yml",
            ("global:\n"),
        )
        files = files_builder.build()
        command = ["/bin/prometheus"]

        container_builder = ContainerV3Builder(app_name, image_info)
        container_builder.add_port(name=app_name, port=port)
        container_builder.add_http_readiness_probe("/-/ready", port)
        container_builder.add_http_liveness_probe("/-/healthy", port)
        container_builder.add_command(command)
        container_builder.add_volume_config("config", "/etc/prometheus", files)
        container = container_builder.build()

        annotations = {"nginx.ingress.kubernetes.io/proxy-body-size": "15m"}

        ingress_resource_builder = IngressResourceV3Builder(
            f"{app_name}-ingress", annotations
        )

        ingress_resource_builder.add_tls([hostname], "tls_secret_name")
        ingress_resource_builder.add_rule(hostname, app_name, port)

        ingress_resource = ingress_resource_builder.build()
        pod_spec_builder = PodSpecV3Builder()
        pod_spec_builder.add_container(container)
        pod_spec_builder.add_ingress_resource(ingress_resource)
        print(pod_spec_builder.build())
        self.assertEqual(
            pod_spec_builder.build(),
            {
                "version": 3,
                "containers": [
                    {
                        "name": "prometheus",
                        "imageDetails": {
                            "imagePath": "registrypath",
                            "username": "username",
                            "password": "password",
                        },
                        "imagePullPolicy": "Always",
                        "ports": [
                            {
                                "name": "prometheus",
                                "containerPort": 9090,
                                "protocol": "TCP",
                            }
                        ],
                        "envConfig": {},
                        "volumeConfig": [
                            {
                                "name": "config",
                                "mountPath": "/etc/prometheus",
                                "files": [
                                    {"path": "prometheus.yml", "content": "global:\n"}
                                ],
                            }
                        ],
                        "kubernetes": {
                            "readinessProbe": {},
                            "livenessProbe": {
                                "httpGet": {"path": "/-/healthy", "port": 9090},
                                "initialDelaySeconds": 10,
                                "timeoutSeconds": 30,
                            },
                        },
                        "command": ["/bin/prometheus"],
                    }
                ],
                "kubernetesResources": {
                    "ingressResources": [
                        {
                            "name": "prometheus-ingress",
                            "annotations": {
                                "nginx.ingress.kubernetes.io/proxy-body-size": "15m"
                            },
                            "spec": {
                                "rules": [
                                    {
                                        "host": "hostname",
                                        "http": {
                                            "paths": [
                                                {
                                                    "path": "/",
                                                    "backend": {
                                                        "serviceName": "prometheus",
                                                        "servicePort": 9090,
                                                    },
                                                }
                                            ]
                                        },
                                    }
                                ],
                                "tls": [
                                    {
                                        "hosts": [["hostname"]],
                                        "secretName": "tls_secret_name",
                                    },
                                ],
                            },
                        }
                    ]
                },
            },
        )
