from django.shortcuts import render
def home_view(request):

    return render(request, "epe_app/home.html")