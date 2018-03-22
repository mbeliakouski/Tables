import csv
import datetime
import logging

from django.contrib.auth.models import User
from django.shortcuts import render, redirect

from test_app.forms import UploadFileForm
from test_app.models import Employee, Post
from test_app.models import Tax
import math

logger = logging.getLogger(__name__)
PRE_TAX = 'pre_tax'
AMOUNT = 'amount'
RECORDS_PER_PAGE = 20


def home(request):
    if request.method == 'GET':
        # if request.user.is_authenticated:
        return render(request, 'home.html', {'nbar': 'home'})
        # else:
        #     return HttpResponseRedirect('/login')
    else:
        return render_error(request, 'Only GET is allowed')


def post(request, post_id):
    if request.method == 'GET':
        taxes = Tax.objects.filter(post=post_id).order_by('tax_date')
        amount_result = dict()
        amount_total = 0
        pre_amount_total = 0

        for tax in taxes:
            amount_total += tax.amount
            pre_amount_total += tax.pre_tax_amount
            month = tax.tax_date.strftime('%B %Y')
            if month not in amount_result:
                amount_result.update({month: {}})

            if PRE_TAX in amount_result[month]:
                amount_result[month][PRE_TAX] += tax.pre_tax_amount
            else:
                amount_result[month][PRE_TAX] = tax.pre_tax_amount

            if AMOUNT in amount_result[month]:
                amount_result[month][AMOUNT] += tax.amount
            else:
                amount_result[month][AMOUNT] = tax.amount

        return render(request, 'post.html',
                      {'data': amount_result.items(),
                       'amount_total': round(amount_total, 2),
                       'pre_amount_total': round(pre_amount_total, 2)})


def upload(request):
    if request.user.is_authenticated:
        if request.method == 'GET':
            form = UploadFileForm()
            return render(request, 'upload.html', {'form': form, 'nbar': 'upload'})
        if request.method == 'POST':
            form = UploadFileForm(request.POST, request.FILES)

            if form.is_valid():
                try:
                    reader = csv.DictReader(request.FILES['file'].read().decode('utf-8').splitlines())
                    tax_list = list()
                    posted = Post.objects.create(posted_by=User.objects.get(id=request.user.id))

                    for row in reader:
                        employee_name = row["employee name"]
                        employee_address = row["employee address"]

                        if not Employee.objects.filter(name=employee_name, address=employee_address).exists():
                            employee = Employee.objects.create(name=employee_name, address=employee_address)
                        else:
                            employee = Employee.objects.get(name=employee_name, address=employee_address)

                        tax = Tax()
                        tax.employee = employee
                        str_date = row["date"]
                        tax.tax_date = datetime.datetime.strptime(str_date, '%m/%d/%Y')
                        tax.name = row['tax name']
                        tax.amount = float(row['tax amount'].replace(',', ''))
                        tax.category = row['category']
                        tax.pre_tax_amount = float(row['pre-tax amount'].replace(',', ''))
                        tax.exp_description = row['expense description']
                        tax.post = posted
                        tax_list.append(tax)

                    Tax.objects.bulk_create(tax_list)

                    return redirect(f'/post/{posted.id}')
                except KeyError:
                    return render_error(request, 'Bad file format')

        return render_error(request, 'Only POST and GET are allowed')
    else:
        return redirect('login')


def posts(request):
    if request.user.is_authenticated:
        try:
            page = int(request.GET.get('page', 1))
        except ValueError:
            return render_error(request, 'Invalid page number')
        if not page > 0:
            return render_error(request, 'Invalid page number')
        pages_count = math.ceil(Tax.objects.all().count() / RECORDS_PER_PAGE)
        taxes = Tax.objects.all()[RECORDS_PER_PAGE * (page - 1):page * RECORDS_PER_PAGE]

        return render(request, 'posts.html', {'data': taxes, 'nbar': 'posts',
                                              'pages': range(1, int(pages_count + 1)),
                                              'active_page': page})
    else:
        return redirect('login')


def render_error(request, message, status=400):
    return render(request, 'error.html', {'message': message}, status=status)
