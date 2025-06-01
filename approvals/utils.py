from decimal import Decimal, getcontext

getcontext().prec = 10  # set precision as needed

def calculate_emi(principal: Decimal, rate: Decimal, tenure: int) -> Decimal:
    monthly_rate = rate / Decimal('1200')  # Convert annual rate % to monthly decimal
    one = Decimal('1')
    power = (one + monthly_rate) ** tenure
    emi = (principal * monthly_rate * power) / (power - one)
    return emi
