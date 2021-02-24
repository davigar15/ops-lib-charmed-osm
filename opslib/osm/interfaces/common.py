import ops.framework
import ops.charm


class BaseRelationClient(ops.framework.Object):
    """Requires side of a Kafka Endpoint"""

    def __init__(
        self,
        charm: ops.charm.CharmBase,
        relation_name: str,
        mandatory_fields: list,
    ):
        super().__init__(charm, relation_name)
        self.relation_name = relation_name
        self.mandatory_fields = mandatory_fields
        self._update_relation()

    def get_data_from_unit(self, key: str):
        if not self.relation:
            # This update relation doesn't seem to be needed, but I added it because apparently
            # the data is empty in the unit tests. In reality, the constructor is called in every hook.
            # In the unit tests when doing an update_relation_data, apparently it is not called.
            self._update_relation()
        if self.relation:
            for unit in self.relation.units:
                data = self.relation.data[unit].get(key)
                if data:
                    return data

    def is_missing_data(self):
        return not all(
            [self.get_data_from_unit(field) for field in self.mandatory_fields]
        )

    def _update_relation(self):
        self.relation = self.framework.model.get_relation(self.relation_name)
