from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def rules(request):
    return render(request, "members/rules.html")
