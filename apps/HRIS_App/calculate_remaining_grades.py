from .models import Employee, Region
from django.db.models import Count


def calculate_remaining_grades(region):
    # Get the total number of employees in the same region
    total_employees = Employee.objects.filter(region=region).count()
    if total_employees == 0:
        return {}

    # Fetch the Region instance
    try:
        region_instance = Region.objects.get(name=region)
    except Region.DoesNotExist:
        # Return empty dict if region doesn't exist
        return {}

    # Define the number of employees allowed per grade based on percentage
    grade_limits = {
        'Excellent': int(total_employees * region_instance.A_Grade_seats / 100),
        'Very Good': int(total_employees * region_instance.B_Grade_seats / 100),
        'Good': int(total_employees * region_instance.C_Grade_seats / 100),
        'Needs Improvement': int(total_employees * region_instance.D_Grade_seats / 100),
        'Unsatisfactory': int(total_employees * region_instance.E_Grade_seats / 100),
    }

    # Convert to integers, with rounding to handle fractional employees
    grade_limits = {grade: int(limit) for grade, limit in grade_limits.items()}

    # Calculate the remaining employees after applying the floor values
    assigned_employees = sum(grade_limits.values())
    remaining_employees = total_employees - assigned_employees
    
    # Distribute the remaining employees (this could go to the grade with the smallest number)
    if remaining_employees > 0:
        # Add remaining employees to the lowest grade
        grade_limits['Unsatisfactory'] += remaining_employees

    total_grade_limits = grade_limits.copy()  # To preserve the original limits for later use

    # Count current assignments
    current_grade_counts = Employee.objects.filter(region=region).values('grade_assignment').annotate(count=Count('id'))

    # Subtract current counts from grade limits
    for entry in current_grade_counts:
        grade = entry['grade_assignment']
        count = entry['count']
        if grade in grade_limits:
            grade_limits[grade] -= count

    # Collect awarded grades (assuming these are the grades assigned to employees)
    awarded_grades = {}
    for entry in current_grade_counts:
        grade = entry['grade_assignment']
        count = entry['count']
        awarded_grades[grade] = count

    # Prepare final data to return
    remaining_grades = []
    for grade, remaining in grade_limits.items():
        total = total_grade_limits.get(grade, 0)
        awarded = awarded_grades.get(grade, 0)
        remaining_grades.append({
            'grade': grade,
            'remaining': remaining,
            'total': total,
            'awarded': awarded,
        })

    return remaining_grades
