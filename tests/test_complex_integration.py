import pytest
from src.manager import Manager
from src.models import Bill, Parameters

def test_get_apartment_costs():
    parameters = Parameters()
    manager = Manager(parameters)

    # przykladowe obiekty
    manager.bills = [
        Bill(
            amount_pln=760.00,
            date_due="2025-02-15",
            settlement_year=2025,
            settlement_month=1,
            apartment="apart-polanka",
            type="rent"
        ),
        Bill(
            amount_pln=150.00,
            date_due="2025-02-12",
            settlement_year=2025,
            settlement_month=1,
            apartment="apart-polanka",
            type="electricity"
        ),
    ]

    # 1. Mieszkanie istnieje i ma rachunki w tym miesiącu
    assert manager.get_apartment_costs('apart-polanka', 2025, 1) == 910.0

    # 2. Mieszkanie istnieje rok się zgadza ale w tym miesiącu nie ma rachunków
    assert manager.get_apartment_costs('apart-polanka', 2025, 2) == 0.0

    # 3. Mieszkanie nie istnieje - wyjątek KeyError
    with pytest.raises(KeyError):
        manager.get_apartment_costs('invalid-key', 2025, 1)


def test_apartment_costs_with_optional_parameters():
    manager = Manager(Parameters())
    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2025-03-15',
        settlement_year=2025,
        settlement_month=2,
        amount_pln=1250.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-03-15',
        settlement_year=2024,
        settlement_month=2,
        amount_pln=1150.0,
        type='rent'
    ))

    manager.bills.append(Bill(
        apartment='apart-polanka',
        date_due='2024-02-02',
        settlement_year=2024,
        settlement_month=1,
        amount_pln=222.0,
        type='electricity'
    ))

    with pytest.raises(KeyError):
        manager.get_apartment_costs('apartment-1', 2024, 1)

    costs = manager.get_apartment_costs('apart-polanka', 2024, 3)
    assert costs == 0.0

    costs = manager.get_apartment_costs('apart-polanka', 2024, 1)
    assert costs == 222.0

    costs = manager.get_apartment_costs('apart-polanka', 2025, 1)
    assert costs == 910.0
    
    costs = manager.get_apartment_costs('apart-polanka', 2024)
    assert costs == 1372.0

    costs = manager.get_apartment_costs('apart-polanka')
    assert costs == 3532.0