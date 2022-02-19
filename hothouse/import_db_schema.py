import os
from dotenv import dotenv_values

config = dotenv_values()

os.environ['PGPASSWORD'] = config.get('PG_PASSWORD')


def import_schema(db_name: str):
    this_directory = os.path.dirname(os.path.realpath(__file__))
    import_file = f"{this_directory}/create_hothouse_db_schema.psql"
    import_schema_command = \
        f"psql -U {config.get('PG_USERNAME')} -d {db_name} " \
        f"-c \"\i {import_file}\""
    print(import_schema_command)

    os.system(import_schema_command)


if __name__ == "__main__":
    import_schema(config.get('DB_NAME'))
