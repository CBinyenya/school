from django.shortcuts import render

def home_page_view(request):
    return render(request, 'site/index.html')

def base_page_view(request):
    return render(request, 'site/base.html')


# Create your views here.
