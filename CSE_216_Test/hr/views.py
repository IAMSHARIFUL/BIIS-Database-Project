from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse
# from .forms import *
from django.shortcuts import redirect
from django.forms.formsets import formset_factory
from django.db import connection
import cx_Oracle
import hashlib
# This is logout line : request.session.flush()
from numpy.core import long
def term_result(request):
    return render(request, 'term_result.html')
def  list_jobs (request):
    # cursor = connection.cursor()
    # sql = "INSERT INTO JOBS VALUES(%s,%s,%s,%s)"
    # cursor.execute(sql,['NEW_JOB','Something New',4000,8000])
    # connection.commit()
    # cursor.close()
    cursor = connection.cursor()
    sql = "SELECT ROLL_NUMBER, STUDENT_NAME FROM STUDENT"
    cursor.execute(sql)
    result = cursor.fetchall()
    # cursor = connection.cursor()
    # sql = "SELECT * FROM JOBS WHERE MIN_SALARY=%s"
    # cursor.execute(sql,[4000])
    # result = cursor.fetchall()
    cursor.close()
    dict_result = []
    for r in result:
        job_id = r[0]
        nam = r[1]
        row = {'job_id':job_id, 'nam':nam}
        dict_result.append(row)

    #return render(request,'list_jobs.html',{'jobs' : Job.objects.all()})
    return render(request,'list_jobs.html',{'jobs' : dict_result})

def student_marksheet(request):
    usar = request.POST.get("username", "")
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    student = {'name': "irri", 'year': 2017, 'dept': "Comp.", 'lev': 1, 'ter': 1, 'usar': usar, 'credit': 0,
               'cgpa': 0}
    cursor.execute('''SELECT S.STUDENT_NAME,S.YEAR,D.DEPT_NAME,S.LEVEL_,S.TERM,NVL(S.TOTAL_CREDIT,0),NVL(S.CGPA,0)
    FROM STUDENT S LEFT OUTER JOIN DEPARTMENT D ON(S.DEPT_ID=D.DEPT_ID)
    WHERE LPAD(TO_CHAR(MOD(S.YEAR,100)*100000+S.DEPT_ID*1000+S.ROLL_NUMBER),7,'0')=:usar''', [usar])
    row = cursor.fetchall()
    marks_code_prefix=int(usar)
    marks_code_prefix=200000000+marks_code_prefix
    for r in row:
        student['name'] = r[0]
        student['year'] = r[1]
        student['dept'] = r[2]
        student['lev'] = r[3]
        student['ter'] = r[4]
        student['credit'] = r[5]
        student['cgpa'] = r[6]
    lavl=student['lev']
    tarm=student['ter']
    cursor.execute(
        '''SELECT (D.DEPT_CODE||TO_CHAR(R.LEVEL_)||LPAD(TO_CHAR(R.COURSE_NUMBER),2,'0')) , C.COURSE_NAME , C.CREDIT, C.DEPT_ID, C.LEVEL_,C.COURSE_NUMBER  FROM REGISTRATION R JOIN DEPARTMENT D ON (D.DEPT_ID=R.COURSE_DEPT_ID)  JOIN COURSE C ON (R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER) WHERE LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar AND TO_CHAR(R.LEVEL_)=:lavl AND TO_CHAR(C.TERM)=:tarm''',
        [usar, lavl, tarm])
    # row = dictfetchall(cursor)
    row = cursor.fetchall()
    dict = []
    for r in row:
        blank = False
        course_id = r[0]
        course_name = r[1]
        full_marks = r[2]*100
        marks_code=marks_code_prefix*100000+r[3]*1000+r[4]*100+r[5]
        d = {'course_id': course_id, 'course_name': course_name, 'full_marks': full_marks,'marks_code':marks_code}
        dict.append(d)
    conn.close()
    return render(request, 'set_student_marks.html',
                  {'course_list': dict, 'lavl': lavl, 'tarm': tarm, 'student': student})

