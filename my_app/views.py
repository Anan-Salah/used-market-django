from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Item
from django.contrib.auth import logout
from django.db.models import Count
from .models import Item

def home(request):
    category = request.GET.get('category')  # None, 'electronics', 'clothes', 'furniture', 'others'

    qs = Item.objects.all().order_by('-created_at')

    if category in ['electronics', 'clothes', 'furniture', 'others']:
        qs = qs.filter(category=category)

    # عدّادات لكل فئة (للبادج على الأزرار)
    counts = Item.objects.values('category').annotate(total=Count('id'))
    count_map = {'electronics': 0, 'clothes': 0, 'furniture': 0, 'others': 0}
    for c in counts:
        count_map[c['category']] = c['total']

    context = {
        'items': qs,
        'active_category': category or 'all',
        'counts': count_map,
        'total_all': Item.objects.count(),
    }
    return render(request, 'accounts/home.html', context)


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "اسم المستخدم أو كلمة المرور غير صحيحة.")
    return render(request, 'accounts/login.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.error(request, "كلمتا المرور غير متطابقتين.")
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, "اسم المستخدم موجود بالفعل.")
            return redirect('register')

        user = User.objects.create_user(username=username, email=email, password=password1)
        login(request, user)
        messages.success(request, "تم إنشاء الحساب وتسجيل الدخول بنجاح!")
        return redirect('home')

    return render(request, 'accounts/register.html')

@login_required
def add_item(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        phone = request.POST.get('phone')
        category = request.POST.get('category')
        image = request.FILES.get('image')

        Item.objects.create(
            seller=request.user,
            name=name,
            description=description,
            price=price,
            phone=phone,
            category=category,
            image=image
        )
        messages.success(request, "تم إضافة الغرض بنجاح!")
        return redirect('home')

    return render(request, 'accounts/add_item.html')

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'accounts/item_detail.html', {'item': item})


@login_required
def edit_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    if item.seller != request.user:
        messages.error(request, "غير مسموح لك بتعديل هذا الغرض ❌")
        return redirect('home')

    if request.method == 'POST':
        item.name = request.POST.get('name')
        item.description = request.POST.get('description')
        item.price = request.POST.get('price')
        item.category = request.POST.get('category')
        item.phone = request.POST.get('phone')
        if 'image' in request.FILES:
            item.image = request.FILES['image']
        item.save()
        messages.success(request, "تم تعديل الغرض بنجاح ✅")
        return redirect('item_detail', item_id=item.id)

    return render(request, 'accounts/edit_item.html', {'item': item})



def logout_view(request):
    logout(request)
    return redirect('login')


@login_required
def delete_item(request, item_id):
    item = get_object_or_404(Item, id=item_id)

    # تحقق أن المستخدم هو صاحب الغرض
    if item.seller == request.user:
        item.delete()
        messages.success(request, "تم حذف الغرض بنجاح ✅")
    else:
        messages.error(request, "غير مسموح لك بحذف هذا الغرض ❌")

    return redirect('home')


@login_required
def account_view(request):
    user = request.user
    items = Item.objects.filter(seller=user).order_by('-created_at')

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')

        user.username = username
        user.email = email
        user.save()
        messages.success(request, "تم تحديث بيانات الحساب بنجاح ✅")
        return redirect('account')

    context = {
        'user': user,
        'items': items,
    }
    return render(request, 'accounts/account.html', context)
