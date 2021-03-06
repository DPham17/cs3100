from django.shortcuts import render
from django.http import HttpResponse
import json
from tokenapi.http import JsonResponse, JsonError
from tokenapi.decorators import token_required
from tracker.models import Course, Homework, Category, Grade
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from tracker.utils import get, check, rm, edit, getObjects, isError, singularOp

def index(request):
    return HttpResponse("This is the API for chalkboard.")

@csrf_exempt
def register(request):
    """
        "username": username
        "password": password
        "email": email
    """
    if check(request) is not None:
        return check(request)
    data = json.loads(request.body.decode('utf-8'))

    #Username
    if not 'username' in data:
        return JsonError("'username' is a required field.")
    if len(data['username']) < 4 or len(data['username']) > 25:
        return JsonError("Usernames must be between 4 and 25 characters.")
    if User.objects.filter(username=data['username']).exists():
        return JsonError("Username already exists")
    
    if not 'password' in data:
        return JsonError("'password' is a required field.")
    if len(data['password']) < 5:
        return JsonError("A password must be at least 5 characters long.")
    
    if not 'email' in data:
        return JsonError("'email' is a required field.")
    if len(data['email']) < 5:
        return JsonError("Email is too short")

    user = User(username=data['username'], email=data['email'])
    user.set_password(data['password'])
    user.save()

    return JsonResponse({"success": True, "data": {"id": user.id}})



@token_required
def addCategory(request):
    """
    name: category name

    Optional:
        weight:    <weight>
    """
    if check(request) is not None:
        return check(request)
    data = json.loads(request.body.decode('utf-8'))

    if not 'name' in data:
        return JsonError("A name field is required to create a category.")
    if len(data['name']) < 4:
        return JsonError("The name provided for the category is too short.")

    cat = Category(name=data['name'])

    if 'weight' in data:
        cat.weight = float(data['weight'])

    cat.save()
    
    return JsonResponse({"data": {"id": cat.id}, "success": True})

@token_required
def addCourse(request):
    """
    name: coursename
    school: school name
    """
    if check(request) is not None:
        return check(request)
    data = json.loads(request.body.decode('utf-8'))

    if not 'name' in data:
        return JsonError("A name field is required to create a course.")
    if not 'school' in data:
        return JsonError("A school field is required to create a course.")
    if len(data['name']) < 4:
        return JsonError("The name provided for the course is too short.")
    if len(data['school']) < 4:
        return JsonError("The name provided for the school is too short.")

    course = Course(name=data['name'], school=data['school'])
    course.save()
    
    return JsonResponse({"data": {"id": course.id}, "success": True})

@token_required
def addHomework(request):
    """
       categoryid: <categoryid>
       name:      <name>

       
       optional:
         points_possible: <# points possible>
    """
    if check(request) is not None:
        return check(request)
    data = json.loads(request.body.decode('utf-8'))
    
    if not 'name' in data:
        return JsonError("A name field is required to create a homework.")
    if not 'categoryid' in data:
        return JsonError("A categoryid field is required to create a homework.")
    if len(data['name']) < 4:
        return JsonError("The name provided for the homework is too short.")
    
    if not Category.objects.filter(id=data['categoryid']).exists():
        return JsonError("The categoryid provided for the homework isn't valid.")
    
    homework = Homework(name=data['name'], category=Category.objects.get(id=data['categoryid'])) 

    if 'points_possible' in data:
        homework.points_possible = data['points_possible']

    homework.save()

    return JsonResponse({"data": { "id": homework.id }, "success": True})

@token_required
def addGrade(request):
    """
        courseid: <courseid>
        homeworkid: <homeworkid>
        
        optional:
         points_received: <# points>

    """

    if check(request) is not None:
        return check(request)
    data = json.loads(request.body.decode('utf-8'))

    if not 'courseid' in data:
        return JsonError("A courseid field is required to create a grade.")
    if not 'homeworkid' in data:
        return JsonError("A homeworkid field is required to create a grade.")

    if not Course.objects.filter(id=data['courseid']).exists():
        return JsonError("The courseid provided for the grade isn't valid.")

    if not Homework.objects.filter(id=data['homeworkid']).exists():
        return JsonError("The homeworkid provided for the grade isn't valid.")

    grade = Grade(course=Course.objects.get(id=data['courseid']), homework=Homework.objects.get(id=data['homeworkid']), 
            user=request.user)

    if 'points_received' in data:
        grade.points_received = data['points_received']

    grade.save()

    return JsonResponse({"data": { "id": grade.id }, "success": True})

@token_required
def getCourse(request):
    return get(request, Course)

@token_required
def getGrade(request):
    return get(request, Grade)

@token_required
def getCategory(request):
    return get(request, Category)

@token_required
def getHomework(request):
    return get(request, Homework)

@token_required
def editCourse(request):
    return edit(request, Course)

@token_required
def editGrade(request):
    return edit(request, Grade)

@token_required
def editCategory(request):
    return edit(request, Category)

@token_required
def editHomework(request):
    return edit(request, Homework)

@token_required
def rmGrade(request):
    return rm(request, Grade)

@token_required
def getCategoriesForCourse(request):
    response = [ ]

    res = check(request)
    if res is not None:
        return res

    data = json.loads(request.body.decode('utf-8'))

    course = getObjects(data, Course)
    if isError(course):
        return course

    res = singularOp(course, Course, op="Course2cat")
    if res is not None:
        return res
    
    coursefil = course[0]
    grades = Grade.objects.filter(course=coursefil)

    for grade in grades:
        response.append(grade.homework.category.id)
    
    # Flatten
    response = list(set(response))
    responsearr = []
    for cid in response:
        responsearr.append(Category.objects.filter(id=cid).values()[0])

    return JsonResponse({"data": responsearr}) 
    
