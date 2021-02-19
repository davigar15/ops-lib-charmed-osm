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

import logging

import ops.charm
import ops.framework
import ops.model
from ops.model import Application

__all__ = [
    "PrometheusClient",
    "PrometheusClientEvents",
]


class PrometheusChangedEvent(ops.framework.EventBase):
    """PrometheusChangedEvent"""


class PrometheusClientEvents(ops.framework.ObjectEvents):
    changed = ops.framework.EventSource(PrometheusChangedEvent)


class PrometheusServer(ops.framework.Object):
    """Provides side of a Prometheus Endpoint"""

    relation_name: str = None

    def __init__(self, charm: ops.charm.CharmBase, relation_name: str):
        super().__init__(charm, relation_name)
        self.relation_name = relation_name

    def publish_info(self, hostname: str, port: int = 9091):
        if self.framework.model.unit.is_leader():
            for relation in self.framework.model.relations[self.relation_name]:
                relation.data[self.framework.model.app]["hostname"] = hostname
                relation.data[self.framework.model.app]["port"] = str(port)


class PrometheusClient(ops.framework.Object):
    """Requires side of a Prometheus Endpoint"""

    on = PrometheusClientEvents()
    relation_name: str = None

    def __init__(self, charm: ops.charm.CharmBase, relation_name: str):
        super().__init__(charm, relation_name)

        self.relation = self.framework.model.get_relation(relation_name)

        self.framework.observe(
            charm.on[relation_name].relation_changed, self._on_changed
        )
        self.framework.observe(charm.on[relation_name].relation_broken, self._on_broken)

    def _get_remote_app_data(self, entities: list):
        for entity in entities:
            if isinstance(entity, Application) and self.framework.model.app != entity:
                return entity

    @property
    def hostname(self):
        if self.relation:
            remote_app = self._get_remote_app_data(self.relation.data.keys())
            reldata = self.relation.data.get(remote_app, {})
            return reldata.get("hostname", None)

    @property
    def port(self):
        if self.relation:
            remote_app = self._get_remote_app_data(self.relation.data.keys())
            reldata = self.relation.data.get(remote_app, {})
            return int(reldata.get("port", 9090))

    def _on_changed(self, event: ops.charm.RelationEvent) -> None:
        if event.app is None:
            return  # Ignore unit relation data events.
        self.on.changed.emit()

    def _on_broken(self, event: ops.charm.RelationEvent) -> None:
        self.on.changed.emit()
