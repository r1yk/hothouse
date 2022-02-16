import os
from dotenv import dotenv_values

config = dotenv_values()

os.environ['PGPASSWORD'] = config.get('PG_PASSWORD')


def import_schema(db_name: str):
    import_schema_command = \
        f"psql -U {config.get('PG_USERNAME')} -d {db_name} " \
        "-c \"\i db_schema_export.sql\""
    print(import_schema_command)

    os.system(import_schema_command)


if __name__ == "__main__":
    import_schema(config.get('DB_NAME'))
