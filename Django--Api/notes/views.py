# employees/views.py
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Employee, UserProfile
from .forms import EmployeeForm, UserForm, ProfileForm
import json, uuid

TOKENS = {}

def authenticate_request(request):
    token = request.headers.get('Authorization')
    user_id = TOKENS.get(token)
    return user_id

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)
        User.objects.create_user(username=username, password=password)
        return JsonResponse({'message': 'User registered successfully'})

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        username = data['username']
        password = data['password']
        user = authenticate(username=username, password=password)
        if user:
            token = str(uuid.uuid4())
            TOKENS[token] = user.id
            return JsonResponse({'token': token})
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=401)

@csrf_exempt
def employee_list(request):
    user_id = authenticate_request(request)
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        employees = list(Employee.objects.values())
        return JsonResponse(employees, safe=False)
    elif request.method == 'POST':
        data = json.loads(request.body)
        emp = Employee.objects.create(
            name=data['name'],
            email=data['email'],
            department=data['department'],
            salary=data['salary']
        )
        return JsonResponse({'id': emp.id, 'message': 'Employee created'})

@csrf_exempt
def employee_detail(request, emp_id):
    user_id = authenticate_request(request)
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        emp = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': emp.id,
            'name': emp.name,
            'email': emp.email,
            'department': emp.department,
            'salary': str(emp.salary)
        })
    elif request.method == 'PUT':
        data = json.loads(request.body)
        emp.name = data['name']
        emp.email = data['email']
        emp.department = data['department']
        emp.salary = data['salary']
        emp.save()
        return JsonResponse({'message': 'Updated'})
    elif request.method == 'DELETE':
        emp.delete()
        return JsonResponse({'message': 'Deleted'})

# Web views
def home_view(request):
    return render(request, 'employees/home.html')

@login_required
def dashboard_view(request):
    employees = Employee.objects.all()
    return render(request, 'employees/dashboard.html', {'employees': employees})

def add_info(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EmployeeForm()
    return render(request, 'employees/add_info.html', {'form': form})

def edit_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'employees/add_info.html', {'form': form})

def delete_employee(request, emp_id):
    employee = get_object_or_404(Employee, id=emp_id)
    employee.delete()
    return redirect('dashboard')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'employees/register.html', {'error': 'Username exists'})
        User.objects.create_user(username=username, password=password)
        return redirect('/login/')
    return render(request, 'employees/register.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('/dashboard/')
        else:
            return render(request, 'employees/login.html', {'error': 'Invalid credentials'})
    return render(request, 'employees/login.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')

@login_required
def profile_view(request):
    return render(request, 'employees/profile.html', {'user': request.user})

@login_required
def profile_edit(request):
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    if request.method == 'POST':
        user_form = UserForm(request.POST, instance=user)
        profile_form = ProfileForm(request.POST, request.FILES, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('profile')
    else:
        user_form = UserForm(instance=user)
        profile_form = ProfileForm(instance=profile)
    return render(request, 'employees/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })
