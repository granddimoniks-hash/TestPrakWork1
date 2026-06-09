import pytest
from django.test import Client
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from inventory.models import Supplier, Equipment


@pytest.fixture
def client():
    return Client()


@pytest.fixture
def supplier(db):
    return Supplier.objects.create(
        name='ООО Приборы',
        contact_email='info@pribory.ru',
        phone='+7-999-123-45-67',
    )


@pytest.fixture
def another_supplier(db):
    return Supplier.objects.create(
        name='ЗАО Техника',
        contact_email='tech@technika.ru',
        phone='+7-999-765-43-21',
    )


@pytest.fixture
def equipment(db, supplier):
    return Equipment.objects.create(
        name='Осциллограф',
        inventory_number='INV-001',
        description='Цифровой осциллограф 200 МГц',
        status='in_stock',
        supplier=supplier,
    )


@pytest.fixture
def another_equipment(db, supplier):
    return Equipment.objects.create(
        name='Мультиметр',
        inventory_number='INV-002',
        description='Цифровой мультиметр',
        status='in_use',
        supplier=supplier,
    )


@pytest.fixture(scope='session')
def browser():
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()
