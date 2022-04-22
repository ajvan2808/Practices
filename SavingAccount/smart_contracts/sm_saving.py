api = "3.9.0"
version = "1.0.0"
display_name = "Saving Account Demo"
summary = "Saving account demo - Practice with Ops smart contract version"
tside = Tside.LIABILITY
denomination = "USD"
internal_account = "1"

ACCRUED_INTEREST_PAYABLE = "ACCRUED_INTEREST_PAYABLE"
ACCRUED_INTEREST_RECEIVABLE = "ACCRUED_INTEREST_RECEIVABLE"

global_parameters = [
    "sa_interest_rate",
    "sa_penalty_interest_rate",
    "sa_cash_ops_fee",
]

supported_denomination = ["USD"]
event_types = [
    EventType(
        name="ACCRUE_INTEREST",
        scheduler_tag_ids=["SAVING_ACCOUNT_ACCRUE_INTEREST"]
    ),
    EventType(
        name="APPLY_ACCRUED_INTEREST",
        scheduler_tag_ids=["SAVING_ACCOUNT_APPLY_DEPOSIT_INTEREST"]
    ),
    EventType(
        name="APPLY_ACCRUED_PENALTY_INTEREST",
        scheduler_tag_ids=["SAVING_ACCOUNT_APPLY_ACCRUED_PENALTY_INTEREST"]
    ),
]

parameters = [
    Parameter(
        name="interest_accrual_days_in_year",
        shape=UnionShape(
            UnionItem(key="actual", display_name="Actual"),
            UnionItem(key="365", display_name="365"),
            UnionItem(key="360", display_name="360")
        ),
        level=Level.TEMPLATE,
        description="The days in the year for interest accrual calculation."
                    ' Valid values are "actual", "365", "360"',
        display_name="Interest accrual days in year",
        default_value=UnionItemValue(key="actual")
    )
]


@requires(parameters=False)
def execution_schedules():
    return [
        (
            'ACCRUE_INTEREST', {
                'hour': '23',
                'minute': '59',
                'second': '59',
            }
        ),
        (
            'APPLY_ACCRUED_INTEREST', {
                'day': '1',
                'hour': '1',
                'minute': '0',
                'second': '0',
            }
        ),
        (
            'APPLY_ACCRUED_PENALTY_INTEREST', {
                'day': '1',
                'hour': '1',
                'minute': '0',
                'second': '0',
            }
        ),
    ]


@requires(event_type='ACCRUE_INTEREST', parameters=True, balances='1 day')
@requires(event_type='APPLY_ACCRUED_INTEREST', parameters=True, balances='1 day')
@requires(event_type='APPLY_ACCRUED_PENALTY_INTEREST', parameters=True, balances='1 day')
def scheduled_code(event_type, effective_date):
    if event_type == 'ACCRUE_INTEREST':
        _accrued_interest(vault, effective_date)
    elif event_type == 'APPLY_ACCRUED_INTEREST':
        _apply_accrued_interest(vault, effective_date)
    elif event_type == 'APPLY_ACCRUED_PENALTY_INTEREST':
        _apply_accrued_penalty_fee(vault, effective_date, penalty=True)


# Get the value of the latest balance when we receive the posting
@requires(parameters=True, balances="latest live", postings="1 day")
def pre_posting_code(postings, effective_date):
    if any(post.denomination != denomination for post in postings):
        raise Rejected("Cannot make transactions in given denomination; "
                       f"transactions must be in {denomination}",
                       reason_code=RejectedReason.WRONG_DENOMINATION,)

    balances = vault.get_balance_timeseries().latest()
    available_balance = _get_balancce(balances, denomination)
    for post in postings:
        amount = post.amount
        if post.instruction_details.get("ops_type") == "CASH":
            amount += _calculate_cash_ops_fee(vault, amount)
        if (
                not post.credit
                and amount > available_balance
                and post.instruction_details.get("ops_type") != "INTEREST"
        ):
            raise Rejected("Insufficient fund for transaction.",
                           reason_code=RejectedReason.INSUFFICIENT_FUNDS,)


@requires(parameters=True, balances='latest live', postings='1 day')
def post_posting_code(postings, effective_date):
    for post in postings:
        if post.instruction_details.get("ops_type") == 'CASH':
            _apply_cash_ops_fee(vault, effective_date, post.amount)


