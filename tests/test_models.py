import pytest
from django.db import IntegrityError
from inventory.models import Supplier, Equipment


@pytest.mark.django_db
class TestSupplierModel:

    def test_create_supplier(self, supplier):
        assert supplier.pk is not None
        assert supplier.name == 'ООО Приборы'

    def test_str(self, supplier):
        assert str(supplier) == 'ООО Приборы'

    def test_name_unique(self, supplier):
        with pytest.raises(IntegrityError):
            Supplier.objects.create(name='ООО Приборы')

    def test_name_max_length(self):
        field = Supplier._meta.get_field('name')
        assert field.max_length == 200

    def test_name_required(self, db):
        s = Supplier(name='')
        with pytest.raises(Exception):
            s.full_clean()

    def test_email_optional(self, db):
        s = Supplier(name='Тест')
        s.full_clean()

    def test_phone_max_length(self):
        field = Supplier._meta.get_field('phone')
        assert field.max_length == 30


@pytest.mark.django_db
class TestEquipmentModel:

    def test_create_equipment(self, equipment):
        assert equipment.pk is not None
        assert equipment.name == 'Осциллограф'

    def test_str(self, equipment):
        assert str(equipment) == 'Осциллограф (INV-001)'

    def test_inventory_number_unique(self, equipment, supplier):
        with pytest.raises(IntegrityError):
            Equipment.objects.create(
                name='Дубликат',
                inventory_number='INV-001',
                supplier=supplier,
            )

    def test_name_max_length(self):
        field = Equipment._meta.get_field('name')
        assert field.max_length == 200

    def test_name_required(self, db, supplier):
        eq = Equipment(name='', inventory_number='INV-999', supplier=supplier)
        with pytest.raises(Exception):
            eq.full_clean()

    def test_inventory_number_required(self, db, supplier):
        eq = Equipment(name='Тест', inventory_number='', supplier=supplier)
        with pytest.raises(Exception):
            eq.full_clean()

    def test_default_status(self, db, supplier):
        eq = Equipment.objects.create(
            name='Тест', inventory_number='INV-100', supplier=supplier
        )
        assert eq.status == 'in_stock'

    def test_slug_auto_generated(self, equipment):
        assert equipment.slug != ''
        assert equipment.slug is not None

    def test_slug_unique(self, db, supplier):
        eq1 = Equipment.objects.create(
            name='Прибор', inventory_number='INV-A1', supplier=supplier
        )
        eq2 = Equipment.objects.create(
            name='Прибор', inventory_number='INV-A2', supplier=supplier
        )
        assert eq1.slug != eq2.slug

    def test_protect_on_supplier_delete(self, equipment):
        with pytest.raises(Exception):
            equipment.supplier.delete()

    def test_created_at_auto(self, equipment):
        assert equipment.created_at is not None

    def test_updated_at_auto(self, equipment):
        assert equipment.updated_at is not None
