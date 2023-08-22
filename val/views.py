from django.shortcuts import render


# Create your views here.
def landing_val(request):
    return render(request, "val/landing_val.html")
