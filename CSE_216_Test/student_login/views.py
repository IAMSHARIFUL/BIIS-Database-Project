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

def logout(request):
    request.session.clear()
    return redirect('/login')


def home(request):
    if 'usar' in request.session:
        student = {'name': "irri", 'year': 2017, 'dept': "Comp.", 'lev': 1, 'ter': 1, 'usar': '253245', 'credit': 0,
                   'cgpa': 0}
        student['name'] = request.session['name']
        student['year'] = request.session['year']
        student['dept'] = request.session['dept']
        student['lev'] = request.session['lev']
        student['usar'] = request.session['usar']
        student['ter'] = request.session['ter']
        student['credit'] = request.session['credit']
        student['cgpa'] = request.session['cgpa']
        return render(request, 'home.html', {'student': student})

    usar = request.POST.get("username", "")
    passw = request.POST.get("password", "")
    if authenticate(usar, passw):
        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
        conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)

        cursor = conn.cursor()
        student = {'name': "irri", 'year': 2017, 'dept': "Comp.", 'lev': 1, 'ter': 1, 'usar': usar, 'credit': 0,
                   'cgpa': 0}
        cursor.execute('''SELECT S.STUDENT_NAME,S.YEAR,D.DEPT_NAME,S.LEVEL_,S.TERM,NVL(S.TOTAL_CREDIT,0),NVL(S.CGPA,0)
        FROM STUDENT S LEFT OUTER JOIN DEPARTMENT D ON(S.DEPT_ID=D.DEPT_ID)
        WHERE LPAD(TO_CHAR(MOD(S.YEAR,100)*100000+S.DEPT_ID*1000+S.ROLL_NUMBER),7,'0')=:usar''', [usar])
        row = cursor.fetchall()
        conn.close()
        for r in row:
            student['name'] = r[0]
            student['year'] = r[1]
            student['dept'] = r[2]
            student['lev'] = r[3]
            student['ter'] = r[4]
            student['credit'] = r[5]
            student['cgpa'] = r[6]

            request.session['usar'] = usar
            request.session['name'] = student['name']
            request.session['year'] = student['year']
            request.session['lev'] = student['lev']
            request.session['ter'] = student['ter']
            request.session['credit'] = student['credit']
            request.session['cgpa'] = student['cgpa']
            request.session['dept'] = student['dept']
        return render(request, 'home.html', {'student': student})
    else:
        return redirect('/login')

def login(request):
    if 'usar' in request.session:
        return redirect('/home')
    return render(request, 'login.html')
def homepage(request):
    return redirect('/home')
def course_registration(request):
    return redirect('/go_for_register')
def course_drop(request):
    return redirect('/go_for_drop')
def my_courses(request):
    return redirect('/go_for_ongoing_courses')
def my_advisor(request):
    return redirect('/go_for_advisor')
def my_result(request):
    return redirect('/go_for_result')

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def authenticate(username, password):
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM STUDENT WHERE LPAD(TO_CHAR(MOD(YEAR,100)*100000+DEPT_ID*1000+ROLL_NUMBER),7,'0')=:username", [username])
    row = dictfetchall(cursor)
    conn.close()
    password=hashlib.sha256(str.encode(password)).hexdigest()
    for user in row:
        if(user['PASSWORD']==password):
            return True
    return False
#
#
# # class LoginForm(object):
# #     pass

def go_for_result(request):
    if ('usar' in request.session)==False:
        return redirect('/login')
    else:
        return render(request,"result.html")
