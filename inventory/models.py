from django.db import models
from django.utils.text import slugify
from transliterate import translit


STATUS_CHOICES = [
    ('in_stock', 'На складе'),
    ('in_use', 'В эксплуатации'),
    ('under_repair', 'В ремонте'),
    ('decommissioned', 'Списано'),
]


class Supplier(models.Model):
    name = models.CharField('Название', max_length=200, unique=True)
    contact_email = models.EmailField('Email', blank=True)
    phone = models.CharField('Телефон', max_length=30, blank=True)

    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'
        ordering = ['name']

    def __str__(self):
        return self.name


class Equipment(models.Model):
    name = models.CharField('Название', max_length=200)
    slug = models.SlugField('Slug', max_length=200, unique=True, blank=True)
    inventory_number = models.CharField(
        'Инвентарный номер', max_length=50, unique=True
    )
    description = models.TextField('Описание', blank=True)
    status = models.CharField(
        'Статус', max_length=20, choices=STATUS_CHOICES, default='in_stock'
    )
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        verbose_name='Поставщик',
        related_name='equipment',
    )
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)
    updated_at = models.DateTimeField('Дата обновления', auto_now=True)

    class Meta:
        verbose_name = 'Оборудование'
        verbose_name_plural = 'Оборудование'
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} ({self.inventory_number})'

    def save(self, *args, **kwargs):
        if not self.slug:
            base = self.name
            try:
                base = translit(base, 'ru', reversed=True)
            except Exception:
                pass
            self.slug = slugify(base)
            if not self.slug:
                self.slug = f'item-{self.inventory_number}'
            original = self.slug
            counter = 1
            while Equipment.objects.filter(slug=self.slug).exclude(pk=self.pk).exists():
                self.slug = f'{original}-{counter}'
                counter += 1
        super().save(*args, **kwargs)
