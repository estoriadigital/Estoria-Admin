from django.shortcuts import render


def index(request):
    """
    index page
    """
    return render(request, 'index.html', {})