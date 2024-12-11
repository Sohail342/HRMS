from HRIS_App.models import Employee
from django.shortcuts import render
from django.db.models import Count, Q

def grade_distribution_view(request):
    GRADE_CHOICES = [
        'A - Excellent',
        'B - Very Good',
        'C - Good',
        'D - Needs Improvement',
        'E - Unsatisfactory',
        'Not Assigned',
    ]

    regions = Employee.objects.values_list('region__name', flat=True).distinct()

    grade_data = []
    totals = {grade: 0 for grade in GRADE_CHOICES}
    totals['total_employees'] = 0

    for region in regions:
        branch_data = {'branch': region, 'total_employees': 0}

        for grade in GRADE_CHOICES:
            if grade == "Not Assigned":
                count = Employee.objects.filter(region__name=region, grade_assignment__isnull=True).count()
            else:
                count = Employee.objects.filter(region__name=region, grade_assignment=grade).count()

            branch_data[grade] = count
            totals[grade] += count  # Add to totals for this grade

        branch_data['total_employees'] = Employee.objects.filter(region__name=region, is_admin=False).count()
        totals['total_employees'] += branch_data['total_employees'] 

        grade_data.append(branch_data)

    context = {
        'grade_data': grade_data,
        'grades': GRADE_CHOICES,
        'totals': totals,
    }
    return render(request, 'group_head/grade_distribution.html', context)


