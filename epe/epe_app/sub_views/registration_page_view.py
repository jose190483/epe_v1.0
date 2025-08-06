from django.shortcuts import render, redirect
from ..forms import CreateUserForm,UserextForm
from django.contrib import messages

def registration_page(request):
    if request.method == 'POST':
        form = CreateUserForm(request.POST)
        user_ext_form=UserextForm(request.POST)
        if form.is_valid() and user_ext_form.is_valid():
            print("Form is Valid")
            user= form.save()
            user_ext= user_ext_form.save(commit=False)
            user_ext.user=user
            user_ext.save()
            user_name = form.cleaned_data.get('first_name')
            messages.success(request,f'Account created for {user_name}')
            return redirect('login_page')
        else:
            # Show errors if the forms are not valid
            print("Form is not Valid")
            messages.error(request, 'Please correct the errors below.')
            
        for field, errors in form.errors.items():
            for error in errors:
                print(f"Error in {field}: {error}")
                messages.error(request, f"Error in {field}: {error}")
        messages.error(request, 'Record Not Updated Successfully')
    else:
        form = CreateUserForm()
        user_ext_form = UserextForm()

    context = {'user_ext_form': user_ext_form,'form': form}
    return render(request, "epe_app/registration_form.html",context)