def _apply_cash_ops_fee(vault, effective_date, amount):
    ops_fee = _calculate_cash_ops_fee(vault, amount)
    if ops_fee:
        instructions = vault.make_internal_transfer_instructions(
            amount=ops_fee,
            denomination=denomination,
            from_account_id=vault.account_id,
            from_account_address=DEFAULT_ADDRESS,
            to_account_id=internal_account,
            to_account_address=DEFAULT_ADDRESS,
            asset=DEFAULT_ASSET,
            client_transaction_id='CASH_OPS_FEE_{}'.format(
                vault.get_hook_execution_id()
            ),
            instruction_details={
                'description': 'Cash operation fee charged'
            },
            pics=[],
        )
        vault.instruct_posting_batch(
            posting_instructions=instructions,
            effective_date=effective_date,
            client_batch_id='BATCH_{}_CASH_OPS_FEE'.format(
                vault.get_hook_execution_id()
            )
        )


def _calculate_cash_ops_fee(vault, amount):
    ops_fee_rate = ault.get_parameter_timeseries(name='sa_cash_ops_fee').latest()
    return _precision_fulfilment(ops_fee_rate * amount) if ops_fee_rate > 0 else Decimal('0')


def _get_balance(balances, denomination, address=DEFAULT_ADDRESS, asset=DEFAULT_ASSET):
    return (
        balances[(address, asset, denomination, Phase.COMMITED)].net
        + balances[(address, asset, denomination, Phase.PENDING_OUT)].net
    )


def _accrue_interest(vault, effective_date):
    balances = vault.get_balance_timeseries().at(timestamp=effective_date)
    effective_balance = balances[(DEFAULT_ADDRESS, DEFAULT_ASSET, denomination, Phase.COMMITED)].net
    if effective_balance >= 0:
        interest_rate = vault.get_parameter_timeseries(name='sa_interest_rate').at(timestamp=effective_date)
        days_in_year = _get_parameter(name='interest_accrual_days_in_year', vault=vault).key
        daily_rate = _yearly_to_daily_rate(days_in_year, effective_date.year, interest_rate)
        daily_rate_percent = daily_rate * 100
        amount_to_accrue = _precision_accrual(effective_balance * daily_rate)
        from_account_id = internal_account
        from_account_address = DEFAULT_ADDRESS
        to_account_id = vault.account_id
        to_account_address = ACCRUED_INTEREST_PAYABLE
    else:
        interest_rate = vault.get_parameter_timeseries(name='sa_penalty_interest_rate').at(timestamp=effective_date)
        daily_rate = _yearly_to_daily_rate("actual", interest_rate, effective_date.year)
        daily_rate_percent = daily_rate * 100
        amount_to_accrue = _precision_accrual(abs(effective_balance * daily_rate))
        from_account_id = vault.account_id
        from_account_address = ACCRUED_INTEREST_RECEIVABLE
        to_account_id = internal_account
        to_account_address = DEFAULT_ADDRESS
    if amount_to_accrue > 0:
        posting_instruction = vault.make_internal_transfer_instructions(
            amount=amount_to_accrue,
            denomination=denomination,
            client_transaction_id=f"ACCRUE_INTEREST_{vault.get_hook_execution_id()}",
            from_account_id=from_account_id,
            from_account_address=from_account_address,
            to_account_id=to_account_id,
            to_account_address=to_account_address,
            instruction_details={
                'description': 'Daily interest accrued at %0.5f%% on balance of %0.2f' %(daily_rate_percent, effective_balance)
            },
            asset=DEFAULT_ASSET,
        )
        vault.instruct_posting_batch(
            posting_instructions=posting_instruction,
            effective_date=effective_date,
        )


