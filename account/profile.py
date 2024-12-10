def get_profile_completion_status(user):
    """
    Checks if the user's profile is complete by verifying data in all associated models.
    Returns a dictionary with completion status and missing fields.
    """
    profile_status = {
        "user_details": False,
        "correspondence_address": False,
        "residential_address": False,
        "education_appearing": False,
        "education_passed": False,
        "missing_fields": [],
        "is_complete": False,
    }

    # Check User model fields
    user_required_fields = [user.name, user.guardianName, user.dob, user.aadhar]
    if all(user_required_fields):
        profile_status["user_details"] = True
    else:
        profile_status["missing_fields"].append("User Details (name, guardianName, dob, aadhar)")

    # Check Correspondence Address
    if hasattr(user, "correspondence_address"):
        correspondence = user.correspondence_address
        if all(
            [
                correspondence.countrySelected,
                correspondence.streetAddress,
                correspondence.localityOrVillage,
                correspondence.selectedState,
                correspondence.citySelected,
                correspondence.pincode,
            ]
        ):
            profile_status["correspondence_address"] = True
        else:
            profile_status["missing_fields"].append("Correspondence Address")
    else:
        profile_status["missing_fields"].append("Correspondence Address (missing)")

    # Check Residential Address
    if hasattr(user, "residential_address"):
        residential = user.residential_address
        if all(
            [
                residential.countrySelected,
                residential.streetAddress,
                residential.localityOrVillage,
                residential.selectedState,
                residential.citySelected,
                residential.pincode,
            ]
        ):
            profile_status["residential_address"] = True
        else:
            profile_status["missing_fields"].append("Residential Address")
    else:
        profile_status["missing_fields"].append("Residential Address (missing)")

    # Check Education Details Appearing
    if hasattr(user, "education_details_appearing"):
        education_appearing = user.education_details_appearing
        if all(
            [
                education_appearing.standard,
                education_appearing.board,
                education_appearing.school,
                education_appearing.registration_no,
                education_appearing.subjects,
            ]
        ):
            profile_status["education_appearing"] = True
        else:
            profile_status["missing_fields"].append("Education Details Appearing")
    else:
        profile_status["missing_fields"].append("Education Details Appearing (missing)")

    # Check Education Details Passed
    if hasattr(user, "education_details_passed"):
        education_passed = user.education_details_passed
        if all(
            [
                education_passed.standard,
                education_passed.board,
                education_passed.school,
                education_passed.roll_no,
                education_passed.marks_obtained,
                education_passed.subjects,
            ]
        ):
            profile_status["education_passed"] = True
        else:
            profile_status["missing_fields"].append("Education Details Passed")
    else:
        profile_status["missing_fields"].append("Education Details Passed (missing)")

    # Determine overall completion
    profile_status["is_complete"] = all(
        [
            profile_status["user_details"],
            profile_status["correspondence_address"],
            profile_status["residential_address"],
            profile_status["education_appearing"],
            profile_status["education_passed"],
        ]
    )

    return profile_status
