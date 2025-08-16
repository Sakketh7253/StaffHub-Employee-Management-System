from flask import Flask, render_template, request, redirect, url_for, flash, abort
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Employee, Role
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import random
from datetime import datetime
import time
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your_secret_key_for_development')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///employees.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize db with app
db.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Role-based decorators
def role_required(roles):
    """Decorator to require specific roles"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if current_user.role not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def permission_required(permission):
    """Decorator to require specific permission"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('login'))
            if not current_user.has_permission(permission):
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# Create tables and users
with app.app_context():
    # Drop all tables and recreate them to ensure schema consistency
    db.drop_all()
    db.create_all()
    
    # Create users with different roles
    users_data = [
        {
            'username': 'CEO',
            'password': 'ceo123',
            'role': Role.ADMIN.value,
            'full_name': 'CEO Admin',
            'email': 'ceo@staffhub.com'
        },
        {
            'username': 'HR',
            'password': 'hr123',
            'role': Role.HR.value,
            'full_name': 'HR Manager',
            'email': 'hr@staffhub.com'
        },
        {
            'username': 'Manager',
            'password': 'manager123',
            'role': Role.MANAGER.value,
            'full_name': 'Department Manager',
            'email': 'manager@staffhub.com'
        },
        {
            'username': 'Employee',
            'password': 'emp123',
            'role': Role.EMPLOYEE.value,
            'full_name': 'Employee User',
            'email': 'employee@staffhub.com'
        }
    ]
    
    for user_data in users_data:
        user = User(
            username=user_data['username'],
            password=generate_password_hash(user_data['password']),
            role=user_data['role'],
            full_name=user_data['full_name'],
            email=user_data['email']
        )
        db.session.add(user)
    
    db.session.commit()
    print("Users created:")
    print("Admin: CEO / ceo@staffhub.com")
    print("HR: HR / hr@staffhub.com")
    print("Manager: Manager / manager@staffhub.com")
    print("Employee: Employee / employee@staffhub.com")

    # Generate 100+ sample employees for enterprise-scale testing
    def generate_large_employee_dataset():
        departments = ['Engineering', 'Human Resources', 'Marketing', 'Finance', 'Sales', 'Operations', 'IT Support', 'Legal', 'Research & Development', 'Customer Service']
        positions = {
            'Engineering': ['Software Engineer', 'Senior Software Engineer', 'Lead Developer', 'DevOps Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer', 'System Architect'],
            'Human Resources': ['HR Manager', 'HR Specialist', 'Recruiter', 'Training Coordinator', 'Compensation Analyst'],
            'Marketing': ['Marketing Manager', 'Digital Marketing Specialist', 'Content Creator', 'SEO Specialist', 'Brand Manager'],
            'Finance': ['Financial Analyst', 'Accountant', 'Finance Manager', 'Budget Analyst', 'Tax Specialist'],
            'Sales': ['Sales Manager', 'Sales Representative', 'Account Executive', 'Business Development Manager'],
            'Operations': ['Operations Manager', 'Project Manager', 'Quality Analyst', 'Process Improvement Specialist'],
            'IT Support': ['IT Support Specialist', 'System Administrator', 'Network Engineer', 'Help Desk Technician'],
            'Legal': ['Legal Counsel', 'Paralegal', 'Contract Specialist', 'Compliance Officer'],
            'Research & Development': ['Research Scientist', 'Product Manager', 'Innovation Specialist', 'R&D Engineer'],
            'Customer Service': ['Customer Service Rep', 'Support Manager', 'Client Success Manager', 'Call Center Agent']
        }
        
        first_names = ['John', 'Sarah', 'Michael', 'Emily', 'Robert', 'Lisa', 'David', 'Jennifer', 'Christopher', 'Ashley', 
                      'Matthew', 'Amanda', 'Daniel', 'Jessica', 'Anthony', 'Melissa', 'Mark', 'Michelle', 'Steven', 'Kimberly',
                      'Paul', 'Amy', 'Andrew', 'Angela', 'Joshua', 'Helen', 'Kenneth', 'Deborah', 'Kevin', 'Rachel',
                      'Brian', 'Carolyn', 'George', 'Janet', 'Edward', 'Catherine', 'Ronald', 'Maria', 'Timothy', 'Heather',
                      'Jason', 'Diane', 'Jeffrey', 'Ruth', 'Ryan', 'Julie', 'Jacob', 'Joyce', 'Gary', 'Virginia']
        
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez',
                     'Hernandez', 'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson', 'Martin',
                     'Lee', 'Perez', 'Thompson', 'White', 'Harris', 'Sanchez', 'Clark', 'Ramirez', 'Lewis', 'Robinson',
                     'Walker', 'Young', 'Allen', 'King', 'Wright', 'Scott', 'Torres', 'Nguyen', 'Hill', 'Flores']
        
        employees = []
        used_emails = set()  # Track used emails to prevent duplicates
        
        for i in range(120):  # Generate 120 employees for 100+ requirement
            dept = random.choice(departments)
            first_name = random.choice(first_names)
            last_name = random.choice(last_names)
            position = random.choice(positions[dept])
            
            # Generate unique email with counter if needed
            base_email = f"{first_name.lower()}.{last_name.lower()}"
            email = f"{base_email}@staffhub.com"
            counter = 1
            while email in used_emails:
                email = f"{base_email}{counter}@staffhub.com"
                counter += 1
            used_emails.add(email)
            
            # Generate realistic salary ranges based on position and department
            base_salary = {
                'Engineering': random.randint(70000, 130000),
                'Human Resources': random.randint(50000, 85000),
                'Marketing': random.randint(45000, 90000),
                'Finance': random.randint(55000, 95000),
                'Sales': random.randint(40000, 120000),
                'Operations': random.randint(50000, 85000),
                'IT Support': random.randint(45000, 75000),
                'Legal': random.randint(80000, 150000),
                'Research & Development': random.randint(65000, 110000),
                'Customer Service': random.randint(35000, 60000)
            }
            
            employees.append({
                'name': f"{first_name} {last_name}",
                'email': email,
                'department': dept,
                'position': position,
                'salary': base_salary[dept]
            })
        
        return employees
    
    print("Generating 100+ employee records for enterprise-scale testing...")
    start_time = time.time()
    
    sample_employees = generate_large_employee_dataset()
    
    for emp_data in sample_employees:
        employee = Employee(
            name=emp_data['name'],
            email=emp_data['email'],
            department=emp_data['department'],
            position=emp_data['position'],
            salary=emp_data['salary']
        )
        db.session.add(employee)
    
    db.session.commit()
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"✅ Successfully created {len(sample_employees)} employee records!")
    print(f"⚡ Database processing time: {processing_time:.2f} seconds")
    print("🚀 Enterprise-scale dataset ready for testing!")

