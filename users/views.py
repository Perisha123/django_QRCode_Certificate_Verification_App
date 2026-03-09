from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from certificate.models import Certificate  # if you want users to see certificates
import qrcode
import io
from django.http import HttpResponse

# User registration
def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('user_register')
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()
        messages.success(request, 'User registered successfully!')
        return redirect('user_login')
    return render(request, 'users/register.html')

# User login
def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('user_dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('user_login')
    return render(request, 'users/login.html')

# User logout
def user_logout(request):
    logout(request)
    return redirect('user_login')

# User dashboard
def user_dashboard(request):
    # Display certificates uploaded
    certificates = Certificate.objects.all()
    context = {'certificates': certificates}
    return render(request, 'users/dashboard.html', context)

# QR scanning page
def scan_qr(request):
    if request.method == 'POST':
        data = request.POST['qr_data']  # Assuming you get QR code content from a form
        try:
            certificate = Certificate.objects.get(id=data)
            messages.success(request, 'Certificate verified!')
            return redirect('user_dashboard')
        except Certificate.DoesNotExist:
            messages.error(request, 'Certificate not found!')
            return redirect('scan_qr')
    return render(request, 'users/scan.html')