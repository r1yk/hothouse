import os
from dotenv import dotenv_values

config = dotenv_values()

import_schema_command = \
    f"psql -U {config.get('PG_USERNAME')} -d {config.get('DB_NAME')} " \
    "-c \"\i db_schema_export.sql\""
print(import_schema_command)

os.system(import_schema_command)
