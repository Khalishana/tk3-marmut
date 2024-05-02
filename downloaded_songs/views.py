from django.shortcuts import render

# Create your views here.
def show_download_page(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "download.html", context)

def search_bar(request):
    context = {
        'name': 'Marmut',
        'class': 'Basdat A'
    }
    return render(request, "search_bar.html", context)