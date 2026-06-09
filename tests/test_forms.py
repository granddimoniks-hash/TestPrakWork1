import pytest
from inventory.forms import EquipmentForm, SupplierForm
from inventory.models import Supplier, Equipment


@pytest.mark.django_db
class TestSupplierForm:

    def test_valid_data(self):
        form = SupplierForm(data={
            'name': 'Новый поставщик',
            'contact_email': 'test@test.ru',
            'phone': '+7-000-000-00-00',
        })
        assert form.is_valid()

    def test_missing_name(self):
        form = SupplierForm(data={
            'name': '',
            'contact_email': 'test@test.ru',
            'phone': '',
        })
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_duplicate_name(self, supplier):
        form = SupplierForm(data={
            'name': 'ООО Приборы',
            'contact_email': '',
            'phone': '',
        })
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_optional_fields(self):
        form = SupplierForm(data={
            'name': 'Минимум',
            'contact_email': '',
            'phone': '',
        })
        assert form.is_valid()


@pytest.mark.django_db
class TestEquipmentForm:

    def test_valid_data(self, supplier):
        form = EquipmentForm(data={
            'name': 'Новый прибор',
            'inventory_number': 'INV-NEW',
            'description': 'Описание',
            'status': 'in_stock',
            'supplier': supplier.pk,
        })
        assert form.is_valid()

    def test_missing_name(self, supplier):
        form = EquipmentForm(data={
            'name': '',
            'inventory_number': 'INV-X',
            'status': 'in_stock',
            'supplier': supplier.pk,
        })
        assert not form.is_valid()
        assert 'name' in form.errors

    def test_missing_inventory_number(self, supplier):
        form = EquipmentForm(data={
            'name': 'Прибор',
            'inventory_number': '',
            'status': 'in_stock',
            'supplier': supplier.pk,
        })
        assert not form.is_valid()
        assert 'inventory_number' in form.errors

    def test_missing_supplier(self):
        form = EquipmentForm(data={
            'name': 'Прибор',
            'inventory_number': 'INV-X',
            'status': 'in_stock',
            'supplier': '',
        })
        assert not form.is_valid()
        assert 'supplier' in form.errors

    def test_duplicate_inventory_number(self, equipment, supplier):
        form = EquipmentForm(data={
            'name': 'Другой',
            'inventory_number': 'INV-001',
            'status': 'in_stock',
            'supplier': supplier.pk,
        })
        assert not form.is_valid()
        assert 'inventory_number' in form.errors
