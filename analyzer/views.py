from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Resume
import PyPDF2


# 🏠 Home Page
def home(request):
    return render(request, 'home.html')


# 📝 Register
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'register.html', {'error': 'All fields are required!'})

        if User.objects.filter(username=username).exists():
            return render(request, 'register.html', {'error': 'Username already exists!'})

        User.objects.create_user(username=username, password=password)
        return redirect('login')

    return render(request, 'register.html')


# 🔐 Login
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user:
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


# 🔓 Logout
def user_logout(request):
    logout(request)
    return redirect('login')


# 📄 Upload Resume + Analysis
@login_required(login_url='/login/')
def upload_resume(request):
    if request.method == 'POST':
        file = request.FILES.get('resume')

        # ❌ No file
        if not file:
            return render(request, 'upload.html', {
                'error': 'Please select a file'
            })

        # ❌ Only PDF allowed
        if file.content_type != 'application/pdf':
            return render(request, 'upload.html', {
                'error': '❌ Only PDF files are allowed!'
            })

        try:
            # ✅ Save file
            resume = Resume.objects.create(file=file)

            text = ""

            # ✅ Read PDF safely
            pdf_reader = PyPDF2.PdfReader(resume.file.path)

            for page in pdf_reader.pages:
                try:
                    extracted = page.extract_text()

                    if extracted:
                        text += extracted

                except:
                    continue

            # ❌ No readable text
            if not text.strip():
                return render(request, 'upload.html', {
                    'error': '⚠️ This PDF has no readable text (scanned/image PDF)'
                })

        except Exception as e:
            return render(request, 'upload.html', {
                'error': f'⚠️ Error reading PDF: {str(e)}'
            })

        # ✅ Skill Detection
        skills = ['python', 'django', 'java', 'javascript', 'react', 'sql', 'html', 'css']
        found_skills = [s for s in skills if s in text.lower()]

        # ✅ Recommended Skills
        recommended_skills = ['machine learning', 'data science', 'aws', 'docker']
        missing_skills = [s for s in recommended_skills if s not in found_skills]

        # ✅ Score
        score = min(len(found_skills) * 10, 100)

        # ✅ Job Roles
        job_roles = []

        if 'python' in found_skills and 'django' in found_skills:
            job_roles.append('Python Django Developer')

        if 'javascript' in found_skills and 'react' in found_skills:
            job_roles.append('Frontend Developer')

        if 'sql' in found_skills:
            job_roles.append('Database Developer')

        if 'java' in found_skills:
            job_roles.append('Java Developer')

        if 'html' in found_skills and 'css' in found_skills:
            job_roles.append('Web Developer')

        if not job_roles:
            job_roles.append('Software Developer (General)')

        return render(request, 'result.html', {
            'text': text,
            'skills': found_skills,
            'missing_skills': missing_skills,
            'score': score,
            'jobs': job_roles
        })

    return render(request, 'upload.html')