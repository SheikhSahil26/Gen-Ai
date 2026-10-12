from ecommerce_ai.models.base import Base

print("Before importing models:")
print(Base.metadata.tables)

from ecommerce_ai import models

print("\nAfter importing ecommerce_ai.models:")
print(Base.metadata.tables)

print("\nRegistered tables:")

if not Base.metadata.tables:
    print("NO TABLES REGISTERED")

else:
    for table_name, table in Base.metadata.tables.items():
        print(f"- {table_name}")