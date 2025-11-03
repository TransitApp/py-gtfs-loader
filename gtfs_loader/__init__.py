import csv
import enum
import json
import os
import shutil
import typing
from pathlib import Path
from . import schema_classes, types, schema


class ParseError(ValueError):
    pass

def get_files(files):
    return schema.FileCollection(*(schema.GTFS_FILENAMES[f] for f in files)).values()


def load(gtfs_dir, sorted_read=False, files=None, verbose=True, itineraries=False):
    gtfs_dir = Path(gtfs_dir)
    gtfs = types.Entity()

    files_to_load = get_files(files) if files else schema.GTFS_SUBSET_SCHEMA_ITINERARIES.values() if itineraries else schema.GTFS_SUBSET_SCHEMA.values()

    for file_schema in files_to_load:
        if verbose:
            print(f'Loading {file_schema.name}')
        filepath = gtfs_dir / file_schema.filename
        gtfs[file_schema.name] = types.EntityDict(
            file_schema.get_declared_fields())

        if not filepath.exists():
            if file_schema.required:
                raise ParseError(
                    f'{file_schema.filename}: required file is missing')
            else:
                continue

        if file_schema.fileType is schema_classes.FileType.CSV:
            load_csv(gtfs, filepath, file_schema, sorted_read=(True if file_schema.name == 'stop_times' or file_schema.name == 'shapes' else sorted_read))
        elif file_schema.fileType is schema_classes.FileType.GEOJSON:
            load_json(gtfs, filepath, file_schema)

    return gtfs


def load_csv(gtfs, filepath, file_schema, sorted_read=False):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f, skipinitialspace=True)
        header_row = next(reader, None)
        if not header_row:
            if file_schema.required:
                raise ParseError(
                    f'{file_schema.filename}: required file is empty')
            else:
                return

        resolved_fields = merge_header_and_declared_fields(
            file_schema, header_row)
        entities = {}
        for entity in parse_rows(gtfs, file_schema, resolved_fields,
                                 header_row, reader):
            index_entity(file_schema, entities, entity)

        if sorted_read:
            processed_entities = sorted_entities(file_schema, entities)
        else:
            processed_entities = entities.items()

        gtfs[file_schema.name] = types.EntityDict(fields=resolved_fields,
                                                  values=processed_entities)


def load_json(gtfs, filepath, file_schema):
    with open(filepath, 'r', encoding='utf-8-sig') as f:
        json_data = json.load(f)

        gtfs[file_schema.name] = visit_json(json_data, file_schema.class_def())


def visit_json(json_data, expected_type, type_config=None):
    if isinstance(json_data, dict):
        file_schema = expected_type._schema
        declared_fields = file_schema.get_declared_fields()
        output = file_schema.class_def()

        for name, config in declared_fields.items():
            value = json_data.get(name, None)

            if config.required and value is None:
                raise ParseError(
                    f'{expected_type.__name__} missing required field {name}')

            output[name] = visit_json(value, config.type, config)

        return output
    elif isinstance(json_data, list):
        output = []
        for value in json_data:
            inner_type = get_inner_type(expected_type)
            output.append(visit_json(value, inner_type))

        return output
    else:
        if type_config is not None and not type_config.required and json_data == None:
            return type_config.default

        if expected_type is typing.Any:
            return json_data

        return expected_type(json_data)


def merge_header_and_declared_fields(file_schema, header_row):
    declared_fields = file_schema.get_declared_fields()
    fields = {}

    for name in header_row:
        fields[name] = declared_fields.get(name) or schema_classes.Field(
            str, False, '')

    for name, config in declared_fields.items():
        if config.required and name not in fields:
            raise ParseError(
                f'{file_schema.filename}:1: missing required field {name}')

        fields.setdefault(name, config)

    return fields


def parse_rows(gtfs, file_schema, fields, header_row, reader):
    for lineno, row in enumerate(reader, 2):
        if len(row) == 0:
            continue  # empty row, just skip it

        entity = file_schema.class_def()
        entity._gtfs = gtfs

        for name, value in zip(header_row, row):
            config = fields[name]
            if config.required and not value:
                raise ParseError(
                    f'{file_schema.filename}:{lineno}: required field {name} is empty'
                )

            entity[name] = validate(
                config,
                value,
                context_fn=lambda:
                f'{file_schema.filename}:{lineno} field {name} = {repr(value)}')

        yield entity


