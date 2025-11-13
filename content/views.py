from django.shortcuts import render, redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django_ratelimit.decorators import ratelimit

# === HOME PAGE ===
@ratelimit(key='ip', rate='5/m', block=True)
def homie(request):
    home = Home.objects.all().order_by('-id')
    homes = home.first()
    return render(request, 'con/content/homie.html', {'homes': homes})


# === ABOUT PAGE ===
@ratelimit(key='ip', rate='5/m', block=True)
def about(request):
    home = About.objects.all().order_by('-id')
    homes = home.first()
    return render(request, 'con/content/about.html', {'homes': homes})


# === CONTACT FORM ===
@ratelimit(key='ip', rate='40/m', block=True)
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        message = request.POST.get('message')
        email = request.POST.get('email')

        Mess.objects.create(
            name=name,
            messages=message,
            email=email,
        )
        messages.success(request, "Message recieved, We will get back to you shortly")
        return redirect('about')
    return redirect('about')


@ratelimit(key='ip', rate='40/m', block=True)
def portfolio(request):
    category_slug = request.GET.get('category', None)
    categories = Categorysss.objects.all()

    home = Socails.objects.all().order_by('-id')
    if category_slug:
        home = home.filter(category__slug=category_slug)

    paginator = Paginator(home, 400)
    page_number = request.GET.get('page')
    home_page = paginator.get_page(page_number)

    return render(request, 'con/content/port.html', {
        'home': home_page,
        'categories': categories
    })



@ratelimit(key='ip', rate='40/m', block=True)
def cats(request, id):
    category = Categorysss.objects.filter(pk=id).first()
    if not category:
        return redirect('portfolio')

    homes = Socails.objects.filter(category=category).order_by('-id')

    return render(request, 'con/content/cats.html', {
        'category': category,
        'homes': homes
    })

@ratelimit(key='ip', rate='40/m', block=True)
def collab(request):
    home = Campagin.objects.all().order_by('-id')
    return render(request, 'con/content/coll.html', {'home': home})

@ratelimit(key='ip', rate='40/m', block=True)
def collabo(request, id):
    home= Campagin.objects.filter(pk=id).first()


    return render(request, 'con/content/collab.html', {'home': home})
    

@ratelimit(key='ip', rate='40/m', block=True)
def service(request):
    home = Service.objects.all().order_by('-id')
    return render(request, 'con/content/service.html', {'home': home})
