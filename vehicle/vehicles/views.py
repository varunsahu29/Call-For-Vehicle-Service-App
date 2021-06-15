from django.http.response import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import Group
from django.shortcuts import render,redirect
from vehicles import forms,models
from django.contrib.auth.decorators import login_required,user_passes_test
from django.db.models import Q,Sum
#########################################################################################################################
# HOME VIEWS BEGINS
#########################################################################################################################
def home_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'vehicles/index.html')
def afterlogin_view(request):
    if is_customer(request.user):
        return redirect('customer-dashboard')
    elif is_mechanic(request.user):
        accountapproval=models.Mechanic.objects.all().filter(user_id=request.user.id,status=True)
        if accountapproval:
            return redirect('mechanic-dashboard')
        else:
            return render(request,'vehicles/mechanic/wait_for_approval.html')
    else:
        return redirect('/admin')
def aboutus_view(request):
    if(request.user.groups.filter(name='CUSTOMER').exists()):
        return render(request,'vehicles/customer/aboutus.html')
    elif(request.user.groups.filter(name='MECHANIC').exists()):
        return render(request,'vehicles/mechanic/aboutus.html')
    else:
        return render(request,'vehicles/aboutus.html')
def contactus_view(request):
    sub = forms.ContactusForm()
    if request.method == 'POST':
        sub = forms.ContactusForm(request.POST)
        if sub.is_valid():
            email = sub.cleaned_data['Email']
            name=sub.cleaned_data['Name']
            message = sub.cleaned_data['Message']
            print(email,name,message)
            return redirect('')
    if(request.user.groups.filter(name='CUSTOMER').exists()):
        return render(request,'vehicles/customer/contactus.html',{'form':sub})
    elif(request.user.groups.filter(name='MECHANIC').exists()):
        return render(request,'vehicles/mechanic/contactus.html',{'form':sub})
    else:
        return render(request, 'vehicles/contactus.html', {'form':sub})
#########################################################################################################################
# Home View Ends:
#########################################################################################################################




#########################################################################################################################
# Customers View Begins:
#########################################################################################################################
def customer_signup_view(request):
    userForm=forms.CustomerUserForm()
    customerForm=forms.CustomerForm()
    mydict={'userForm':userForm,'customerForm':customerForm}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST)
        customerForm=forms.CustomerForm(request.POST,request.FILES)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customer=customerForm.save(commit=False)
            customer.user=user
            customer.save()
            my_customer_group = Group.objects.get_or_create(name='CUSTOMER')
            my_customer_group[0].user_set.add(user)
        return redirect('customerlogin')
    return render(request,'vehicles/customer/signup.html',mydict)
def customerclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'vehicles/customer/click.html')
def is_customer(user):
    return user.groups.filter(name='CUSTOMER').exists()
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_dashboard_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    work_in_progress=models.Request.objects.all().filter(customer_id=customer.id,status='Repairing').count()
    work_completed=models.Request.objects.all().filter(customer_id=customer.id).filter(Q(status="Repairing Done") | Q(status="Released")).count()
    new_request_made=models.Request.objects.all().filter(customer_id=customer.id).filter(Q(status="Pending") | Q(status="Approved")).count()
    bill=models.Request.objects.all().filter(customer_id=customer.id).filter(Q(status="Repairing Done") | Q(status="Released")).aggregate(Sum('cost'))
    if(bill['cost__sum']==None):
       bill['cost__sum']=0
    dict={
    'work_in_progress':work_in_progress,
    'work_completed':work_completed,
    'new_request_made':new_request_made,
    'bill':bill['cost__sum'],
    'customer':customer,
    }
    return render(request,'vehicles/customer/dashboard.html',context=dict)
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'vehicles/customer/profile.html',{'customer':customer})
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def edit_customer_profile_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=customer.user_id)
    userForm=forms.CustomerUserForm(instance=user)
    customerForm=forms.CustomerForm(request.FILES,instance=customer)
    mydict={'userForm':userForm,'customerForm':customerForm,'customer':customer}
    if request.method=='POST':
        userForm=forms.CustomerUserForm(request.POST,instance=user)
        customerForm=forms.CustomerForm(request.POST,instance=customer)
        if userForm.is_valid() and customerForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            customerForm.save()
            return HttpResponseRedirect('customer-dashboard')
    return render(request,'vehicles/customer/edit_profile.html',context=mydict)

@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_request_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    return render(request,'vehicles/customer/request.html',{'customer':customer})
    
