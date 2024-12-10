from django.contrib import admin
from account.models import User, CorrespondenceAddress  
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import ResidentialAddress, EducationDetailsPassed, EducationDetailsAppearing


class UserModelAdmin(BaseUserAdmin):
    

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserModelAdmin
    # that reference specific fields on auth.User.
    list_display = ["id","email", "name","tc", "is_admin"]
    list_filter = ["is_admin"]
    fieldsets = [
        ("User Credentials", {"fields": ["email", "password"]}),
        ("Personal info", {"fields": ["name", "tc"]}),
        ("Permissions", {"fields": ["is_admin"]}),
    ]
    # add_fieldsets is not a standard ModelAdmin attribute. UserModelAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    add_fieldsets = [
        (
            None,
            {
                "classes": ["wide"],
                "fields": ["email", "name", "tc" "password1", "password2"],
            },
        ),
    ]
    search_fields = ["email"]
    ordering = ["email", "id"]
    filter_horizontal = []


# Now register the new UserModelAdmin...
admin.site.register(User, UserModelAdmin)



class CorrespondenceAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'streetAddress', 'citySelected', 'selectedState', 'pincode')  # Customize as needed


# Register CorrespondenceAddress model
admin.site.register(CorrespondenceAddress, CorrespondenceAddressAdmin)




class ResidentialAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'streetAddress', 'citySelected', 'selectedState', 'pincode')  # Customize as needed

# Register ResidentialAddress with the custom admin class
admin.site.register(ResidentialAddress, ResidentialAddressAdmin)







class EducationDetailsPassedAdmin(admin.ModelAdmin):
    list_display = ['user', 'standard', 'board', 'school', 'roll_no', 'marks_obtained']
    search_fields = ['user__username', 'standard', 'board', 'school', 'roll_no']
    list_filter = ['standard']

admin.site.register(EducationDetailsPassed, EducationDetailsPassedAdmin)


class EducationDetailsAppearingAdmin(admin.ModelAdmin):
    list_display = ['user', 'standard', 'board', 'school', 'registration_no']
    search_fields = ['user__username', 'standard', 'board', 'school', 'registration_no']
    list_filter = ['standard']

admin.site.register(EducationDetailsAppearing, EducationDetailsAppearingAdmin)






