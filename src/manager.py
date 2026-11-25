from src.models import Apartment, ApartmentSettlement, Bill, Parameters, Tenant, TenantSettlement, Transfer


class Manager:
    def __init__(self, parameters: Parameters):
        self.parameters = parameters 

        self.apartments = {}
        self.tenants = {}
        self.transfers = []
        self.bills = []
       
        self.load_data()

    def load_data(self):
        self.apartments = Apartment.from_json_file(self.parameters.apartments_json_path)
        self.tenants = Tenant.from_json_file(self.parameters.tenants_json_path)
        self.transfers = Transfer.from_json_file(self.parameters.transfers_json_path)
        self.bills = Bill.from_json_file(self.parameters.bills_json_path)

    def check_tenants_apartment_keys(self) -> bool:
        for tenant in self.tenants.values():
            if tenant.apartment not in self.apartments:
                return False
        return True

    def get_apartment_costs(self, apartment_key: str, year=None, month=None):
        if apartment_key not in self.apartments:
            raise KeyError(f"Apartment '{apartment_key}' does not exist.")

        if month is not None and not (1 <= month <= 12):
            raise ValueError(f"Invalid month: {month}")

        total_cost = 0.0

        for bill in self.bills:
            if (bill.apartment == apartment_key and (year is None or bill.settlement_year == year) 
                and (month is None or bill.settlement_month == month)):
                total_cost += float(bill.amount_pln)

        return round(total_cost, 2)

    def create_apartment_settlement(self, apartment_key: str, year: int, month: int):
        total_bills = self.get_apartment_costs(apartment_key, year, month)
        total_rent = 0.0
        total_due = round(total_rent - total_bills, 2)

        return ApartmentSettlement(
            apartment=apartment_key,
            month=month,
            year=year,
            total_rent_pln=total_rent,
            total_bills_pln=total_bills,
            total_due_pln=total_due,
        )

    def create_tenant_settlements(self, settlement: ApartmentSettlement):
        # Krok 1: Zbieramy klucze aktualnych najemców z tego mieszkania
        active_tenants = []
        miesiac_rozliczenia = f"{settlement.year}-{settlement.month:02d}"

        for tenant_key, tenant in self.tenants.items():
            if tenant.apartment == settlement.apartment:
                od = tenant.date_agreement_from[:7]
                do = tenant.date_agreement_to[:7]
                if od <= miesiac_rozliczenia <= do:
                    active_tenants.append(tenant_key)

        # Krok 2: Jeśli nie ma nikogo, zwracamy pustą listę
        if len(active_tenants) == 0:
            return []

        # Krok 3: Dzielimy rachunki po równo i tworzymy obiekty
        rachunki_na_osobe = round(settlement.total_bills_pln / len(active_tenants), 2)
        czynsz = 0.0
        do_zaplaty = round(czynsz + rachunki_na_osobe, 2)
        bilans = round(0.0 - do_zaplaty, 2)

        wynik = []
        for tenant_key in active_tenants:
            rozliczenie = TenantSettlement(
                tenant=tenant_key,
                apartment_settlement=settlement.apartment,
                month=settlement.month,
                year=settlement.year,
                rent_pln=czynsz,
                bills_pln=rachunki_na_osobe,
                total_due_pln=do_zaplaty,
                balance_pln=bilans,
            )
            wynik.append(rozliczenie)

        return wynik