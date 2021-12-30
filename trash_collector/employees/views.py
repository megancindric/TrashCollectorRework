from .models import Employee
from django.http.response import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.shortcuts import render
from django.apps import apps
from datetime import date
import calendar
import requests

# Create your views here.

#Displays pickupsf for:
    #Customers in employee zip code, where pickup day is today & service is not suspended OR there is a 1-time pickup scheduled for today
@login_required
def index(request):
    user = request.user

    try:
        # This line inside the 'try' will return the customer record of the logged-in user if one exists
        logged_in_employee = Employee.objects.get(user=user)
    except:
        return HttpResponseRedirect(reverse('employees:create'))
    today = date.today()
    today_weekday = calendar.day_name[today.weekday()]
    Customer = apps.get_model('customers.Customer')
    employee_geocode = geocode_address(logged_in_employee.zip_code)
    emp_lat = employee_geocode['lat']
    emp_lng = employee_geocode['lng']
    employee_lat_lng = {
        'lat': emp_lat,
        'lng': emp_lng
    }
    
    matching_customers = Customer.objects.filter(zip_code=logged_in_employee.zip_code).filter(weekly_pickup=today_weekday).exclude(date_of_last_pickup=today).exclude(suspend_start__lte=today, suspend_end__gte=today)
    customer_onetime_pickup = Customer.objects.filter(zip_code=logged_in_employee.zip_code).filter(one_time_pickup=today).exclude(date_of_last_pickup=today).exclude(suspend_start__lte=today, suspend_end__gte=today)

    customer_geocodes = []
    for customer in matching_customers:
        customer_full_address = customer.address + ' '+ customer.zip_code
        customer_geocode = geocode_address(customer_full_address)
        lat = customer_geocode['lat']
        lng = customer_geocode['lng']
        formatted_lat_lng = {
            'lat': lat,
            'lng': lng
        }
        customer_geocodes.append(formatted_lat_lng)
    for customer in customer_onetime_pickup:
        customer_full_address = customer.address + ' '+ customer.zip_code
        customer_geocode = geocode_address(customer_full_address)
        lat = customer_geocode['lat']
        lng = customer_geocode['lng']
        formatted_lat_lng = {
            'lat': lat,
            'lng': lng
        }
        customer_geocodes.append(formatted_lat_lng)

    context = {
        'matching_customers': matching_customers,
        'customer_geocodes': customer_geocodes,
        'employee_lat_lng': employee_lat_lng,
        'customer_onetime_pickup': customer_onetime_pickup,
        'logged_in_employee': logged_in_employee
    }
    return render(request, 'employees/index.html', context)

#Display all ccustomers in zip code, option to filter by pickup day
@login_required
def my_accounts(request):
    user = request.user
    logged_in_employee = Employee.objects.get(user=user)
    Customer = apps.get_model('customers.Customer')
    matching_customers = []
    
    if(request.method == "POST" and request.POST.get("pickup_day") != "All"):
        pickup_day = request.POST.get("pickup_day")
        all_customers = Customer.objects.filter(weekly_pickup=pickup_day)
    else:
        all_customers = Customer.objects.all()

    context = {
        'matching_customers': all_customers
    }

    return render(request, 'employees/my_accounts.html', context)

@login_required
def create(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        zip_code = request.POST.get('zip_code')
        new_customer = Employee(user=user, first_name=first_name, last_name=last_name, zip_code=zip_code)
        new_customer.save()
        context = {
            'logged_in_employee': new_customer
        }
        return render(request, 'employees/index.html', context)
    else:
         return render(request, 'employees/create.html')

@login_required
def confirm_pickup(request, customer_id):
    Customer = apps.get_model('customers.Customer')
    customer = Customer.objects.get(id=customer_id)
    if request.method == "POST":
        customer.balance += 20
        customer.date_of_last_pickup = date.today()
        customer.save()
        
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'customer': customer
        } 
        return render(request, 'employees/confirm_pickup.html', context)

        

@login_required
def customer_profile(request, customer_id):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)

    Customer = apps.get_model('customers.Customer')
    customer = Customer.objects.get(pk=customer_id)
    customer_address = customer.address
    customer_zip = customer.zip_code
    customer_full_address = customer_address + ' '+ customer_zip
    customer_geocode = geocode_address(customer_full_address)
    #customer_url = urllib.parse.quote(customer_full_address)
    
    context = {'customer': customer,
                'logged_in_employee': logged_in_employee,
                'customer_full_address': customer_full_address,
                'customer_geocode': customer_geocode,
                'cust_lat': customer_geocode['lat'],
                'cust_long': customer_geocode['lng']
                }
    
    return render (request, 'employees/customer_profile.html', context)

def geocode_address(address):
    geo_request = requests.get(f'https://maps.googleapis.com/maps/api/geocode/json?address={address}&key=APIKEYHERE!')
    if geo_request.status_code == 200:
        response = geo_request.json()
        lat_lng = response['results'][0]['geometry']['location']
        return lat_lng
        #default returns Uluru, as to not break app
    else: 
        return { 'lat': -25.344, 'lng': 131.036 }

def edit(request):
    if request.method == "POST":
        user = request.user
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        zip_code = request.POST.get('zip_code')
        new_customer = Employee(user=user, first_name=first_name, last_name=last_name, zip_code=zip_code)
        new_customer.save()
        return render(request, 'employees/index.html')
    else:
         return render(request, 'employees/create.html')

@login_required
def edit_profile(request):
    logged_in_user = request.user
    logged_in_employee = Employee.objects.get(user=logged_in_user)
    if request.method == "POST":
        name_from_form = request.POST.get('first_name')
        last_name_from_form = request.POST.get('last_name')
        zip_from_form = request.POST.get('zip_code')
        logged_in_employee.first_name = name_from_form
        logged_in_employee.last_name = last_name_from_form
        logged_in_employee.zip_code = zip_from_form
        logged_in_employee.save()
        return HttpResponseRedirect(reverse('employees:index'))
    else:
        context = {
            'logged_in_employee': logged_in_employee
        }
        return render(request, 'employees/edit_profile.html', context)