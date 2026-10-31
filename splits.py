from decimal import Decimal

PAISE= Decimal("0.01")

def to_paise(amount:Decimal) -> int:
    return int(amount*100)

def from_paise(paise:int)-> Decimal:
    return (Decimal(paise)/100).quantize(PAISE)


def split_equal(total:Decimal, n:int)-> list[Decimal]:
    """Shares differ by at most 1 paisa and sum exactly to total."""
    base, remainder= divmod(to_paise(total),n)
    return [from_paise(base+(1 if i<remainder else 0)) for i in range(n)]

def split_percent(total:Decimal, percents:list[Decimal])-> list[Decimal]:
    """Leftover paise to go the shares with the largest fractional parts"""

    total_paise=to_paise(total)
    raw=[total_paise*p/100 for p in percents]
    shares=[int(r) for r in raw]
    leftover=total_paise-sum(shares)

    by_fraction= sorted(range(len(raw)), key=lambda i:raw[i]-shares[i], reverse=True)
    for i in by_fraction[:leftover]:
        shares[i]+=1

    return [from_paise(s) for s in shares]
