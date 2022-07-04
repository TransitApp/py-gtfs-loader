from collections import namedtuple
from enum import IntEnum

Field = namedtuple('Field', ('type', 'required', 'default'))


class FileType(IntEnum):
    CSV = 0
    GEOJSON = 1


class Schema:
    def __init__(self, required=True, group_id=None, inner_dict=False):
        # If this file is absent from the GTFS directory, should process abort?
        self.required = required

        # If set, multiple entities may share the same ID. The group key is used to provide a deterministic order among
        # such entities
        self.group_id = group_id

        # If true, then the group key should be a dictionary key at the second level
        self.inner_dict = inner_dict

        # Will be set to point to the class defining this file
        self.class_def = None

    def get_declared_fields(self):
        return {
            k: Field(type=v,
                     required=k not in self.class_def.__dict__,
                     default=self.class_def.__dict__.get(k))
            for k, v in self.class_def.__annotations__.items()
        }


class File(Schema):

    def __init__(self,
                 id,
                 name,
                 fileType,
                 filename=None,
                 required=True,
                 group_id=None,
                 inner_dict=False):

        super().__init__(required, group_id, inner_dict)
        # Primary key for this file, serves as the key of the generated dict
        self.id = id

        # Objects will appear under gtfs."name"
        self.name = name

        # Specify if the file is a csv or a json
        self.fileType = fileType

        # Objects will be read from "filename".txt
        # If unset, the entity name shall be used instead
        self.filename = filename if filename else name + \
            File._get_file_ext(fileType)

    @staticmethod
    def _get_file_ext(fileType):
        if fileType is FileType.CSV:
            return ".txt"

        if fileType is FileType.GEOJSON:
            return ".geojson"


class FileCollection:

    def __init__(self, *args):
        self.entities = {}
        for file in args:
            file._schema.class_def = file
            self.entities[file._schema.filename] = file._schema

    def keys(self):
        return self.entities.keys()

    def values(self):
        return self.entities.values()

    def __getitem__(self, item):
        return self.entities[item]


class SchemaCollection:

    def __init__(self, *args):
        for file in args:
            file._schema.class_def = file
