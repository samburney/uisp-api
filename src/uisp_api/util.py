import collections.abc
import configargparse

from pathlib import Path


class Util:
    @property
    def project_root(self):
        '''
        Define the project_root directory.  Used as the default location to
        look for config.yaml and cache folder.
        '''
        script_path = Path(__file__).resolve()
        project_root = script_path.parents[2]

        return project_root

    # Define config as provided by config.yaml
    @property
    def config(self):
        config = self.parse_config()

        # Defined empty webapp dict
        if not hasattr(config, 'webapp'):
            config.webapp = {}

        return config

    @staticmethod
    def is_hashable(obj):
        return isinstance(obj, collections.abc.Hashable)

    @staticmethod
    def find_hashable_columns(df):
        hashable_columns = []

        # Find columns with 'unhashable' types
        for column in df.columns:
            # Check first 15 rows
            rows = 15 if len(df) > 15 else len(df)

            for row in range(0, rows):
                if Util.is_hashable(df.iloc[row][column]) is False:
                    hashable_columns.append(column)

                    break

        return hashable_columns

    @staticmethod
    def get_default_value(sub_schema):
        '''
        Gets the default value based on the schema type or other keywords.
        '''
        if 'default' in sub_schema:
            return sub_schema['default']

        # Handle anyOf by using the first schema definition
        if 'anyOf' in sub_schema and sub_schema['anyOf']:
            return Util.get_default_value(sub_schema['anyOf'][0])

        schema_type = sub_schema.get('type')

        # Infer type from enum if 'type' is missing and enum is present
        if not schema_type and 'enum' in sub_schema and sub_schema['enum']:
            first_enum_value = sub_schema['enum'][0]
            if isinstance(first_enum_value, str):
                schema_type = 'string'
            elif isinstance(first_enum_value, bool):
                schema_type = 'boolean'
            elif isinstance(first_enum_value, int):
                schema_type = 'integer'
            elif isinstance(first_enum_value, float):
                schema_type = 'number'
            elif first_enum_value is None:
                schema_type = 'null'

        if schema_type == 'object':
            return Util.generate_skeleton(sub_schema)
        elif schema_type == 'array':
            # Could potentially generate default item based on 'items' schema
            # For a simple skeleton, an empty list is usually sufficient.
            return []
        elif schema_type == 'string':
            return ""
        elif schema_type == 'number':
            return 0.0
        elif schema_type == 'integer':
            return 0
        elif schema_type == 'boolean':
            return False
        elif schema_type == 'null':
            return None
        else:
            # Default for unknown or missing type (could also return None)
            # Or if 'properties' exists without 'type', assume 'object'
            if 'properties' in sub_schema:
                return Util.generate_skeleton(sub_schema)
            # Otherwise, use None as a sensible default
            return None

    @staticmethod
    def generate_skeleton(schema_node):
        '''
        Recursively generates a Python dictionary skeleton from a JSON schema.
        '''
        skeleton = {}
        schema_type = schema_node.get('type')

        if schema_type != 'object' and 'properties' not in schema_node:
            # If the root node itself is not an object, return its default value
            return Util.get_default_value(schema_node)

        # Iterate through properties if they exist
        if 'properties' in schema_node:
            for key, prop_schema in schema_node['properties'].items():
                skeleton[key] = Util.get_default_value(prop_schema)

        return skeleton

    def parse_config(self):
        '''
        Parse configuration from its various sources.
        '''
        parser = configargparse.ArgumentParser(
            default_config_files=[
                Path(self.project_root, 'config.yml'),
                Path(self.project_root, 'config.yaml'),
            ]
        )

        parser.add_argument('-c', '--config', env_var='UISP_API_CONFIG_FILE',
                            is_config_file=True, help='Path to config.yaml')
        parser.add_argument('--cache-debug', env_var='UISP_API_CACHE_DEBUG', default=False,
                            help='Enable cache helper debugging')
        parser.add_argument('--cache-type', default='FileSystemCache', env_var='UISP_API_CACHE_TYPE',
                            help='Cache provider module')
        parser.add_argument('--cache-dir', default=Path(self.project_root, 'cache'), env_var='UISP_API_CACHE_DIR',
                            help='Location of cache directory when using cache-type `FileSystemCache`')

        return parser.parse_args()