def _apply_accrued_interest(vault, effective_date, penalty=False):
    latest_bal_by_address = vault.get_balance_timeseries().at(timestamp=effective_date)
    accrued_payable = latest_bal_by_address[(ACCRUED_INTEREST_PAYABLE, DEFAULT_ASSET, denomination, Phase.COMMITED)].net
    accrued_receivable = latest_bal_by_address[(ACCRUED_INTEREST_RECEIVABLE, DEFAULT_ASSET, denomination, Phase.COMMITED)].net
    amount_to_be_paid = _precision_fulfilment(accrued_payable)
    amount_to_be_charged = _precision_fulfilment(accrued_receivable)
    instructions = []
    if not penalty and amount_to_be_paid > Decimal("0.00"):
        instructions.extend(vault.make_internal_transfer_instructions(
            amount=amount_to_be_paid,
            denomination=denomination,
            from_account_id=vault.account_id,
            from_account_address=ACCRUED_INTEREST_PAYABLE,
            to_account_id=vault.account_id,
            to_account_address=DEFAULT_ADDRESS,
            asset=DEFAULT_ASSET,
            client_transaction_id=f"APPLY_ACCRUED_INTEREST_{vault.get_hook_execution_id()}",
            instruction_details={
                "description": "Accrued Interest Applied",
                "event": "APPLY_ACCRUED_INTEREST",
                "ops_type": "INTERESTS",
            }
        ))
        fulfilment_remainder = accrued_payable + amount_to_be_paid
        if fulfilment_remainder != 0:
            _clear_fractional_amount(vault, fulfilment_remainder, 'PAYABLE', instructions)

    elif penalty and amount_to_be_charged > Decimal("0.00"):
        instructions.extend(vault.make_internal_transfer_instructions(
            amount=amount_to_be_charged,
            denomination=denomination,
            from_account_id=vault.account_id,
            from_account_address=DEFAULT_ADDRESS,
            to_account_id=vault.account_id,
            to_account_address=ACCRUED_INTEREST_RECEIVABLE,
            asset=DEFAULT_ASSET,
            client_transaction_id=f"APPLY_ACCRUED_PENALTY_INTEREST_{vault.get_hook_execution_id()}",
            instruction_details={
                "description": "Accrued Penalty Interest Applied",
                "event": "APPLY__ACCRUED_PENALTY_INTEREST",
                "ops_type": "INTERESTS",
            }
        ))
        fulfilment_remainder = accrued_receivable + amount_to_be_charged
        if fulfilment_remainder != 0:
            _clear_fractional_amount(vault, fulfilment_remainder, 'RECEIVABLE', instructions)

    client_batch_prefix = "APPLY_ACCRUED_PENALTY_INTEREST" if penalty else "APPLY_ACCRUED_INTEREST"
    if instructions:
        vault.instruct_posting_batch(
            posting_instructions=instructions,
            effective_date=effective_date,
            client_batch_id=f"{client_batch_prefix}_{vault.get_hook_execution_id()}",
        )


def _clear_fractional_amount(vault, remainder_amount, remainder_type, instruction):
    if remainder_amount > 0:
        from_account_id = vault.account_id,
        from_account_address = f"ACCRUED_INTEREST_{remainder_type}",
        to_account_id = internal_account,
        to_account_address = DEFAULT_ADDRESS,

    elif remainder_amount < 0:
        from_account_id = internal_account,
        from_account_address = DEFAULT_ADDRESS
        to_account_id = vault.account_id,
        to_account_address = f"ACCRUED_INTEREST_{remainder_type}",

    if abs(remainder_amount) > 0:
        instruction.extend(
            vault.make_internal_transfer_instructions(
                amount=abs(remainder_amount),
                denomination=denomination,
                from_accoint_id=from_account_id,
                from_account_address=from_account_address,
                to_account_id=to_account_id,
                to_account_address=to_account_address,
                asset=DEFAULT_ASSET,
                client_transaction_id=f"CLEAR_RESIDUAL_FRACTIONAL_{remainder_type}_ACCRUAL_"
                                      f"AMOUNTS_{vault.get_hook_execution_id()}",
                instruction_details={
                    "description": f"Clear residual fractional amounts from "
                                   f"{remainder_type.lower()} accrual addresses due to rounding ",
                    "event": "APPLY_ACCRUED_INTEREST" if remainder_type == 'PAYABLE' else "APPLY_ACCRUED_PENALTY_INTEREST",
                },
            )
        )


def _yearly_to_daily_rate(days_in_year, year, yearly_rate):
    allowed_values = ['actual', '365', '360']
    if days_in_year in allowed_values:
        if days_in_year == 'actual':
            days_in_year = 366 if _is_leap_year(year) else 365
        else:
            days_in_year = Decimal(days_in_year)
        return yearly_rate / days_in_year


def _is_leap_year(year):
    if year % 400 == 0:
        return True
    elif year % 100 == 0:
        return False
    elif year % 4 == 0:
        return True
    else:
        return False


def _get_parameter(vault, name, at=None, is_json=False, optional=False, default_value=None):
    if at:
        parameter = vault.get_parameter_timeseries(name=name).at(timestamp=at)
    else:
        parameter = vault.get_parameter_timeseries(name=name).latest()
    if optional:
        parameter = parameter.value if parameter.is_set() else default_value
    if is_json:
        parameter = json_loads(parameter)
    return parameter


def _precision_accrual(amount):
    return amount.copy_abs().quantize(Decimal('.00001'), rounding=ROUND_HALF_UP)


def _precision_fulfilment(amount):
    return amount.copy_abs().quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