def marks_are_set(request):
    marks=request.POST.getlist("marks[]","")
    courses=request.POST.getlist("courses[]","")
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    YY=2017
    DD=5
    RR=119
    i=0;
    while i<len(marks):
        #return redirect('/login')
        reg_id=int(courses[i])
        print(reg_id)
        CNUM=reg_id%100
        CLEVEL=reg_id%1000
        CLEVEL=CLEVEL//100
        CDEPT_ID=reg_id%100000
        CDEPT_ID=CDEPT_ID//1000
        ROLL=reg_id%100000000
        ROLL=ROLL//100000
        SDEPT_ID=reg_id%10000000000
        SDEPT_ID=SDEPT_ID//100000000
        Y=reg_id//10000000000
        YY=Y
        DD=SDEPT_ID
        RR=ROLL
        MARK=int(marks[i])
        cursor.execute('''DECLARE BEGIN ADD_MARKS(:CDEPT_ID,:CLEVEL,:CNUM,:Y,:SDEPT_ID,:ROLL,:MARK); END;''',[CDEPT_ID,CLEVEL,CNUM,Y,SDEPT_ID,ROLL,MARK])
        i=i+1
    cursor.execute('''DECLARE BEGIN CGPA_UPDATE(:YY,:DD,:RR); END;''',[YY, DD, RR])
    conn.commit()
    conn.close()
    return render(request, 'success_message.html')

def term_resultsubj(request):
    return redirect('/adminhome')

def adminlogin(request):
    if 'admin' in request.session:
        return redirect('/adminhome')
    return render(request, 'adminlogin.html')

def home(request):
    if 'admin' in request.session:
        return render(request, 'menu.html')
    else:
        usar = request.POST.get("username", "")
        passw = request.POST.get("password", "")
        if(usar=='admin' and passw=='mara'):
            request.session['admin'] = True
            return render(request, 'menu.html')
        else:
            return redirect('/adminlogin')

def menu(request):
    if 'admin' in request.session:
        return
    else:
        return redirect('/adminlogin')

def gotermresult(request):
    if 'admin' in request.session:
        return redirect('/term_result')
    else:
        return redirect('/adminlogin')

def logout(request):
    del request.session['admin']
    return redirect('/adminlogin')

def opreg(request):
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute('''DECLARE BEGIN OPEN_REGISTRATION; END;''')
    conn.commit()
    conn.close()
    return redirect('/adminhome')

def closreg(request):
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute('''DECLARE BEGIN CLOSE_REGISTRATION; END;''')
    conn.commit()
    conn.close()
    return redirect('/adminhome')
def update_result(request):
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute('''DECLARE BEGIN RESULT_OF_ALL; END;''')
    conn.commit()
    conn.close()
    return redirect('/adminhome')

def termcheng(request):
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute('''DECLARE BEGIN BEGIN_NEXT_TERM; END;''')
    conn.commit()
    conn.close()
    return redirect('/adminhome')

def get_marksheet(request):
    course_no = request.POST.get("course_no", "")
    offered_dept_id = request.POST.get("offered_dept_id", "")
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    course_no=int(course_no)
    offered_dept_id=int(offered_dept_id)
    CNUM=course_no%100
    course_no=course_no//100
    CLEVEL_=course_no%10
    course_no=course_no//10
    CDEPT=course_no
    lavl=1
    term=1
    cursor.execute('''SELECT LEVEL_,TERM FROM COURSE WHERE DEPT_ID=:CDEPT AND LEVEL_=:CLEVEL_ AND COURSE_NUMBER=:CNUM''',[CDEPT,CLEVEL_,CNUM])
    row = cursor.fetchall()
    for r in row:
        lavl=r[0]
        term=r[1]
    cursor.execute('''SELECT (R.YEAR*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER) AS STUDENT_ID
FROM REGISTRATION R LEFT OUTER JOIN STUDENT S ON(R.YEAR=S.YEAR AND R.STUDENT_DEPT_ID=S.DEPT_ID AND R.ROLL_NUMBER=S.ROLL_NUMBER)
WHERE R.COURSE_DEPT_ID=:CDEPT AND R.LEVEL_=:CLEVEL AND R.COURSE_NUMBER=:CNUM AND S.DEPT_ID=:offered_dept_id AND S.LEVEL_=:lavl AND S.TERM=:term ORDER BY STUDENT_ID''',[CDEPT,CLEVEL_,CNUM,offered_dept_id,lavl,term])
    row = cursor.fetchall()
    student_info=[]
    for r in row:
        sinfo={'roll':r[0]%10000000,'reg_id':(r[0]*100000+CDEPT*1000+CLEVEL_*100+CNUM)}
        student_info.append(sinfo)
    course={'course_id':'CSE101','course_name':'SPL','full_marks':300}
    cursor.execute('''SELECT D.DEPT_CODE||TO_CHAR(C.LEVEL_*100+C.COURSE_NUMBER) AS ID, C.COURSE_NAME, C.CREDIT*100 AS FM
FROM COURSE C JOIN DEPARTMENT D ON(C.DEPT_ID=D.DEPT_ID)
WHERE C.DEPT_ID=:CDEPT AND C.LEVEL_=:CLEVEL_ AND C.COURSE_NUMBER=:CNUM''',[CDEPT,CLEVEL_,CNUM])
    row = cursor.fetchall()
    for r in row:
        course['course_id']=r[0]
        course['course_name']=r[1]
        course['full_marks']=r[2]
    conn.close()
    return render(request, 'course_marksheet.html',
                  {'course': course, 'student': student_info})
