import datetime
import yaml
#  import json
from yaml_schema import *
from colorize import tokenize


person = {
    "firstName": "John",
    "dateOfBirth": datetime.date(1996, 3, 14),
    "married": False,
    "spouse": None,
    "children": ["Bobby", "Molly"],
}

# print(json.dumps(person, indent=2, default=str))
result = load(yaml.dump(person, allow_unicode=True), schema)
# print(result.as_yaml())


# print(yaml.safe_load(
#     """
#     Shipping Address: &shipping |
#         111 College Ave
#         Palo Alto
#         CA 94306
#         USA
#     Invoice Address : *shipping
#     """))

# Tokenize a YAML document
for token in tokenize(yaml.dump(person), yaml.SafeLoader):
    print(token)
    # print(token.start_mark)
    # print(token.end_mark)
