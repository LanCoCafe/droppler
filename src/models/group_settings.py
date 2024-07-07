from src.models.mongo_object import MongoObject


class GroupSettings(MongoObject):
    collection_name = "group_settings"

    def __init__(self, api, database, group_id: str, allowed_tags: list[int]):
        super().__init__(api, database)

        self.group_id: str = group_id
        self.allowed_tags: list[int] = allowed_tags

    def unique_identifier(self):
        return {"group_id": self.group_id}

    def to_dict(self):
        return {
            "group_id": self.group_id,
            "allowed_tags": self.allowed_tags
        }

    @classmethod
    def from_dict(cls, api, database, data):
        return cls(
            api=api,
            database=database,
            group_id=data["group_id"],
            allowed_tags=data["allowed_tags"]
        )
