# 🚀  Login-Register-Healthcare API by FastAPI Framework
A secure, scalable, and containerized user management system for healthcare, built using FastAPI, JWT authentication, and MySQL.

# 🔹 Features
✅ OAuth2 Authentication with JWT
✅ Role-based access control (Admin, Doctor, Employee)
✅ Secure password hashing with bcrypt
✅ CRUD operations for user management
✅ MySQL database integration with SQLAlchemy
✅ Dockerized with lightweight containers
✅ Automated health checks for MySQL
✅ Fully automated testing with pytest

# 📌 1. Installation & Setup
🔹 Prerequisites
Docker & Docker Compose
Python 3.8+ (only for local development)

# 🔹 Clone the Repository

git clone https://github.com/GHAZI-ALANZI/login-register-healthcare-fastapi-service.git


# 🔹 Configure Environment Variables
Create a .env file in the project root and add:

DATABASE_URL=mysql+pymysql://user:password@db/healthcare
SECRET_KEY=your_super_secret_key
ACCESS_TOKEN_EXPIRE_MINUTES=30

# 📌 2. Running the Application with Docker
🔹 Step 1: Build & Run Docker Containers
Run the following command:


docker-compose up --build

🚀 Now your API is running inside a Docker container!

FastAPI API: http://127.0.0.1:8000
MySQL Database: localhost:3306

# 🔹 Step 2: Check Running Containers
To verify that the containers are running:


docker ps

# 🔹 Step 3: Stopping & Cleaning Up
To stop the containers:

docker-compose down

**To remove all containers, volumes, and networks:

docker-compose down -v

# 📌 3. Authentication & OAuth2
The API uses OAuth2 Password Flow for authentication.

# 🔹 How to Get an Access Token
Send a POST request to /login with application/x-www-form-urlencoded data:

**🔹 Curl Example

curl -X 'POST' \
  'http://127.0.0.1:8000/login' \
  -H 'Content-Type: application/x-www-form-urlencoded' \
  -d 'grant_type=password&username=admin&password=Admin@123&scope=admin read write'



# 📌 4. API Endpoints

🔹 Authentication

Method	                Endpoint	        Description
POST	                 /login	            Authenticate user and get JWT token
POST	                 /register	        Create a new user (Admin only)


🔹 User Management

Method	            Endpoint	                   Description	          Authorization
GET	               /users	                       Get all users	        admin
GET	               /user/email/{email}	         Get user by email	    admin
GET	               /user/username/{username}	   Get user by username	  admin
PUT	               /user/update/{id}	           Update user details	  admin
DELETE	           /user/delete/{id}	           Delete a user	        admin

# 📌 5. Running Automated Tests

🔹 Install Testing Dependencies

pip install pytest httpx

🔹 Run Tests

pytest test_main.py

***🔹 Expected Output***

============================= test session starts =============================
collected 7 items

test_main.py::test_login_success ✅ PASSED
test_main.py::test_login_invalid_password ✅ PASSED
test_main.py::test_register_user ✅ PASSED
test_main.py::test_get_users ✅ PASSED
test_main.py::test_register_user_not_admin ✅ PASSED
test_main.py::test_delete_user ✅ PASSED
test_main.py::test_delete_user_not_admin ✅ PASSED

========================== 7 passed in 2.3 seconds ============================

# 📌  Security Best Practices
✅ Use environment variables for secret keys and database credentials.
✅ Store hashed passwords (bcrypt).
✅ Use JWT expiration time to prevent long-term token abuse.
✅ Enforce role-based access control (RBAC) using Scopes.
✅ Health check for MySQL ensures API doesn’t start until DB is ready.

# 📌  Contribution Guide
🔹 Want to contribute? Follow these steps:
Fork the repo and create a new branch.
Make your changes and test them.
Create a pull request with a clear description.


🎯 Now your FastAPI Login-Register Healthcare API is fully containerized, documented, and production-ready! 🚀🔥
