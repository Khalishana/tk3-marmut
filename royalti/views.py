from django.shortcuts import render

# Create your views here.
def show_royalti(request):
    return render(request, "royalti.html")