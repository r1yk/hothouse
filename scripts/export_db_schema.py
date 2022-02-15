import os
from dotenv import dotenv_values

config = dotenv_values()

export_schema_command = \
    f"pg_dump -d {config.get('DB_NAME')} -U {config.get('PG_USER')} " \
    f"--schema-only > db_schema_export.sql"
print(export_schema_command)

os.system(export_schema_command)