def result(request):

    lavl = request.POST.get("level","")
    tarm = request.POST.get("term","")
    usar = request.session['usar']
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    x=0
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT COUNT(*)  FROM REGISTRATION R JOIN DEPARTMENT D ON (D.DEPT_ID=R.COURSE_DEPT_ID)  JOIN COURSE C ON (R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER) WHERE LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar AND TO_CHAR(R.LEVEL_)=:lavl AND TO_CHAR(C.TERM)=:tarm AND R.GRADE_POINT IS NULL OR (R.GRADE_POINT>0 AND R.GRADE_POINT<1.50)''',
        [usar, lavl, tarm])
    row = cursor.fetchall()
    for r in row:
        x=r[0]
    if x>0:
        return render(request, 'blank.html')
    cursor.execute('''SELECT (D.DEPT_CODE||TO_CHAR(R.LEVEL_)||LPAD(TO_CHAR(R.COURSE_NUMBER),2,'0')) , C.COURSE_NAME , C.CREDIT, R.GRADE_POINT, GRADE(R.GRADE_POINT)  FROM REGISTRATION R JOIN DEPARTMENT D ON (D.DEPT_ID=R.COURSE_DEPT_ID)  JOIN COURSE C ON (R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER) WHERE LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar AND TO_CHAR(R.LEVEL_)=:lavl AND TO_CHAR(C.TERM)=:tarm AND R.GRADE_POINT IS NOT NULL''',[usar,lavl,tarm])
        # row = dictfetchall(cursor)
    row = cursor.fetchall()
    term_credit=0
    term_cgpa=0
    dict = []
    res = []
    blank=True
    for r in row:
        blank=False
        course_id= r[0]
        course_name=r[1]
        credit=r[2]
        grade_point=r[3]
        grade=r[4]
        term_cgpa=term_cgpa+grade_point*credit
        if grade_point>0:
            term_credit=term_credit+credit
        d = {'course_id': course_id, 'course_name' : course_name, 'credit':credit,'grade_point':round(grade_point,2),'grade':grade}
        dict.append(d)
    if blank:
        return render(request, 'blank.html')
    cursor.execute('''SELECT NVL(S.TOTAL_CREDIT,0),NVL(S.CGPA,0) FROM STUDENT S WHERE LPAD(TO_CHAR(MOD(S.YEAR,100)*100000+S.DEPT_ID*1000+S.ROLL_NUMBER),7,'0')=:usar''', [usar])
    row = cursor.fetchall()
    for r in row:
        request.session['credit']=r[0]
        request.session['cgpa']=r[1]
    student={'name':"irri",'year':2017,'dept':"Comp.",'lev':lavl,'ter':tarm,'usar':usar,'credit':0,'cgpa':0}
    student['name']=request.session['name']
    student['year']=request.session['year']
    student['dept']=request.session['dept']
    student['lev']=request.session['lev']
    student['ter']=request.session['ter']
    student['credit']=request.session['credit']
    student['cgpa']=request.session['cgpa']
    student['usar']=request.session['usar']
    if term_credit>0:
        term_cgpa=term_cgpa/term_credit
    term_cgpa=round(term_cgpa,2)
    r={'term_cgpa':term_cgpa,'term_credit':term_credit}
    res.append(r)
    student['cgpa'] = round(student['cgpa'],2)
    return render(request, 'view_result.html', {'jobs': dict,'res':res,'lavl':lavl,'tarm':tarm,'student':student})


def registration(request):
    courses=request.POST.getlist("courses[]","")
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    b = False
    for c in courses:
        b=True
        reg_id=int(c)
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

        cursor.execute('''DECLARE BEGIN ADD_COURSE(:CDEPT_ID,:CLEVEL,:CNUM,:Y,:SDEPT_ID,:ROLL); END;''',[CDEPT_ID,CLEVEL,CNUM,Y,SDEPT_ID,ROLL])
    conn.commit()
    dict = []
    for c in courses:
        b = True
        reg_id = int(c)
        CNUM = reg_id % 100
        CLEVEL = reg_id % 1000
        CLEVEL = CLEVEL // 100
        CDEPT_ID = reg_id % 100000
        CDEPT_ID = CDEPT_ID // 1000
        cursor.execute(
            '''SELECT D.DEPT_CODE,C.DEPT_ID,C.LEVEL_,C.COURSE_NUMBER,C.COURSE_NAME,C.TYPE_,C.CREDIT FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON (C.DEPT_ID=D.DEPT_ID) WHERE C.LEVEL_=:CLEVEL AND C.DEPT_ID=:CDEPT_ID AND C.COURSE_NUMBER=:CNUM''',
            [CLEVEL, CDEPT_ID, CNUM])
        row = cursor.fetchall()
        for r in row:
            blank = False
            dept_code = r[0]
            dept_id = r[1]
            level_ = r[2]
            course_number = r[3]
            course_name = r[4]
            tp = r[5]
            ctype = "Theoretical"
            if tp == 2:
                ctype = "Sessional"
            credit = r[6]
            d = {'course_id': (dept_code + str(level_ * 100 + course_number)), 'course_name': course_name,
                 'course_type': ctype, 'credit': credit}
            dict.append(d)
    conn.close()
    if b:
        return render(request, 'confirmed_registration.html', {'course_list': dict})
    return render(request, 'successful_registration.html')


def drop(request):
    courses=request.POST.getlist("courses[]","")
    dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
    conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
    cursor = conn.cursor()
    b = False
    for c in courses:
        b = True
        reg_id=int(c)
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
        cursor.execute('''DECLARE BEGIN DROP_COURSE(:CDEPT_ID,:CLEVEL,:CNUM,:Y,:SDEPT_ID,:ROLL); END;''',[CDEPT_ID,CLEVEL,CNUM,Y,SDEPT_ID,ROLL])
    conn.commit()
    dict=[]
    for c in courses:
        b = True
        reg_id=int(c)
        CNUM=reg_id%100
        CLEVEL=reg_id%1000
        CLEVEL=CLEVEL//100
        CDEPT_ID=reg_id%100000
        CDEPT_ID=CDEPT_ID//1000
        cursor.execute('''SELECT D.DEPT_CODE,C.DEPT_ID,C.LEVEL_,C.COURSE_NUMBER,C.COURSE_NAME,C.TYPE_,C.CREDIT FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON (C.DEPT_ID=D.DEPT_ID) WHERE C.LEVEL_=:CLEVEL AND C.DEPT_ID=:CDEPT_ID AND C.COURSE_NUMBER=:CNUM''', [CLEVEL, CDEPT_ID, CNUM])
        row = cursor.fetchall()
        for r in row:
            blank=False
            dept_code=r[0]
            dept_id=r[1]
            level_=r[2]
            course_number=r[3]
            course_name=r[4]
            tp=r[5]
            ctype="Theoretical"
            if tp==2:
                ctype="Sessional"
            credit=r[6]
            d={'course_id':(dept_code+str(level_*100+course_number)),'course_name':course_name,'course_type':ctype,'credit':credit}
            dict.append(d)
    conn.close()
    if b:
        return render(request, 'confirmed_drop.html',{'course_list':dict})
    return render(request, 'successful_drop.html')
def go_for_register(request):
    if 'usar' in request.session:
        usar=request.session['usar']

        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
        conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
        reg_id=int(usar)
        student_dept_id=reg_id//1000
        student_dept_id=student_dept_id%100
        reg_id = reg_id + 200000000
        reg_id=reg_id*100000
        cursor = conn.cursor()
        lavl=request.session['lev']
        term=request.session['ter']
        cursor.execute('''SELECT D.DEPT_CODE,C.DEPT_ID,C.LEVEL_,C.COURSE_NUMBER,C.COURSE_NAME,C.TYPE_,C.CREDIT FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON (C.DEPT_ID=D.DEPT_ID) WHERE C.LEVEL_=:lavl AND C.TERM=:term AND NOT EXISTS(SELECT * FROM REGISTRATION R WHERE R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER AND LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar)