def course_marks_are_set(request):
    marks = request.POST.getlist("marks[]", "")
    courses = request.POST.getlist("courses[]", "")
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    YY = 2017
    DD = 5
    RR = 119
    i = 0;
    while i < len(marks):
        # return redirect('/login')
        reg_id = int(courses[i])
        print(reg_id)
        CNUM = reg_id % 100
        CLEVEL = reg_id % 1000
        CLEVEL = CLEVEL // 100
        CDEPT_ID = reg_id % 100000
        CDEPT_ID = CDEPT_ID // 1000
        ROLL = reg_id % 100000000
        ROLL = ROLL // 100000
        SDEPT_ID = reg_id % 10000000000
        SDEPT_ID = SDEPT_ID // 100000000
        Y = reg_id // 10000000000
        YY = Y
        DD = SDEPT_ID
        RR = ROLL
        MARK = int(marks[i])
        cursor.execute('''DECLARE BEGIN ADD_MARKS(:CDEPT_ID,:CLEVEL,:CNUM,:Y,:SDEPT_ID,:ROLL,:MARK); END;''',
                       [CDEPT_ID, CLEVEL, CNUM, Y, SDEPT_ID, ROLL, MARK])
        i = i + 1
    conn.commit()
    conn.close()
    return render(request, 'success_message.html')
def marksheet_menu(request):
    if 'admin' not in request.session:
        return redirect('/adminlogin')
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    depts=[]
    cursor.execute('''SELECT DEPT_ID,DEPT_CODE FROM DEPARTMENT''')
    row = cursor.fetchall()
    for r in row:
        d={'dept_id':r[0],'dept_code':r[1]}
        depts.append(d)
    conn.close()
    return render(request, 'course_info_select.html',{'depts':depts})
def select_course(request):
    lev_=request.POST.get("level", "")
    term=request.POST.get("term", "")
    offerer=request.POST.get("offerer", "")
    offeree = request.POST.get("offeree", "")
    lev_=int(lev_)
    term=int(term)
    offeree=int(offeree)
    offerer=int(offerer)
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute('''SELECT C.DEPT_ID, C.COURSE_NUMBER,C.LEVEL_,D.DEPT_CODE||TO_CHAR(C.LEVEL_*100+C.COURSE_NUMBER),COURSE_NAME
FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON(C.DEPT_ID=D.DEPT_ID)
WHERE C.DEPT_ID=:offerer AND C.LEVEL_=:lev_ AND C.TERM=:term AND EXISTS
(
SELECT R.OFFERED_DEPT_ID
FROM TEACHING R
WHERE R.DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER AND R.OFFERED_DEPT_ID=:offeree
) ORDER BY D.DEPT_CODE''',[offerer,lev_,term,offeree])
    row = cursor.fetchall()
    courses=[]
    cursor.close()
    for r in row:
        c={'course_id':r[3],'course_no':r[0]*1000+r[2]*100+r[1],'course_name':r[4]}
        courses.append(c)
    return render(request, 'course_select.html',{'courses':courses,'offered_dept_id':offeree})