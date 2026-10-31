from collections import defaultdict
from sqlalchemy.orm import Session
import models
from decimal import Decimal

def simplify_debts(raw_transactions, user_map):
    net_balances=defaultdict(Decimal)

    for t in raw_transactions:
        net_balances[t["borrower_id"]]-=t["amount"]
        net_balances[t["payer_id"]]+=t["amount"]

    debtors=[]
    creditors=[]

    for user_id, balance in net_balances.items():
        if balance< 0:
            debtors.append([user_id, -balance])
        elif balance >0:
            creditors.append([user_id, balance])
    
    debtors.sort(key=lambda x:x[1], reverse=True)
    creditors.sort(key=lambda x:x[1], reverse=True)

    simplified=[]
    i,j=0,0

    while i<len(debtors) and j<len(creditors):
        debtor_id, debt_amount= debtors[i]
        creditor_id, credit_amount=creditors[j]

        settle_amount=min(debt_amount, credit_amount)

        borrower_name=user_map.get(debtor_id, f"User {debtor_id}")
        payer_name= user_map.get(creditor_id, f"User {creditor_id}")


        simplified.append({
            "borrower_id":debtor_id,
            "payer_id":creditor_id,
            "amount":settle_amount,
            "message": f"{borrower_name} owes {payer_name} Rs{settle_amount}"
        })

        debtors[i][1] -=settle_amount
        creditors[j][1] -=settle_amount

        if debtors[i][1]==0: i+=1
        if creditors[j][1]==0: j+=1

    return simplified


def fetch_and_calculate_balances(group_id: int, db:Session):
    expenses= db.query(models.Expense).filter(models.Expense.group_id==group_id).all()

    raw_transactions=[]
    involved_user_ids=set()

    for expense in expenses:
        for split in expense.splits:
            if split.user_id!=expense.payer_id:
                raw_transactions.append({
                    "borrower_id": split.user_id,
                    "payer_id": expense.payer_id,
                    "amount":split.amount_owed
                })
                involved_user_ids.add(split.user_id)
                involved_user_ids.add(expense.payer_id)

    if not involved_user_ids:
        return []

    users=db.query(models.User).filter(models.User.id.in_(involved_user_ids)).all()
    user_names={user.id: user.name for user in users}

    return simplify_debts(raw_transactions, user_names)