from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from .models import Equipment, Supplier
from .forms import EquipmentForm, SupplierForm


def index(request):
    return redirect('equipment_list')


def equipment_list(request):
    queryset = Equipment.objects.select_related('supplier')
    q = request.GET.get('q', '').strip()
    status = request.GET.get('status', '').strip()
    if q:
        queryset = queryset.filter(
            Q(name__icontains=q) | Q(inventory_number__icontains=q)
        )
    if status:
        queryset = queryset.filter(status=status)
    return render(request, 'inventory/equipment_list.html', {
        'object_list': queryset,
        'q': q,
        'status': status,
    })


def equipment_detail(request, slug):
    obj = get_object_or_404(Equipment, slug=slug)
    return render(request, 'inventory/equipment_detail.html', {'object': obj})


def equipment_create(request):
    form = EquipmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('equipment_list')
    return render(request, 'inventory/equipment_form.html', {
        'form': form,
        'title': 'Добавить оборудование',
    })


def equipment_update(request, slug):
    obj = get_object_or_404(Equipment, slug=slug)
    form = EquipmentForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('equipment_detail', slug=obj.slug)
    return render(request, 'inventory/equipment_form.html', {
        'form': form,
        'title': 'Редактировать оборудование',
    })


def equipment_delete(request, slug):
    obj = get_object_or_404(Equipment, slug=slug)
    if request.method == 'POST':
        obj.delete()
        return redirect('equipment_list')
    return render(request, 'inventory/equipment_confirm_delete.html', {
        'object': obj,
    })


def supplier_list(request):
    queryset = Supplier.objects.all()
    q = request.GET.get('q', '').strip()
    if q:
        queryset = queryset.filter(name__icontains=q)
    return render(request, 'inventory/supplier_list.html', {
        'object_list': queryset,
        'q': q,
    })


def supplier_detail(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    return render(request, 'inventory/supplier_detail.html', {'object': obj})


def supplier_create(request):
    form = SupplierForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'title': 'Добавить поставщика',
    })


def supplier_update(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    form = SupplierForm(request.POST or None, instance=obj)
    if request.method == 'POST' and form.is_valid():
        form.save()
        return redirect('supplier_detail', pk=obj.pk)
    return render(request, 'inventory/supplier_form.html', {
        'form': form,
        'title': 'Редактировать поставщика',
    })


def supplier_delete(request, pk):
    obj = get_object_or_404(Supplier, pk=pk)
    if request.method == 'POST':
        obj.delete()
        return redirect('supplier_list')
    return render(request, 'inventory/supplier_confirm_delete.html', {
        'object': obj,
    })