AND EXISTS(
SELECT OFFERED_DEPT_ID FROM TEACHING T WHERE T.OFFERED_DEPT_ID=:student_dept_id AND T.DEPT_ID=C.DEPT_ID AND T.LEVEL_=C.LEVEL_ AND T.COURSE_NUMBER=C.COURSE_NUMBER
)
AND NOT EXISTS(
SELECT * FROM PRE_REQUISITE PR
WHERE PR.DEPT_ID=C.DEPT_ID AND PR.LEVEL_=C.LEVEL_ AND PR.COURSE_NUMBER=C.COURSE_NUMBER AND NOT EXISTS(
SELECT * FROM REGISTRATION R2
WHERE R2.COURSE_DEPT_ID=PR.PRE_REQ_DEPT_ID AND R2.LEVEL_=PR.PRE_REQ_LEVEL_ AND R2.COURSE_NUMBER=PR.PRE_REQ_COURSE_NUMBER 
AND LPAD(TO_CHAR(MOD(R2.YEAR,100)*100000+R2.STUDENT_DEPT_ID*1000+R2.ROLL_NUMBER),7,'0')=:usar
AND R2.GRADE_POINT>=2
)
)''',[lavl,term,usar,student_dept_id,usar])
        row=cursor.fetchall()
        dict = []
        blank=True
        for r in row:
            blank=False
            dept_code=r[0]
            dept_id=r[1]
            level_=r[2]
            course_number=r[3]
            course_name=r[4]
            tp=r[5]
            ctype="Theoretical"
            if tp==2:
                ctype="Sessional"
            credit=r[6]
            d={'reg_code':str(reg_id+dept_id*1000+level_*100+course_number),'course_id':(dept_code+str(level_*100+course_number)),'course_name':course_name,'course_type':ctype,'credit':credit}
            dict.append(d)
        cursor.execute('''SELECT D.DEPT_CODE,C.DEPT_ID,C.LEVEL_,C.COURSE_NUMBER,C.COURSE_NAME,C.TYPE_,C.CREDIT FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON (C.DEPT_ID=D.DEPT_ID) WHERE C.LEVEL_=:lavl AND C.TERM=:term AND NOT EXISTS(SELECT * FROM REGISTRATION R WHERE R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER AND LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar)
        AND EXISTS(
        SELECT OFFERED_DEPT_ID FROM TEACHING T WHERE T.OFFERED_DEPT_ID=:student_dept_id AND T.DEPT_ID=C.DEPT_ID AND T.LEVEL_=C.LEVEL_ AND T.COURSE_NUMBER=C.COURSE_NUMBER
        )
        AND EXISTS(
        SELECT * FROM PRE_REQUISITE PR
        WHERE PR.DEPT_ID=C.DEPT_ID AND PR.LEVEL_=C.LEVEL_ AND PR.COURSE_NUMBER=C.COURSE_NUMBER AND NOT EXISTS(
        SELECT * FROM REGISTRATION R2
        WHERE R2.COURSE_DEPT_ID=PR.PRE_REQ_DEPT_ID AND R2.LEVEL_=PR.PRE_REQ_LEVEL_ AND R2.COURSE_NUMBER=PR.PRE_REQ_COURSE_NUMBER 
        AND LPAD(TO_CHAR(MOD(R2.YEAR,100)*100000+R2.STUDENT_DEPT_ID*1000+R2.ROLL_NUMBER),7,'0')=:usar
        AND R2.GRADE_POINT>=2
        )
        )''', [lavl, term, usar, student_dept_id, usar])
        row = cursor.fetchall()
        udict = []
        for r in row:
            blank = False
            dept_code = r[0]
            dept_id = r[1]
            level_ = r[2]
            course_number = r[3]
            course_name = r[4]
            tp = r[5]
            ctype = "Theoretical"
            if tp == 2:
                ctype = "Sessional"
            credit = r[6]
            d = {'reg_code': str(reg_id + dept_id * 1000 + level_ * 100 + course_number),
                 'course_id': (dept_code + str(level_ * 100 + course_number)), 'course_name': course_name,
                 'course_type': ctype, 'credit': credit}
            udict.append(d)
        if blank:
            return render(request, 'blank.html')
        yr=request.session['year']
        cursor.execute('''SELECT COUNT(*) FROM REGISTRATION R LEFT OUTER JOIN STUDENT S ON(R.YEAR=S.YEAR AND R.STUDENT_DEPT_ID=S.DEPT_ID AND R.ROLL_NUMBER=S.ROLL_NUMBER) WHERE R.LEVEL_=:lavl AND S.TERM=:term AND R.YEAR=:yr AND R.STUDENT_DEPT_ID=:student_dept_id AND GRADE_POINT IS NOT NULL''',[lavl,term,yr,student_dept_id])
        row=cursor.fetchall()
        x=0
        for r in row:
            x=r[0]
        if x>0:
            return render(request, 'blank.html')
        return render(request, 'register_course.html', {'course_list': dict,'ucourse_list': udict,'lavl':lavl,'tarm':term})
    else:
        return redirect('/login')
def go_for_drop(request):
    if 'usar' in request.session:
        usar=request.session['usar']
        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
        conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
        reg_id=int(usar)
        student_dept_id = reg_id // 1000
        student_dept_id = student_dept_id % 100
        reg_id=reg_id+200000000
        reg_id=reg_id*100000
        cursor = conn.cursor()
        lavl=request.session['lev']
        term=request.session['ter']
        cursor.execute('''SELECT D.DEPT_CODE,C.DEPT_ID,C.LEVEL_,C.COURSE_NUMBER,C.COURSE_NAME,C.TYPE_,C.CREDIT FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON (C.DEPT_ID=D.DEPT_ID) WHERE C.LEVEL_=:lavl AND C.TERM=:term AND EXISTS(SELECT * FROM REGISTRATION R WHERE R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER AND LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar AND R.GRADE_POINT IS NULL)''',[lavl,term,usar])
        row=cursor.fetchall()
        dict = []
        blank=True
        for r in row:
            blank=False
            dept_code=r[0]
            dept_id=r[1]
            level_=r[2]
            course_number=r[3]
            course_name=r[4]
            tp=r[5]
            ctype="Theoretical"
            if tp==2:
                ctype="Sessional"
            credit=r[6]
            d={'reg_code':str(reg_id+dept_id*1000+level_*100+course_number),'course_id':(dept_code+str(level_*100+course_number)),'course_name':course_name,'course_type':ctype,'credit':credit}
            dict.append(d)
        if blank:
            return render(request, 'blank.html')
        yr = request.session['year']
        cursor.execute('''SELECT COUNT(*) FROM REGISTRATION R LEFT OUTER JOIN STUDENT S ON(R.YEAR=S.YEAR AND R.STUDENT_DEPT_ID=S.DEPT_ID AND R.ROLL_NUMBER=S.ROLL_NUMBER) WHERE R.LEVEL_=:lavl AND S.TERM=:term AND R.YEAR=:yr AND R.STUDENT_DEPT_ID=:student_dept_id AND GRADE_POINT IS NOT NULL''',[lavl, term, yr, student_dept_id])
        row = cursor.fetchall()
        x = 0
        for r in row:
            x = r[0]
        if x > 0:
            return render(request, 'blank.html')
        return render(request, 'drop_course.html', {'course_list': dict,'lavl':lavl,'tarm':term})
    else:
        return redirect('/login')
def go_for_ongoing_courses(request):
    if 'usar' in request.session:
        usar = request.session['usar']
        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
        conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
        reg_id=int(usar)
        reg_id=reg_id+200000000
        reg_id=reg_id*100000
        cursor = conn.cursor()
        lavl=request.session['lev']
        term=request.session['ter']
        cursor.execute('''SELECT D.DEPT_CODE,C.DEPT_ID,C.LEVEL_,C.COURSE_NUMBER,C.COURSE_NAME,C.TYPE_,C.CREDIT FROM COURSE C LEFT OUTER JOIN DEPARTMENT D ON (C.DEPT_ID=D.DEPT_ID) WHERE C.LEVEL_=:lavl AND C.TERM=:term AND EXISTS(SELECT * FROM REGISTRATION R WHERE R.COURSE_DEPT_ID=C.DEPT_ID AND R.LEVEL_=C.LEVEL_ AND R.COURSE_NUMBER=C.COURSE_NUMBER AND LPAD(TO_CHAR(MOD(R.YEAR,100)*100000+R.STUDENT_DEPT_ID*1000+R.ROLL_NUMBER),7,'0')=:usar)''',[lavl,term,usar])
        row=cursor.fetchall()
        dict = []
        total_credit=0
        blank=True
        for r in row:
            blank=False
            dept_code=r[0]
            dept_id=r[1]
            level_=r[2]
            course_number=r[3]
            course_name=r[4]
            tp=r[5]
            ctype="Theoretical"
            if tp==2:
                ctype="Sessional"
            credit=r[6]
            total_credit=total_credit+credit
            d={'reg_code':str(reg_id+dept_id*1000+level_*100+course_number),'course_id':(dept_code+str(level_*100+course_number)),'course_name':course_name,'course_type':ctype,'credit':credit}
            dict.append(d)
        if blank:
            return render(request, 'blank.html')
        return render(request, 'view_ongoing_courses.html', {'course_list': dict,'lavl':lavl,'tarm':term,'total_credit':total_credit})
    else:
        return redirect('/login')
def go_for_advisor(request):
    if 'usar' in request.session:
        dsn_tns = cx_Oracle.makedsn('localhost', '1521', service_name='ORCL')
        conn = cx_Oracle.connect(user='biis', password='mara', dsn=dsn_tns)
        usar=request.session['usar']
        cursor = conn.cursor()
        cursor.execute('''SELECT T.TEACHER_NAME,D.DEPT_NAME,NVL(T.EMAIL_ADDRESS,'Not available'),NVL(T.MOBILE_NO,'Not available'),FIND_DESIGNATION(T.DESIGNATION) FROM TEACHER T LEFT OUTER JOIN DEPARTMENT D ON(T.DEPT_ID=D.DEPT_ID)
WHERE EXISTS(
SELECT S.ADVISOR_ID
FROM STUDENT S
WHERE LPAD(TO_CHAR(MOD(YEAR,100)*100000+DEPT_ID*1000+ROLL_NUMBER),7,'0')=:usar AND S.ADVISOR_ID=T.TEACHER_ID
)''',[usar])
        # row = dictfetchall(cursor)
        row = cursor.fetchall()
        advisor={'name':"Me",'dept':"CSE",'email':"E",'mobile_no':"M",'designation':"Lecturer"}
        blank=True
        for r in row:
            blank=False
            advisor['name']=r[0]
            advisor['dept']=r[1]
            advisor['email']=r[2]
            advisor['mobile_no']=r[3]
            advisor['designation']=r[4]
        conn.close()

        # request.session['userr'] = user
        if blank:
            return render(request, 'blank.html')
        return render(request, 'view_advisor_info.html', {'advisor': advisor})
    else:
        return redirect('/login')