# This file is part of the ops-lib-mysql component for Juju Operator
# Framework Charms.
# Copyright 2021 Canonical Ltd.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the Lesser GNU General Public License version 3,
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranties of
# MERCHANTABILITY, SATISFACTORY QUALITY, or FITNESS FOR A PARTICULAR
# PURPOSE.  See the Lesser GNU General Public License for more details.
#
# You should have received a copy of the Lesser GNU General Public
# License along with this program.  If not, see
# <http://www.gnu.org/licenses/>.

"""
MySQL endpoint implementation for the Operator Framework.
Ported to the Operator Framework from the canonical-osm Reactive
charms at https://git.launchpad.net/canonical-osm
"""

import ops.charm
import ops.framework
import ops.model
from .common import BaseRelationClient


class KeystoneServer(ops.framework.Object):
    """Provides side of a Keystone Endpoint"""

    relation_name: str = None

    def __init__(self, charm: ops.charm.CharmBase, relation_name: str):
        super().__init__(charm, relation_name)
        self.relation_name = relation_name

    def publish_info(
        self,
        host: str,
        port: int,
        user_domain_name: str,
        project_domain_name: str,
        username: str,
        password: str,
        service: str,
    ):
        if self.framework.model.unit.is_leader():
            for relation in self.framework.model.relations[self.relation_name]:
                for unit in relation.units:
                    relation_data = relation.data[unit]
                    relation_data["host"] = str(host)
                    relation_data["port"] = str(port)
                    relation_data["user_domain_name"] = str(user_domain_name)
                    relation_data["project_domain_name"] = str(project_domain_name)
                    relation_data["username"] = str(username)
                    relation_data["password"] = str(password)
                    relation_data["service"] = str(service)


class KeystoneClient(BaseRelationClient):
    """Requires side of a Keystone Endpoint"""

    mandatory_fields = [
        "host",
        "port",
        "user_domain_name",
        "project_domain_name",
        "username",
        "password",
        "service",
    ]

    def __init__(self, charm: ops.charm.CharmBase, relation_name: str):
        super().__init__(charm, relation_name, self.mandatory_fields)

    @property
    def host(self):
        return self.get_data_from_unit("host")

    @property
    def port(self):
        return self.get_data_from_unit("port")

    @property
    def user_domain_name(self):
        return self.get_data_from_unit("user_domain_name")

    @property
    def project_domain_name(self):
        return self.get_data_from_unit("project_domain_name")

    @property
    def username(self):
        return self.get_data_from_unit("username")

    @property
    def password(self):
        return self.get_data_from_unit("password")

    @property
    def service(self):
        return self.get_data_from_unit("service")
