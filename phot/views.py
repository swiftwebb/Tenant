from django.shortcuts import render, get_object_or_404,redirect
from .models import *
from django.core.paginator import Paginator
from django.contrib import messages
from django_ratelimit.decorators import ratelimit
# Create your views here.


@ratelimit(key='ip', rate='40/m', block=True)
def home(request):
    photo = Photo.objects.filter(featured=True).all().order_by('-id')
    return render(request, "booth/photo/home.html", {"photo":photo} )



@ratelimit(key='ip', rate='40/m', block=True)
def hoomelist(request):
    photos = Photo.objects.all().order_by('-id') 
    paginator = Paginator(photos, 24)            
    page_number = request.GET.get('page')
    home_page = paginator.get_page(page_number)
    return render(request, "booth/photo/homelist.html", {"home": home_page})






@ratelimit(key='ip', rate='40/m', block=True)
def hoomedet(request, id):
    photo = get_object_or_404(Photo, id=id)
    return render(request, "booth/photo/homedetail.html", {"photo":photo} )




@ratelimit(key='ip', rate='40/m', block=True)
def aboutme(request):
    photot = Myself.objects.all().order_by('-id')
    photo = photot.first()
    return render(request, "booth/photo/homeabout.html", {"photo":photo} )


@ratelimit(key='ip', rate='40/m', block=True)
def service(request):
    photo = Service_Photo.objects.all().order_by('-id')
    return render(request, "booth/photo/homeservice.html", {"photo":photo} )

@ratelimit(key='ip', rate='40/m', block=True)
def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        message = request.POST.get('message')
        email = request.POST.get('email')

        Bookings.objects.create(
            full_name=name,
            message=message,
            email=email,
        )
        messages.success(request, "Message recieved, We will get back to you shortly")
        return redirect('about')
    return redirect('about')

@ratelimit(key='ip', rate='40/m', block=True)
def about(request):
    return render(request, "booth/photo/homecontact.html", {} )




