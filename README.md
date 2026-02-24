
## 🔧 Backend Setup

### Step 1: Navigate to Backend Directory

```bash
cd fastAPI-backend
````

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**

```bash
venv\Scripts\activate
```

**macOS/Linux**

```bash
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

### Step 4: Configure Environment Variables

Create a `.env` file in the root directory:

```
MONGO_URL=mongodb://localhost:27017/
JWT_SECRET_KEY=my-super-secret-key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7
ADMIN_SECRET_CODE=ADMIN2024SECRET
```

---

### Step 5: Run the Server

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Server will start at:

```
http://localhost:8000
```

Interactive API Documentation:

```
http://localhost:8000/docs
```

---

## 🔐 Authentication Flow

### 🛡 Admin Registration (One-Time Setup)

Admin registration requires a secret admin code.

Endpoint:

```
POST /api/v1/admins/signup
```

Request Body:

```json
{
  "email": "mainadmin.itve@gmail.com",
  "password": "wadvus-wiqzij-6Pepmo",
  "phone": "+921234567890",
  "username": "mainadmin.itve1",
  "admin_code": "ADMIN2024SECRET"
}
```

> ⚠️ Admin secret code must match the value in `.env` file.

---

### 🔑 Login

Endpoint:

```
POST /api/v1/auth/login
```

Request Body:

```json
{
  "username_or_email": "mainadmin.itve",
  "password": "wadvus-wiqzij-6Pepmo"
}
```

Returns:

* Access Token
* Refresh Token


