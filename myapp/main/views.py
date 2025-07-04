# mywebsite/main/views.py

from django.shortcuts import render

def home(request):
    """
    Renders the main front page of the website.
    """
    return render(request, 'main/index.html')

def features_view(request):
    """
    Renders the features page of the website.
    """
    return render(request, 'main/features.html')

def about_view(request):
    """
    Renders the about us page of the website.
    """
    return render(request, 'main/about.html') # NEW VIEWer(request, 'main/features.html')