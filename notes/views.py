from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Employee
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
import json
import uuid
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

# In-memory token store (for demo only)
TOKENS = {}

def authenticate_request(request):
    token = request.headers.get('Authorization')
    user_id = TOKENS.get(token)
    return user_id

@csrf_exempt
def register_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            User.objects.create_user(username=username, password=password)
            return JsonResponse({'message': 'User registered successfully'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def login_user(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            username = data['username']
            password = data['password']

            user = authenticate(username=username, password=password)
            if user is not None:
                token = str(uuid.uuid4())
                TOKENS[token] = user.id
                return JsonResponse({'token': token})
            else:
                return JsonResponse({'error': 'Invalid credentials'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def employee_list(request):
    user_id = authenticate_request(request)
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    if request.method == 'GET':
        employees = list(Employee.objects.values())
        return JsonResponse(employees, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            emp = Employee.objects.create(
                name=data['name'],
                email=data['email'],
                department=data['department'],
                salary=data['salary']
            )
            return JsonResponse({'id': emp.id, 'message': 'Employee created'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

@csrf_exempt
def employee_detail(request, emp_id):
    user_id = authenticate_request(request)
    if not user_id:
        return JsonResponse({'error': 'Unauthorized'}, status=401)

    try:
        emp = Employee.objects.get(id=emp_id)
    except Employee.DoesNotExist:
        return JsonResponse({'error': 'Employee not found'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'id': emp.id,
            'name': emp.name,
            'email': emp.email,
            'department': emp.department,
            'salary': str(emp.salary)
        })

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            emp.name = data['name']
            emp.email = data['email']
            emp.department = data['department']
            emp.salary = data['salary']
            emp.save()
            return JsonResponse({'message': 'Employee updated'})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=400)

    elif request.method == 'DELETE':
        emp.delete()
        return JsonResponse({'message': 'Employee deleted'})

# Web Dashboard Views
def home_view(request):
    return render(request, 'employees/home.html')

def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        if User.objects.filter(username=username).exists():
            return render(request, 'employees/register.html', {'error': 'Username already exists'})
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

@login_required
def dashboard_view(request):
    employees = Employee.objects.all()
    return render(request, 'employees/dashboard.html', {'employees': employees})

def logout_view(request):
    logout(request)
    return redirect('/login/')
