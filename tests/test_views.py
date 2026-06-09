import pytest
from django.urls import reverse
from inventory.models import Supplier, Equipment


@pytest.mark.django_db
class TestEquipmentListView:

    def test_status_code(self, client):
        response = client.get(reverse('equipment_list'))
        assert response.status_code == 200

    def test_template(self, client):
        response = client.get(reverse('equipment_list'))
        assert 'inventory/equipment_list.html' in [
            t.name for t in response.templates
        ]

    def test_contains_equipment(self, client, equipment):
        response = client.get(reverse('equipment_list'))
        assert equipment in response.context['object_list']

    def test_search_by_name(self, client, equipment, another_equipment):
        response = client.get(reverse('equipment_list'), {'q': 'Осцилло'})
        assert equipment in response.context['object_list']
        assert another_equipment not in response.context['object_list']

    def test_search_by_inventory_number(self, client, equipment):
        response = client.get(reverse('equipment_list'), {'q': 'INV-001'})
        assert equipment in response.context['object_list']

    def test_filter_by_status(self, client, equipment, another_equipment):
        response = client.get(reverse('equipment_list'), {'status': 'in_use'})
        assert another_equipment in response.context['object_list']
        assert equipment not in response.context['object_list']

    def test_empty_search_returns_all(self, client, equipment, another_equipment):
        response = client.get(reverse('equipment_list'), {'q': ''})
        obj_list = list(response.context['object_list'])
        assert equipment in obj_list
        assert another_equipment in obj_list


@pytest.mark.django_db
class TestEquipmentDetailView:

    def test_status_code(self, client, equipment):
        response = client.get(
            reverse('equipment_detail', kwargs={'slug': equipment.slug})
        )
        assert response.status_code == 200

    def test_template(self, client, equipment):
        response = client.get(
            reverse('equipment_detail', kwargs={'slug': equipment.slug})
        )
        assert 'inventory/equipment_detail.html' in [
            t.name for t in response.templates
        ]

    def test_context_object(self, client, equipment):
        response = client.get(
            reverse('equipment_detail', kwargs={'slug': equipment.slug})
        )
        assert response.context['object'] == equipment

    def test_nonexistent_slug_404(self, client, db):
        response = client.get(
            reverse('equipment_detail', kwargs={'slug': 'nonexistent'})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestEquipmentCreateView:

    def test_get_form(self, client):
        response = client.get(reverse('equipment_create'))
        assert response.status_code == 200

    def test_create_equipment(self, client, supplier):
        data = {
            'name': 'Вольтметр',
            'inventory_number': 'INV-NEW',
            'description': '',
            'status': 'in_stock',
            'supplier': supplier.pk,
        }
        response = client.post(reverse('equipment_create'), data)
        assert response.status_code == 302
        assert Equipment.objects.filter(inventory_number='INV-NEW').exists()


@pytest.mark.django_db
class TestEquipmentUpdateView:

    def test_get_form(self, client, equipment):
        response = client.get(
            reverse('equipment_update', kwargs={'slug': equipment.slug})
        )
        assert response.status_code == 200

    def test_update_equipment(self, client, equipment):
        data = {
            'name': 'Осциллограф обновлённый',
            'inventory_number': equipment.inventory_number,
            'description': equipment.description,
            'status': 'in_use',
            'supplier': equipment.supplier.pk,
        }
        response = client.post(
            reverse('equipment_update', kwargs={'slug': equipment.slug}), data
        )
        assert response.status_code == 302
        equipment.refresh_from_db()
        assert equipment.name == 'Осциллограф обновлённый'
        assert equipment.status == 'in_use'


@pytest.mark.django_db
class TestEquipmentDeleteView:

    def test_get_confirm_page(self, client, equipment):
        response = client.get(
            reverse('equipment_delete', kwargs={'slug': equipment.slug})
        )
        assert response.status_code == 200

    def test_delete_equipment(self, client, equipment):
        slug = equipment.slug
        response = client.post(
            reverse('equipment_delete', kwargs={'slug': slug})
        )
        assert response.status_code == 302
        assert not Equipment.objects.filter(slug=slug).exists()

    def test_deleted_detail_returns_404(self, client, equipment):
        slug = equipment.slug
        client.post(reverse('equipment_delete', kwargs={'slug': slug}))
        response = client.get(
            reverse('equipment_detail', kwargs={'slug': slug})
        )
        assert response.status_code == 404


@pytest.mark.django_db
class TestSupplierListView:

    def test_status_code(self, client):
        response = client.get(reverse('supplier_list'))
        assert response.status_code == 200

    def test_contains_supplier(self, client, supplier):
        response = client.get(reverse('supplier_list'))
        assert supplier in response.context['object_list']

    def test_search(self, client, supplier, another_supplier):
        response = client.get(reverse('supplier_list'), {'q': 'Приборы'})
        assert supplier in response.context['object_list']
        assert another_supplier not in response.context['object_list']


@pytest.mark.django_db
class TestSupplierDetailView:

    def test_status_code(self, client, supplier):
        response = client.get(
            reverse('supplier_detail', kwargs={'pk': supplier.pk})
        )
        assert response.status_code == 200

    def test_context_object(self, client, supplier):
        response = client.get(
            reverse('supplier_detail', kwargs={'pk': supplier.pk})
        )
        assert response.context['object'] == supplier


@pytest.mark.django_db
class TestSupplierCreateView:

    def test_get_form(self, client):
        response = client.get(reverse('supplier_create'))
        assert response.status_code == 200

    def test_create_supplier(self, client, db):
        data = {'name': 'Новый', 'contact_email': '', 'phone': ''}
        response = client.post(reverse('supplier_create'), data)
        assert response.status_code == 302
        assert Supplier.objects.filter(name='Новый').exists()


@pytest.mark.django_db
class TestSupplierUpdateView:

    def test_update_supplier(self, client, supplier):
        data = {
            'name': 'ООО Приборы (обновлено)',
            'contact_email': supplier.contact_email,
            'phone': supplier.phone,
        }
        response = client.post(
            reverse('supplier_update', kwargs={'pk': supplier.pk}), data
        )
        assert response.status_code == 302
        supplier.refresh_from_db()
        assert supplier.name == 'ООО Приборы (обновлено)'


@pytest.mark.django_db
class TestSupplierDeleteView:

    def test_delete_supplier_without_equipment(self, client, another_supplier):
        pk = another_supplier.pk
        response = client.post(
            reverse('supplier_delete', kwargs={'pk': pk})
        )
        assert response.status_code == 302
        assert not Supplier.objects.filter(pk=pk).exists()

    def test_delete_supplier_with_equipment_protected(self, client, equipment):
        pk = equipment.supplier.pk
        with pytest.raises(Exception):
            client.post(reverse('supplier_delete', kwargs={'pk': pk}))