# -------- Authentication Routes --------
@app.route('/login', methods=['GET', 'POST'])
def login():
    print("Login route accessed")  # Debug print
    if request.method == 'POST':
        print("POST request received")  # Debug print
        username = request.form['username']
        password = request.form['password']
        print(f"Login attempt: {username}")  # Debug print
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Login successful!')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Invalid username or password!')
    
    print("Rendering login template")  # Debug print
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))

# -------- Routes --------
@app.route('/test')
def test():
    return "<h1>Test page works!</h1>"

@app.route('/debug')
def debug():
    try:
        employees = Employee.query.all()
        html = f"""
        <h1>Debug Page - No Login Required</h1>
        <p>Server is working!</p>
        <p>Employees found in database: {len(employees)}</p>
        <h3>Employee List:</h3>
        <ul>
        """
        for emp in employees:
            html += f"<li>{emp.name} - {emp.department} - {emp.position} - ${emp.salary}</li>"
        html += """
        </ul>
        <p><a href='/login'>Go to Login Page</a></p>
        """
        return html
    except Exception as e:
        return f"<h1>Debug Error:</h1><p>{str(e)}</p>"

@app.route('/simple_login')
def simple_login():
    return render_template('simple_login.html')

@app.route('/')
@login_required
def index():
    print("Index route accessed")  # Debug print
    start_time = time.time()
    
    # Get search parameters
    search = request.args.get('search', '')
    department_filter = request.args.get('department', '')
    page = request.args.get('page', 1, type=int)
    per_page = 10  # Show 10 employees per page for better performance
    
    # Build query with optimizations
    query = Employee.query
    
    # Apply search filters
    if search:
        query = query.filter(
            (Employee.name.contains(search)) |
            (Employee.email.contains(search)) |
            (Employee.position.contains(search))
        )
    
    if department_filter:
        query = query.filter(Employee.department == department_filter)
    
    # Order by name for consistent pagination
    query = query.order_by(Employee.name)
    
    # Apply pagination
    employees_paginated = query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get unique departments for filter dropdown
    departments = db.session.query(Employee.department.distinct()).all()
    departments = [dept[0] for dept in departments]
    
    # Get total count for performance metrics
    total_employees = Employee.query.count()
    
    end_time = time.time()
    query_time = end_time - start_time
    
    print(f"Found {total_employees} total employees")  # Debug print
    print(f"Showing page {page} with {len(employees_paginated.items)} employees")  # Debug print
    print(f"Query execution time: {query_time:.3f} seconds")  # Performance metric
    print("Current user:", current_user.username, "Role:", current_user.role)  # Debug print
    
    return render_template('index.html', 
                         employees=employees_paginated,
                         search=search,
                         department_filter=department_filter,
                         departments=departments,
                         total_employees=total_employees,
                         query_time=query_time)

