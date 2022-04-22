import json

import requests
from smart_contracts import helper
import datetime


url = 'https://core-api-demo.grasshopper.tmachine.io/v1/contracts:simulate'
token = 'A0008935689275482795593!s/riPgVaFR9UFIlU5pbhlanSx7J5FyYAnEYKvaX9Q2M998HBKpZJKNlVHwKcVLyR8idbVw+KPxiuZroptfYGvbH1aHY='
headers = {
    "X-Auth-Token": token,
    "Content-Type": "application/json"
}
dt = datetime.datetime.utcnow()
end_time = (dt + datetime.timedelta(days=367)).strftime("%Y-%m-%dT%H:%M:%SZ")
instructions = []


with open('smart_contracts/sm_saving.py', 'r') as f:
    sc_saving = f.read()

sc_code = [
    {
        "code": sc_saving,
        "smart_contract_param_vals": {
            "interest_accrual_days_in_year": "365",
        },
        "smart_contract_version_id": "1",
    }
]

account_create = {
    "timestamp": helper._get_time(),
    "create_account": helper._create_account_value(account_id='SavingAccount',
                                                   product_version_id='1',
                                                   instance_param_vals={},
                                                   )
}
instructions.append(account_create)


with requests.post(url, data=json.dumps({
    "start_timestamp": dt.strftime('%Y-%m-%dT%H:%M:%SZ'),
    "end_timestamp": end_time,
    "smart_contracts": sc_code,
    "supervisor_contracts": [],
    "instructions": instructions
}, indent=2), headers=headers, stream=True) as simulate:
    with open("request.json", "w") as request_file:
        request_file.write(simulate.request.body)

    with open("response.json", "w") as rp_file:
        for line in simulate.iter_lines(decode_unicode=True):
            resp_dict = json.loads(line)
            json.dump(resp_dict, rp_file, indent=2, sort_keys=True)
        print(line)
