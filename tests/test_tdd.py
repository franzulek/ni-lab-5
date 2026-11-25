import pytest
from src.manager import Manager
from src.models import ApartmentSettlement, Bill, Parameters, Tenant

def test_create_apartment_settlement():
    manager = Manager(Parameters())

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

    # Scenariusz 1: Mieszkanie ma rachunki w danym miesiącu
    settlement_with_bills = manager.create_apartment_settlement("apart-polanka", 2025, 1)

    assert isinstance(settlement_with_bills, ApartmentSettlement)       # 1
    assert settlement_with_bills.apartment == "apart-polanka"           # 2
    assert settlement_with_bills.year == 2025                           # 3
    assert settlement_with_bills.month == 1                             # 4
    assert settlement_with_bills.total_rent_pln == 0.0                  # 5
    assert settlement_with_bills.total_bills_pln == 910.0               # 6
    assert settlement_with_bills.total_due_pln == -910.0                # 7

    # Scenariusz 2: Mieszkanie NIE ma rachunków w danym miesiącu
    settlement_no_bills = manager.create_apartment_settlement("apart-polanka", 2025, 6)

    assert isinstance(settlement_no_bills, ApartmentSettlement)         # 8
    assert settlement_no_bills.apartment == "apart-polanka"             # 9
    assert settlement_no_bills.total_rent_pln == 0.0                    # 10
    assert settlement_no_bills.total_bills_pln == 0.0                   # 11
    assert settlement_no_bills.total_due_pln == 0.0                     # 12

    # Scenariusz 3: Nieistniejące mieszkanie 
    with pytest.raises(KeyError):                                       # 13
        manager.create_apartment_settlement("invalid-key", 2025, 1)

def test_create_tenant_settlements():
    manager = Manager(Parameters())

    manager.tenants = {
        "t1": Tenant(
            name="Jan",
            apartment="apart-polanka",
            room="r1",
            rent_pln=1000.0,
            deposit_pln=1000.0,
            date_agreement_from="2025-01-01",
            date_agreement_to="2025-12-31",
        ),
        "t2": Tenant(
            name="Adam",
            apartment="apart-polanka",
            room="r2",
            rent_pln=1000.0,
            deposit_pln=1000.0,
            date_agreement_from="2025-01-01",
            date_agreement_to="2025-12-31",
        ),
        "t_old": Tenant(
            name="Były Najemca",
            apartment="apart-polanka",
            room="r3",
            rent_pln=1000.0,
            deposit_pln=1000.0,
            date_agreement_from="2024-01-01",
            date_agreement_to="2024-12-31",
        ),
        "t3": Tenant(
            name="Ewa",
            apartment="apart-solo",
            room="r1",
            rent_pln=1500.0,
            deposit_pln=1500.0,
            date_agreement_from="2025-01-01",
            date_agreement_to="2025-12-31",
        ),
    }

    # 1. Dwóch aktualnych najemców
    s1 = ApartmentSettlement(
        apartment="apart-polanka",
        month=1,
        year=2025,
        total_rent_pln=0.0,
        total_bills_pln=1000.0,
        total_due_pln=-1000.0,
    )
    res1 = manager.create_tenant_settlements(s1)

    assert len(res1) == 2                   # 1
    assert res1[0].tenant == "t1"           # 2
    assert res1[0].bills_pln == 500.0       # 3
    assert res1[0].balance_pln == -500.0    # 4
    assert res1[1].tenant == "t2"           # 5
    assert res1[1].bills_pln == 500.0       # 6
    assert res1[1].balance_pln == -500.0    # 7

    # 2. Jeden najemca 
    s2 = ApartmentSettlement(
        apartment="apart-solo",
        month=1,
        year=2025,
        total_rent_pln=0.0,
        total_bills_pln=600.0,
        total_due_pln=-600.0,
    )
    res2 = manager.create_tenant_settlements(s2)

    assert len(res2) == 1                   # 8
    assert res2[0].tenant == "t3"           # 9
    assert res2[0].bills_pln == 600.0       # 10
    assert res2[0].balance_pln == -600.0    # 11

    # 3. Brak najemców
    s3 = ApartmentSettlement(
        apartment="apart-brak",
        month=1,
        year=2025,
        total_rent_pln=0.0,
        total_bills_pln=500.0,
        total_due_pln=-500.0,
    )
    res3 = manager.create_tenant_settlements(s3)

    assert len(res3) == 0                   # 12
    assert res3 == []                       # 13