from django.shortcuts import render


# Create your views here.
def landing_freelo_app(request):
    return render(request, "freelo_app/landing_freelo_app.html")


def landing_lol(request):
    return render(request, "lol/templates/lol/landing_lol.html")


def landing_val(request):
    return render(request, "val/templates/val/landing_val.html")
