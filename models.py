from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from enum import Enum

db = SQLAlchemy()

class Role(Enum):
    ADMIN = "admin"
    HR = "hr"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(50), nullable=False, default=Role.EMPLOYEE.value)
    full_name = db.Column(db.String(200), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    
    def has_permission(self, permission):
        """Check if user has specific permission based on role"""
        role_permissions = {
            Role.ADMIN.value: ['create', 'read', 'update', 'delete', 'manage_users'],
            Role.HR.value: ['create', 'read', 'update', 'delete'],
            Role.MANAGER.value: ['read', 'update'],
            Role.EMPLOYEE.value: ['read']
        }
        return permission in role_permissions.get(self.role, [])
    
    def can_manage_users(self):
        return self.role == Role.ADMIN.value
    
    def can_manage_accounts(self):
        """Allow HR and Admin to manage user accounts"""
        return self.role in [Role.ADMIN.value, Role.HR.value]
    
    def can_create_employees(self):
        return self.role in [Role.ADMIN.value, Role.HR.value]
    
    def can_edit_employees(self):
        return self.role in [Role.ADMIN.value, Role.HR.value, Role.MANAGER.value]
    
    def can_delete_employees(self):
        return self.role in [Role.ADMIN.value, Role.HR.value]
    
    def can_view_salaries(self):
        return self.role in [Role.ADMIN.value, Role.HR.value]

class Employee(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    position = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.Integer, nullable=False)
