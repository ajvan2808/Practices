import datetime
import os


def _get_time():
    return datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")


def _create_account_value(**kwargs):
    return {
        "id": kwargs.get("account_id"),
        "product_version_id": kwargs.get("product_version_id", '1'),
        "instance_param_vals": kwargs.get("instance_param_vals", {})
    }


def _create_posting_instruction_batch(**kwargs):
    return {
            "timestamp": "2022-06-10T17:00:00Z",
            "create_posting_instruction_batch": {
                "client_id": "7576182f-7f0a-4fb3-a8ce-63d9fcd686bd",
                "client_batch_id": "54ca95ac-21a0-4686-83c5-a435abd92325",
                "posting_instructions": [
                    {
                        "client_transaction_id": "063645ac-9c81-4873-b3f3-44c88f2fb4d2",
                        "instruction_details": {
                            "type": "SAVING"
                        },
                        "custom_instruction": {
                            "postings": [
                                {
                                    "credit": True,
                                    "amount": "1000",
                                    "denomination": "VND",
                                    "account_id": "BankAccount",
                                    "account_address": "DEFAULT",
                                    "asset": "COMMERCIAL_BANK_MONEY",
                                    "phase": "POSTING_PHASE_COMMITTED"
                                },
                                {
                                    "credit": False,
                                    "amount": "1000",
                                    "denomination": "VND",
                                    "account_id": "CasaAccount",
                                    "account_address": "DEFAULT",
                                    "asset": "COMMERCIAL_BANK_MONEY",
                                    "phase": "POSTING_PHASE_COMMITTED"
                                }
                            ]
                        }
                    }
                ]
            }
    }