@app.route('/add', methods=['GET', 'POST'])
@login_required
@permission_required('create')
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        department = request.form['department']
        position = request.form['position']
        salary = request.form['salary']
        new_employee = Employee(name=name, email=email, department=department, position=position, salary=salary)
        db.session.add(new_employee)
        db.session.commit()
        flash("Employee added successfully!")
        return redirect(url_for('index'))
    return render_template('add_employee.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
@permission_required('update')
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.department = request.form['department']
        employee.position = request.form['position']
        employee.salary = request.form['salary']
        db.session.commit()
        flash("Employee updated successfully!")
        return redirect(url_for('index'))
    return render_template('edit_employee.html', employee=employee)

@app.route('/delete/<int:id>')
@login_required
@permission_required('delete')
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash("Employee deleted successfully!")
    return redirect(url_for('index'))

# -------- User Account Management Routes --------
@app.route('/users')
@login_required
def manage_users():
    """Show all user accounts - HR and Admin only"""
    if not current_user.can_manage_accounts():
        abort(403)
    
    users = User.query.all()
    return render_template('manage_users.html', users=users)

@app.route('/users/edit/<int:user_id>', methods=['GET', 'POST'])
@login_required
def edit_user_account(user_id):
    """Edit user account details - HR and Admin only"""
    if not current_user.can_manage_accounts():
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # HR users cannot edit Admin accounts - only Admin can edit Admin
    if user.role == Role.ADMIN.value and not current_user.can_manage_users():
        flash("Only Admins can edit Administrator accounts!", "error")
        return redirect(url_for('manage_users'))
    
    if request.method == 'POST':
        new_username = request.form['username']
        new_password = request.form.get('password', '').strip()
        new_full_name = request.form['full_name']
        new_email = request.form['email']
        new_role = request.form['role']
        
        # Check if username is already taken (excluding current user)
        existing_user = User.query.filter(User.username == new_username, User.id != user_id).first()
        if existing_user:
            flash("Username already exists! Please choose a different username.", "error")
            return render_template('edit_user.html', user=user)
        
        # HR users cannot change someone to Admin role
        if new_role == Role.ADMIN.value and not current_user.can_manage_users():
            flash("Only Admins can assign Administrator role!", "error")
            return render_template('edit_user.html', user=user)
        
        # Update user details
        user.username = new_username
        user.full_name = new_full_name
        user.email = new_email
        
        # Only Admin can change roles
        if current_user.can_manage_users():
            user.role = new_role
        
        # Update password if provided
        if new_password:
            user.password = generate_password_hash(new_password)
            flash(f"Account updated successfully! New password set for {user.username}.", "success")
        else:
            flash(f"Account updated successfully for {user.username}!", "success")
        
        db.session.commit()
        return redirect(url_for('manage_users'))
    
    return render_template('edit_user.html', user=user)

@app.route('/users/add', methods=['GET', 'POST'])
@login_required
def add_user_account():
    """Add new user account - HR and Admin only"""
    if not current_user.can_manage_accounts():
        abort(403)
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        full_name = request.form['full_name']
        email = request.form['email']
        role = request.form['role']
        
        # Check if username already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash("Username already exists! Please choose a different username.", "error")
            return render_template('add_user.html')
        
        # HR users cannot create Admin accounts
        if role == Role.ADMIN.value and not current_user.can_manage_users():
            flash("Only Admins can create Administrator accounts!", "error")
            return render_template('add_user.html')
        
        # Create new user
        new_user = User(
            username=username,
            password=generate_password_hash(password),
            full_name=full_name,
            email=email,
            role=role
        )
        
        db.session.add(new_user)
        db.session.commit()
        flash(f"New user account created successfully for {username}!", "success")
        return redirect(url_for('manage_users'))
    
    return render_template('add_user.html')

@app.route('/users/delete/<int:user_id>')
@login_required
def delete_user_account(user_id):
    """Delete user account - Admin can delete anyone, HR can delete non-admin users"""
    if not current_user.can_manage_accounts():
        abort(403)
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current user
    if user.id == current_user.id:
        flash("You cannot delete your own account!", "error")
        return redirect(url_for('manage_users'))
    
    # HR users cannot delete Admin accounts - only Admin can delete Admin
    if user.role == Role.ADMIN.value and not current_user.can_manage_users():
        flash("Only Admins can delete Administrator accounts!", "error")
        return redirect(url_for('manage_users'))
    
    username = user.username
    user_role = user.role.title()
    db.session.delete(user)
    db.session.commit()
    flash(f"{user_role} account '{username}' deleted successfully!", "success")
    return redirect(url_for('manage_users'))

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    flash("You don't have permission to access this resource!", "error")
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found(error):
    flash("The requested page was not found!", "error")
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    flash("An internal error occurred. Please try again!", "error")
    return redirect(url_for('index'))

# Run server
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