def validate(config, value, context_fn):
    try:
        return convert(config, value)
    except Exception as exc:
        raise ParseError(f'{context_fn()}: {exc.args[0]}') from None


def convert(config, value):
    if not config.required and value == '':
        return config.default

    # Lists are stringified as JSON in csv.
    if typing.get_origin(config.type) is list:
        return list(json.loads(value))
    
    config_type = get_inner_type(config.type)
    if issubclass(config_type, enum.IntEnum):
        return config_type(int(value))

    if config_type is bool:
        return bool(int(value))

    return config_type(value)


def get_inner_type(config_type):
    if typing.get_origin(config_type) is list:
        return typing.get_args(config_type)[0]

    if typing.get_origin(config_type) is not typing.Union:
        return config_type

    variants = typing.get_args(config_type)
    if len(variants) != 2:
        raise ValueError("Misconfigured type definition")

    for variant in variants:
        if not isinstance(None, variant):
            return variant

    raise ValueError("Misconfigured type definition")


def index_entity(file_schema, entities, entity):
    key = entity[file_schema.id]
    if not file_schema.group_id:
        entities[key] = entity
        return

    group_key = entity[file_schema.group_id]
    if file_schema.inner_dict:
        entities.setdefault(key, {})[group_key] = entity
    else:
        entities.setdefault(key, []).append(entity)


def sorted_entities(file_schema, entities):
    if file_schema.group_id:
        if file_schema.inner_dict:
            for group_key, group in entities.items():
                entities[group_key] = dict(
                    sorted(group.items(), key=lambda kv: kv[0]))
        else:
            for group in entities.values():
                group.sort(key=lambda entity: entity[file_schema.group_id])

    return sorted(entities.items(), key=lambda kv: kv[0])


def patch(gtfs, gtfs_in_dir, gtfs_out_dir, files=None, sorted_output=False, verbose=True, itineraries=False):
    gtfs_in_dir = Path(gtfs_in_dir)
    gtfs_out_dir = Path(gtfs_out_dir)
    gtfs_out_dir.mkdir(parents=True, exist_ok=True)

    for original_filename in gtfs_in_dir.iterdir():
        try:
            shutil.copy2(original_filename,
                         gtfs_out_dir / original_filename.name)
        except shutil.SameFileError:
            pass  # No need to copy if we're working in-place

    files_to_patch = get_files(files) if files else schema.GTFS_SUBSET_SCHEMA_ITINERARIES.values() if itineraries else schema.GTFS_SUBSET_SCHEMA.values()

    for file_schema in files_to_patch:
        if verbose:
            print(f'Writing {file_schema.name}')
        entities = gtfs.get(file_schema.name)
        if not entities:
            (gtfs_out_dir / file_schema.filename).unlink(missing_ok=True)
            continue

        if file_schema.fileType is schema_classes.FileType.CSV:
            save_csv(file_schema, entities, gtfs_out_dir, sorted_output)
        elif file_schema.fileType is schema_classes.FileType.GEOJSON:
            save_json(file_schema, entities, gtfs_out_dir)


def save_csv(file_schema, entities, gtfs_out_dir, sorted_output=False):
    if sorted_output:
        processed_entities = dict(sorted_entities(file_schema, entities))
    else:
        processed_entities = entities.copy()

    flat_entities = flatten_entities(file_schema, processed_entities)
    fields = entities._resolved_fields

    with open(gtfs_out_dir / (file_schema.filename), 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(fields.keys())
        for entity in flat_entities:
            writer.writerow(
                types.serialize(entity.get(name, '')) for name in fields)


def save_json(file_schema, entities, gtfs_out_dir):
    with open(gtfs_out_dir / (file_schema.filename), 'w', encoding='utf-8') as f:
        f.write(json.dumps(entities, indent=4, default=vars))


def flatten_entities(file_schema, entities):
    if file_schema.group_id:
        flat_entities = []
        for entity_list in entities.values():
            flat_entities.extend(
                entity_list.values() if file_schema.inner_dict else entity_list)
        return flat_entities
    else:
        return entities.values()


def clone(entities, key, new_key):
    if key not in entities:
        return

    entries = entities[key]
    if isinstance(entries, list):
        entities[new_key] = [
            clone_and_index(entity, new_key) for entity in entries
        ]
    else:
        entities[new_key] = clone_and_index(entries, new_key)

    return entities[new_key]


def clone_and_index(entity, new_key):
    field_schema = entity.__class__._schema
    new_entity = entity.clone()
    new_entity[field_schema.id] = new_key
    return new_entity
