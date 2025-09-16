from django.shortcuts import render, request

# Create your views here.
def home(request):
    return render(request, 'index.html')


def dashboard(request):
    return render(request, 'dashboard.html')