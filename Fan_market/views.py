from datetime import date
from io import BytesIO

from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView
from .models import MainItem, Category, Company, Cart, CartItem, Comment, Reply, Dust
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q, Count
from django.db.models import Avg
from .forms import CommentForm, ReplyForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .conf_forms import ConfForm
from django.contrib.auth import logout
from django.http import HttpResponseRedirect, Http404
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from django.http import HttpResponse
from allauth.account.forms import ChangePasswordForm

def index(request):  # Головна сторінка веб-сайту
    categories = Category.objects.all()
    dusts = Dust.objects.all()
    companies = Company.objects.all()
    item = MainItem.objects.all()
    return render(request, 'web_view/home.html',
                  {'categories': categories, 'companies': companies, 'dusts': dusts, 'item': item})


def signout(request):
    logout(request)
    return redirect('/')


@login_required
def account_view(request):  # Сторінка користувача
    password_form = ChangePasswordForm() #Отримуємо форму з бібліотеки allauth
    context = {
        'user': request.user,
        'form': password_form,
    }
    return render(request, 'web_view/account_info.html', context)


@login_required
@require_POST
def account_change_name(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save()
        return redirect('account_info')
    return render(request, 'web_view/account_info.html')


@login_required
def account_change_email(request):
    if request.method == 'POST':
        new_email = request.POST.get('email')
        if new_email:
            request.user.email = new_email
            request.user.save()
    return redirect('account_info')

# Product View
def show_details(request, pk):  # Опис товарів
    item = get_object_or_404(MainItem, pk=pk)
    related_items = MainItem.objects.filter(category=item.category).exclude(pk=pk)[0:3]
    if request.method == 'POST':
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            text = comment_form.cleaned_data['text']
            rating = comment_form.cleaned_data['rating']
            comment = Comment(user=request.user, item=item, text=text, rating=rating)
            comment.save()
            return redirect('detail', pk=pk)
    else:
        comment_form = CommentForm()

    comments = Comment.objects.filter(item=item)
    reply_form = ReplyForm()

    return render(request, 'web_view/details.html', {
        'item': item,
        'related_items': related_items,
        'comment_form': comment_form,
        'comments': comments,
        'reply_form': reply_form,
    })


# Filter View
def items_filter(request):  # пошук товарів
    query = request.GET.get('query', '')
    sort_by = request.GET.get('sort_by', '')
    category_id = request.GET.get('category', 0)
    company_id = request.GET.get('company', 0)
    dust_ids = request.GET.getlist('dust', [])
    price = request.GET.get('price', 0)
    categories = Category.objects.all()
    companies = Company.objects.all()
    dusts = Dust.objects.all()
    items = MainItem.objects.all()
    min_price = request.GET.get('min_price', 0)
    max_price = request.GET.get('max_price', 999)
    min_particle_size = request.GET.get('min_particle_size', 0)
    max_particle_size = request.GET.get('max_particle_size', 999)
    cleaning_efficiency = request.GET.get('cleaning_efficiency', 0)
    temperature = request.GET.get('temperature', 0)
    concentration = request.GET.get('concentration', 0)

    if category_id:
        items = items.filter(category_id=category_id)

    if company_id:
        items = items.filter(company_id=company_id)

    if dust_ids:
        items = items.filter(dust__id__in=dust_ids)

    if query:
        items = items.filter(Q(name__icontains=query) | Q(description__icontains=query))

    if sort_by == 'name_asc':
        items = items.order_by('name')

    elif sort_by == 'name_desc':
        items = items.order_by('-name')

    elif sort_by == 'price_asc':
        items = items.order_by('price')

    elif sort_by == 'price_desc':
        items = items.order_by('-price')

    elif sort_by == 'rating':
        items = items.annotate(avg_rating=Avg('comments__rating')).order_by('avg_rating')

    if min_price:
        items = items.filter(price__gte=min_price)

    if max_price:
        items = items.filter(price__lte=max_price)

    if min_particle_size:
        items = items.filter(min_particle_size__gte=min_particle_size)

    if max_particle_size:
        items = items.filter(max_particle_size__lte=max_particle_size)

    if cleaning_efficiency:
        items = items.filter(cleaning_efficiency__gte=cleaning_efficiency)

    if temperature:
        items = items.filter(temperature__gte=temperature)

    if concentration:
        items = items.filter(concentration__gte=concentration)

    items = items.distinct()  # уникаємо дублювання результатів

    for dust_id in dust_ids:
        items = items.filter(dust__id=dust_id)

    paginator = Paginator(items, 6)
    page = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    return render(request, 'web_view/filter.html', {
        'items': page_obj,
        'query': query,
        'categories': categories,
        'dusts': dusts,
        'companies': companies,
        'category_id': int(category_id),
        'dust_ids': dust_ids,
        'company_id': int(company_id),
        'page_obj': page_obj,
        'min_price': int(min_price),
        'max_price': int(max_price),
        'min_particle_size': float(min_particle_size),
        'max_particle_size': float(max_particle_size),
        'cleaning_efficiency': int(cleaning_efficiency),
        'temperature': int(temperature),
        'concentration': int(concentration),
        'selected_price': int(price),
        'sort_by': sort_by
    })


# Configurator View
def configurator(request):
    if request.method == 'POST':
        form = ConfForm(request.POST)
        if form.is_valid():
            particle_size_range, cleaning_efficiency, temperature, concentration, dust_ids = form.cleaned_data[
                'particle_size'], form.cleaned_data['cleaning_efficiency'], form.cleaned_data['temperature'], \
                form.cleaned_data['concentration'], form.cleaned_data.get('dusts', [])

            min_particle_size, max_particle_size = map(float, particle_size_range.split('-'))
            request.session['min_particle_size'] = min_particle_size
            request.session['max_particle_size'] = max_particle_size
            request.session['cleaning_efficiency'] = cleaning_efficiency
            request.session['temperature'] = temperature
            request.session['concentration'] = concentration
            request.session['dust_ids'] = dust_ids
            # Отримуємо список товарів з відповідними параметрами
            all_items = MainItem.objects.filter(
                min_particle_size__lte=min_particle_size,
                max_particle_size__gte=max_particle_size,
                cleaning_efficiency__gte=cleaning_efficiency,
                concentration__gte=concentration,
                dust__id__in=dust_ids
            ).annotate(num_dusts=Count('dust')).filter(
                num_dusts=len(dust_ids))  # Умова для вивидення фільтрів що мають більше 1 параметрів типу пилу

            items = all_items.filter(temperature__gte=temperature)

            if not items.exists():
                items = all_items

                for item in items:
                    item.heatattention = item.temperature < int(temperature)

                categories_with_items = Category.objects.filter(
                    mainitem__in=items
                ).annotate(num_items=Count('mainitem')).distinct()

                for category in categories_with_items:
                    category.heatattention = category.mainitem_set.filter(temperature__lt=temperature)

            else:
                categories_with_items = Category.objects.filter(
                    mainitem__in=items
                ).annotate(num_items=Count('mainitem')).distinct()

            return render(request, 'web_view/configurator.html',
                          {'categories': categories_with_items, 'items': items, 'form': form})
    else:
        form = ConfForm()

    return render(request, 'web_view/configurator.html', {'form': form})


def configurator_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    print(request.POST)
    min_particle_size = request.session.get('min_particle_size')
    max_particle_size = request.session.get('max_particle_size')
    cleaning_efficiency = request.session.get('cleaning_efficiency')
    temperature = request.session.get('temperature')
    concentration = request.session.get('concentration')
    dust_ids = request.session.get('dust_ids')
    # Фільтрація товарів за параметрами та категорією
    items = MainItem.objects.filter(category=category,
                                    min_particle_size__lte=min_particle_size,
                                    max_particle_size__gte=max_particle_size,
                                    cleaning_efficiency__gte=cleaning_efficiency,
                                    temperature__gte=temperature,
                                    concentration__gte=concentration,
                                    dust__id__in=dust_ids
                                    ).annotate(num_items=Count('id')).distinct()
    if not items.exists():
        items = MainItem.objects.filter(
            category=category,
            min_particle_size__lte=min_particle_size,
            max_particle_size__gte=max_particle_size,
            cleaning_efficiency__gte=cleaning_efficiency,
            concentration__gte=concentration,
            dust__id__in=dust_ids
        ).annotate(num_dusts=Count('dust')).filter(
            num_dusts=len(dust_ids))

    for item in items:
        item.heatattention = item.temperature < int(temperature)

    return render(request, 'web_view/configurator_result.html', {'category': category, 'items': items})


# Cart View
def add_to_cart(request, pk):
    if request.method == 'POST':
        item = MainItem.objects.get(pk=pk)
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart_item, created = CartItem.objects.get_or_create(cart=cart, item=item)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('cart')


def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk)
    cart_item.delete()
    return redirect('cart')


