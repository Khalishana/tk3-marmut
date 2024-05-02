from django.shortcuts import render

# Create your views here.
def show_main(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }

    return render(request, "main.html", context)