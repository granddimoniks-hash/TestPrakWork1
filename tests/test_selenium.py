import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from inventory.models import Supplier, Equipment


@pytest.fixture
def live_url(live_server):
    return live_server.url


@pytest.fixture
def seed_data(db):
    s = Supplier.objects.create(name='ООО Тест', contact_email='t@t.ru', phone='123')
    Equipment.objects.create(
        name='Генератор', inventory_number='INV-100',
        status='in_stock', supplier=s,
    )
    Equipment.objects.create(
        name='Анализатор', inventory_number='INV-200',
        status='in_use', supplier=s,
    )
    return s


@pytest.mark.django_db(transaction=True)
class TestNavigation:

    def test_main_page_redirects_to_equipment(self, browser, live_url):
        browser.get(live_url + '/')
        assert '/equipment/' in browser.current_url

    def test_nav_links(self, browser, live_url, seed_data):
        browser.get(live_url + '/equipment/')
        nav = browser.find_element(By.TAG_NAME, 'nav')
        links = nav.find_elements(By.TAG_NAME, 'a')
        assert len(links) >= 2

        links[1].click()
        assert '/suppliers/' in browser.current_url

        nav = browser.find_element(By.TAG_NAME, 'nav')
        nav.find_elements(By.TAG_NAME, 'a')[0].click()
        assert '/equipment/' in browser.current_url


@pytest.mark.django_db(transaction=True)
class TestEquipmentCRUD:

    def test_create_equipment(self, browser, live_url, db):
        Supplier.objects.create(name='Поставщик Тест')

        browser.get(live_url + '/equipment/add/')
        browser.find_element(By.ID, 'id_name').send_keys('Тестовый прибор')
        browser.find_element(By.ID, 'id_inventory_number').send_keys('INV-SELENIUM')
        browser.find_element(By.ID, 'id_description').send_keys('Описание прибора')

        status_select = Select(browser.find_element(By.ID, 'id_status'))
        status_select.select_by_value('in_stock')

        supplier_select = Select(browser.find_element(By.ID, 'id_supplier'))
        supplier_select.select_by_visible_text('Поставщик Тест')

        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        assert '/equipment/' in browser.current_url
        page = browser.page_source
        assert 'Тестовый прибор' in page
        assert 'INV-SELENIUM' in page

    def test_read_equipment_detail(self, browser, live_url, seed_data):
        eq = Equipment.objects.first()
        browser.get(live_url + f'/equipment/{eq.slug}/')
        page = browser.page_source
        assert eq.name in page
        assert eq.inventory_number in page

    def test_update_equipment(self, browser, live_url, seed_data):
        eq = Equipment.objects.first()
        browser.get(live_url + f'/equipment/{eq.slug}/edit/')

        name_field = browser.find_element(By.ID, 'id_name')
        name_field.clear()
        name_field.send_keys('Обновлённое название')

        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        page = browser.page_source
        assert 'Обновлённое название' in page

    def test_delete_equipment(self, browser, live_url, seed_data):
        eq = Equipment.objects.first()
        slug = eq.slug

        browser.get(live_url + f'/equipment/{slug}/delete/')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        assert '/equipment/' in browser.current_url
        page = browser.page_source
        assert eq.name not in page

        browser.get(live_url + f'/equipment/{slug}/')
        assert 'Not Found' in browser.page_source

    def test_cancel_link(self, browser, live_url, seed_data):
        browser.get(live_url + '/equipment/add/')
        cancel = browser.find_element(By.LINK_TEXT, 'Отмена')
        cancel.click()
        assert '/equipment/' in browser.current_url


@pytest.mark.django_db(transaction=True)
class TestRelatedEntities:

    def test_new_supplier_appears_in_equipment_form(self, browser, live_url, db):
        Supplier.objects.create(name='Свежий поставщик')
        browser.get(live_url + '/equipment/add/')
        supplier_select = Select(browser.find_element(By.ID, 'id_supplier'))
        options = [o.text for o in supplier_select.options]
        assert 'Свежий поставщик' in options

    def test_delete_supplier_with_equipment_blocked(self, browser, live_url, seed_data):
        supplier = seed_data
        browser.get(live_url + f'/suppliers/{supplier.pk}/delete/')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()
        assert Supplier.objects.filter(pk=supplier.pk).exists()


@pytest.mark.django_db(transaction=True)
class TestSearchAndFilter:

    def test_search_equipment(self, browser, live_url, seed_data):
        browser.get(live_url + '/equipment/')
        search = browser.find_element(By.NAME, 'q')
        search.send_keys('Генератор')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        page = browser.page_source
        assert 'Генератор' in page
        assert 'Анализатор' not in page

    def test_filter_by_status(self, browser, live_url, seed_data):
        browser.get(live_url + '/equipment/')
        status_select = Select(browser.find_element(By.NAME, 'status'))
        status_select.select_by_value('in_use')
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        page = browser.page_source
        assert 'Анализатор' in page
        assert 'Генератор' not in page


@pytest.mark.django_db(transaction=True)
class TestSlugURLs:

    def test_slug_generated_from_name(self, browser, live_url, db):
        Supplier.objects.create(name='S')
        browser.get(live_url + '/equipment/add/')
        browser.find_element(By.ID, 'id_name').send_keys('Test Device')
        browser.find_element(By.ID, 'id_inventory_number').send_keys('INV-SLUG')
        Select(browser.find_element(By.ID, 'id_supplier')).select_by_index(1)
        browser.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        eq = Equipment.objects.get(inventory_number='INV-SLUG')
        assert eq.slug == 'test-device'

        browser.get(live_url + f'/equipment/{eq.slug}/')
        assert eq.name in browser.page_source

    def test_crud_with_slug_urls(self, browser, live_url, seed_data):
        eq = Equipment.objects.first()
        slug = eq.slug

        browser.get(live_url + f'/equipment/{slug}/')
        assert eq.name in browser.page_source

        browser.get(live_url + f'/equipment/{slug}/edit/')
        assert browser.find_element(By.ID, 'id_name').get_attribute('value') == eq.name

        browser.get(live_url + f'/equipment/{slug}/delete/')
        assert eq.name in browser.page_source