def view_cart(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()
    for item in cart_items:
        item.total_price = item.quantity * item.item.price
    context = {
        'cart_items': cart_items,
    }
    total_price = sum(item.item.price * item.quantity for item in cart_items)
    return render(request, 'web_view/cart.html', {'cart_items': cart_items, 'total_price': total_price})


@require_POST
def update_cart_item_quantity(request):  # оновлюємо кількість товару в кошику
    if request.method == 'POST':
        cart_item_id = request.POST.get('cart_item_id')
        new_quantity = request.POST.get('new_quantity')

        if new_quantity.isdigit():
            cart_item = get_object_or_404(CartItem, pk=cart_item_id)
            cart_item.quantity = new_quantity
            cart_item.save()
        else:
            cart_item = get_object_or_404(CartItem, pk=cart_item_id)
            cart_item.quantity = 1
            cart_item.save()

    return HttpResponseRedirect(reverse('cart'))


# Comment View
@staff_member_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    item_id = comment.item.id
    comment.delete()
    return redirect('detail', pk=item_id)


def reply_to_comment(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id)
    if request.method == 'POST':
        form = ReplyForm(request.POST)
        if form.is_valid():
            text = form.cleaned_data['text']
            reply = Reply(user=request.user, comment=comment, text=text)
            reply.save()
            return redirect('detail', pk=comment.item.id)
    else:
        form = ReplyForm()
    return render(request, 'web_view/details.html', {'form': form})


def delete_reply(request, reply_id):
    reply = get_object_or_404(Reply, id=reply_id)
    if request.user == reply.user:
        reply.delete()
    return redirect('detail', pk=reply.comment.item.id)


def order_pdf(request):  # функція формування пдф листу замовлення
    user = request.user
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.cartitem_set.all()

    buffer = BytesIO()
    pdf = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    pdfmetrics.registerFont(TTFont('DejaVuSans', 'DejaVuSans.ttf'))
    content = []

    content.append(Paragraph("Filter Market - Замовлення", styles['Heading1']))
    content.append(Spacer(1, 12))

    content.append(Paragraph("Замовлено: {}".format(user.username), styles['Normal']))
    content.append(Paragraph("Товар:", styles['Normal']))

    data = [['Товар', 'Кількість', 'Ціна за один', 'Загальна ціна']]
    for item in cart_items:
        item.total_price = item.quantity * item.item.price
        data.append([item.item.name, item.quantity, "${}".format(item.item.price), "${}".format(item.total_price)])

    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                               ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                               ('FONTNAME', (0, 0), (-1, 0), 'DejaVuSans'),
                               ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                               ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                               ('GRID', (0, 0), (-1, -1), 1, colors.black)]))

    content.append(table)
    total_price = sum(item.item.price * item.quantity for item in cart_items)
    content.append(Paragraph("Сумма замовлення: ${}".format(total_price), styles['Normal']))
    pdf.build(content)

    pdf_content = buffer.getvalue()
    buffer.close()

    response = HttpResponse(pdf_content, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="order_summary.pdf"'
    return response