def customer_view_request(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    enquiries=models.Request.objects.all().filter(customer_id=customer.id , status="Pending")
    return render(request,'vehicles/customer/view_request.html',{'customer':customer,'enquiries':enquiries})
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_delete_request_view(request,pk):
    enquiry=models.Request.objects.get(id=pk)
    if(enquiry.status=='Pending'):
        enquiry.delete()
    else:
        print("You Can Only delete Pending Request")
    return redirect('customer-view-request')
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_add_request(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    enquiry=forms.RequestForm()
    if request.method=='POST':
        enquiry=forms.RequestForm(request.POST)
        if enquiry.is_valid():
            customer=models.Customer.objects.get(user_id=request.user.id)
            enquiry_x=enquiry.save(commit=False)
            enquiry_x.customer=customer
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('customer-dashboard')
    return render(request,'vehicles/customer/add-request.html',{'enquiry':enquiry,'customer':customer})
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_approved_request(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    enquiries=models.Request.objects.all().filter(customer_id=customer.id).exclude(status='Pending')
    return render(request,'vehicles/customer/approved_request.html',{'customer':customer,'enquiries':enquiries})
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_approved_request_invoice(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    enquiries=models.Request.objects.all().filter(customer_id=customer.id).exclude(status='Pending')
    return render(request,'vehicles/customer/approved_request_invoice.html',{'customer':customer,'enquiries':enquiries})
@login_required(login_url='customerlogin')
@user_passes_test(is_customer)
def customer_feedback_view(request):
    customer=models.Customer.objects.get(user_id=request.user.id)
    feedback=forms.FeedbackForm()
    if request.method=='POST':
        feedback=forms.FeedbackForm(request.POST)
        if feedback.is_valid():
            feedback.save()
        else:
            print("form is invalid")
        return redirect('customer-dashboard')
    return render(request,'vehicles/customer/feedback.html',{'feedback':feedback,'customer':customer})
#########################################################################################################################
# Customers View End:
#########################################################################################################################



#########################################################################################################################
# Mechanic View Begins:
#########################################################################################################################

def mechanicclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return render(request,'vehicles/mechanic/click.html')



def mechanic_signup_view(request):
    userForm=forms.MechanicUserForm()
    mechanicForm=forms.MechanicForm()
    mydict={'userForm':userForm,'mechanicForm':mechanicForm}
    if request.method=='POST':
        userForm=forms.MechanicUserForm(request.POST)
        mechanicForm=forms.MechanicForm(request.POST,request.FILES)
        if userForm.is_valid() and mechanicForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            mechanic=mechanicForm.save(commit=False)
            mechanic.user=user
            mechanic.save()
            my_mechanic_group = Group.objects.get_or_create(name='MECHANIC')
            my_mechanic_group[0].user_set.add(user)
        return redirect('mechaniclogin')
    return render(request,'vehicles/mechanic/signup.html',mydict)
def is_mechanic(user):
    return user.groups.filter(name='MECHANIC').exists()

@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_dashboard_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    work_in_progress=models.Request.objects.all().filter(mechanic_id=mechanic.id,status='Repairing').count()
    work_completed=models.Request.objects.all().filter(mechanic_id=mechanic.id,status='Repairing Done').count()
    new_work_assigned=models.Request.objects.all().filter(mechanic_id=mechanic.id,status='Approved').count()
    salary=mechanic.salary
    if(salary):
        pass
    else:
        salary=0
    dict={
    'work_in_progress':work_in_progress,
    'work_completed':work_completed,
    'new_work_assigned':new_work_assigned,
    'salary':salary,
    'mechanic':mechanic,
    }
    return render(request,'vehicles/mechanic/dashboard.html',context=dict)
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_profile_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    return render(request,'vehicles/mechanic/profile.html',{'mechanic':mechanic})
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def edit_mechanic_profile_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    user=models.User.objects.get(id=mechanic.user_id)
    userForm=forms.MechanicUserForm(instance=user)
    mechanicForm=forms.MechanicForm(request.FILES,instance=mechanic)
    mydict={'userForm':userForm,'mechanicForm':mechanicForm,'mechanic':mechanic}
    if request.method=='POST':
        userForm=forms.MechanicUserForm(request.POST,instance=user)
        mechanicForm=forms.MechanicForm(request.POST,request.FILES,instance=mechanic)
        if userForm.is_valid() and mechanicForm.is_valid():
            user=userForm.save()
            user.set_password(user.password)
            user.save()
            mechanicForm.save()
            return redirect('mechanic-profile')
    return render(request,'vehicles/mechanic/edit_profile.html',context=mydict)
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def work_assigned_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    works=models.Request.objects.all().filter(mechanic_id=mechanic.id)
    return render(request,'vehicles/mechanic/work_assigned.html',{'works':works,'mechanic':mechanic})
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def update_status_view(request,pk):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    updateStatus=forms.MechanicUpdateStatusForm()
    if request.method=='POST':
        updateStatus=forms.MechanicUpdateStatusForm(request.POST)
        if updateStatus.is_valid():
            enquiry_x=models.Request.objects.get(id=pk)
            enquiry_x.status=updateStatus.cleaned_data['status']
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/mechanic-work-assigned')
    return render(request,'vehicles/mechanic/update_status.html',{'updateStatus':updateStatus,'mechanic':mechanic})
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def update_status_view(request,pk):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    updateStatus=forms.MechanicUpdateStatusForm()
    if request.method=='POST':
        updateStatus=forms.MechanicUpdateStatusForm(request.POST)
        if updateStatus.is_valid():
            enquiry_x=models.Request.objects.get(id=pk)
            enquiry_x.status=updateStatus.cleaned_data['status']
            enquiry_x.save()
        else:
            print("form is invalid")
        return HttpResponseRedirect('/mechanic-work-assigned')
    return render(request,'vehicles/mechanic/update_status.html',{'updateStatus':updateStatus,'mechanic':mechanic})
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def salary_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    workdone=models.Request.objects.all().filter(mechanic_id=mechanic.id).filter(Q(status="Repairing Done") | Q(status="Released"))
    return render(request,'vehicles/mechanic/salary.html',{'workdone':workdone,'mechanic':mechanic})
@login_required(login_url='mechaniclogin')
@user_passes_test(is_mechanic)
def mechanic_feedback_view(request):
    mechanic=models.Mechanic.objects.get(user_id=request.user.id)
    feedback=forms.FeedbackForm()
    if request.method=='POST':
        feedback=forms.FeedbackForm(request.POST)
        if feedback.is_valid():
            feedback.save()
        else:
            print("form is invalid")
        return redirect('mechanic-dashboard')
    return render(request,'vehicles/mechanic/feedback.html',{'feedback':feedback,'mechanic':mechanic})
#########################################################################################################################
# Mechanic View Ends:
#########################################################################################################################
#for showing signup/login button for ADMIN(by varun)
def adminclick_view(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('afterlogin')
    return HttpResponseRedirect('adminlogin')