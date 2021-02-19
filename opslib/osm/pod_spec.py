#!/usr/bin/env python3
# Copyright 2021 Canonical Ltd.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.
#
# For those usages not covered by the Apache License, Version 2.0 please
# contact: legal@canonical.com
#
# To get in touch with the maintainers, please contact:
# osm-charmers@lists.launchpad.net
##

__all__ = [
    "IngressResourceV3Builder",
    "FilesV3Builder",
    "ContainerV3Builder",
    "PodSpecV3Builder",
]


class IngressResourceV3Builder:
    def __init__(self, name, annotations):
        self.name = name
        self.annotations = annotations
        self._rules = []
        self._tls = []

    @property
    def rules(self):
        return self._rules

    @property
    def tls(self):
        return self._tls

    @property
    def ingress_resource(self):
        r = {
            "name": self.name,
            "annotations": self.annotations,
            "spec": {"rules": self.rules},
        }
        if self._tls:
            r["spec"]["tls"] = self.tls
        return r

    def add_rule(self, hostname: str, service_name, port, path: str = "/"):
        # This function only supports one path per rule for simplicity
        self._rules.append(
            {
                "host": hostname,
                "http": {
                    "paths": [
                        {
                            "path": path,
                            "backend": {
                                "serviceName": service_name,
                                "servicePort": port,
                            },
                        }
                    ]
                },
            }
        )

    def add_tls(self, hosts, secret_name):
        tls = {"hosts": hosts}
        if secret_name:
            tls["secretName"] = secret_name
        self._tls.append(tls)

    def build(self):
        return self.ingress_resource


class FilesV3Builder:
    def __init__(self):
        self._files = []

    @property
    def files(self):
        return self._files

    def add_file(self, path: str, content: str):
        self._files.append({"path": path, "content": content})

    def build(self):
        return self.files


class ContainerV3Builder:
    def __init__(self, name, image_info, image_pull_policy="Always"):
        self.name = name
        self.image_info = image_info
        self.image_pull_policy = image_pull_policy
        self._readiness_probe = {}
        self._liveness_probe = {}
        self._volume_config = []
        self._ports = []
        self._envs = {}
        self._command = None

    @property
    def readiness_probe(self):
        return self._readiness_probe

    @property
    def liveness_probe(self):
        return self._liveness_probe

    @property
    def ports(self):
        return self._ports

    @property
    def env_config(self):
        return self._envs

    @property
    def command(self):
        return self._command

    @property
    def volume_config(self):
        return self._volume_config

    def add_port(self, name, port, protocol="TCP"):
        self._ports.append({"name": name, "containerPort": port, "protocol": protocol})

    def add_volume_config(self, name, mount_path, files):
        self._volume_config.append(
            {
                "name": name,
                "mountPath": mount_path,
                "files": files,
            }
        )

    def add_command(self, command):
        self._command = command

    def add_http_readiness_probe(
        self,
        path,
        port,
        initialDelaySeconds=10,
        timeoutSeconds=30,
    ):
        self._liveness_probe = self._http_probe(
            path, port, initialDelaySeconds, timeoutSeconds
        )

    def add_http_liveness_probe(
        self,
        path,
        port,
        initialDelaySeconds=10,
        timeoutSeconds=30,
    ):
        self._liveness_probe = self._http_probe(
            path, port, initialDelaySeconds, timeoutSeconds
        )

    def add_env(self, key: str, value: str):
        self._envs[key] = value

    def add_envs(self, envs: dict):
        self._envs = {**self._envs, **envs}

    def _http_probe(self, path, port, initialDelaySeconds, timeoutSeconds):
        return {
            "httpGet": {
                "path": path,
                "port": port,
            },
            "initialDelaySeconds": initialDelaySeconds,
            "timeoutSeconds": timeoutSeconds,
        }

    def build(self):
        container = {
            "name": self.name,
            "imageDetails": self.image_info,
            "imagePullPolicy": self.image_pull_policy,
            "ports": self.ports,
            "envConfig": self.env_config,
            "volumeConfig": self.volume_config,
            "kubernetes": {
                "readinessProbe": self.readiness_probe,
                "livenessProbe": self.liveness_probe,
            },
        }
        if self.command:
            container["command"] = self.command
        return container


class PodSpecV3Builder:
    def __init__(self):
        self._containers = []
        self._ingress_resources = []

    @property
    def containers(self):
        return self._containers

    @property
    def ingress_resources(self):
        return self._ingress_resources

    @property
    def pod_spec(self):
        return {
            "version": 3,
            "containers": self.containers,
            "kubernetesResources": {"ingressResources": self.ingress_resources},
        }

    def add_container(self, container):
        self._containers.append(container)

    def add_ingress_resource(self, ingress_resource):
        self._ingress_resources.append(ingress_resource)

    def build(self):
        return self.pod_spec
