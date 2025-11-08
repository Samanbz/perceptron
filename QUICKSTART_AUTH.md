# 🚀 Quick Start Guide - Authentication Setup

## ⚡ What You Need From Azure

To make the authentication work, you need **2 strings** from Azure Cosmos DB:

### 1. COSMOS_ENDPOINT
Format: `https://your-account-name.documents.azure.com:443/`

### 2. COSMOS_KEY  
Format: Long alphanumeric string (primary key)

## 📍 Where to Get These Values

### Step 1: Create Cosmos DB Account (if you don't have one)
1. Go to https://portal.azure.com
2. Click "Create a resource"
3. Search "Azure Cosmos DB"
4. Select "Azure Cosmos DB" → "Create"
5. Choose **Core (SQL)** API
6. Fill in:
   - **Account Name**: Choose unique name (e.g., `perceptron-db-123`)
   - **Location**: Choose closest region
   - **Capacity mode**: Select **Serverless** (free tier available)
7. Click "Review + Create" → "Create"
8. Wait 5-10 minutes for deployment

### Step 2: Get Your Credentials
1. Once deployed, go to your Cosmos DB account
2. In the left menu, click **"Keys"**
3. You'll see:
   - **URI** → This is your `COSMOS_ENDPOINT`
   - **PRIMARY KEY** → This is your `COSMOS_KEY`
4. Copy both values

## 🔧 Configure Your Application

### Backend Configuration

Edit `backend/.env` file:

```env
# Replace these with your actual values
COSMOS_ENDPOINT=https://your-actual-account-name.documents.azure.com:443/
COSMOS_KEY=your-actual-primary-key-paste-here

# These are pre-configured (you can keep them)
COSMOS_DATABASE_NAME=perceptron
COSMOS_USERS_CONTAINER=users
SECRET_KEY=09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
ENVIRONMENT=development
```

**That's it!** Only these 2 strings are needed from you.

## 🏃 Run The Application

### 1. Install Backend Dependencies
```powershell
cd backend
pip install -r requirements.txt
```

### 2. Initialize Cosmos DB
```powershell
python scripts/setup_cosmos_db.py
```

You should see:
```
✅ Connected to Cosmos DB: perceptron
✅ Cosmos DB setup completed successfully!
```

### 3. Start Backend Server
```powershell
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

### 4. Start Frontend (in new terminal)
```powershell
cd frontend
npm run dev
```

## ✅ Test It Works

1. Open http://localhost:5173
2. Click "Sign Up"
3. Create a test account:
   - Name: Test User
   - Email: test@example.com
   - Password: testpassword123
4. Should redirect to dashboard automatically
5. Try logging out and back in

## 🎯 What I've Already Done

### Backend (Complete ✅)
- ✅ Azure Cosmos DB integration
- ✅ JWT authentication system
- ✅ Password hashing with bcrypt
- ✅ User registration endpoint
- ✅ Login endpoint (OAuth2 + JSON)
- ✅ Token verification
- ✅ User profile endpoint
- ✅ Database initialization script
- ✅ Environment configuration
- ✅ CORS setup for frontend

### Frontend (Complete ✅)
- ✅ API service with token management
- ✅ Authentication context (global state)
- ✅ Protected route component
- ✅ Login page with backend integration
- ✅ Signup page with validation
- ✅ Dashboard with user data
- ✅ Logout functionality
- ✅ Error handling and display
- ✅ Loading states
- ✅ Session persistence
- ✅ Auto-redirect after auth

## 🔐 What Happens Behind The Scenes

### When You Sign Up:
1. Frontend sends: name, email, password
2. Backend hashes password with bcrypt
3. Stores user in Cosmos DB
4. Auto-logs you in
5. Returns JWT token
6. Redirects to dashboard

### When You Login:
1. Frontend sends: email, password
2. Backend verifies password
3. Generates JWT token (valid 24 hours)
4. Frontend stores token in localStorage
5. Fetches your user data
6. Redirects to dashboard

### When You Access Dashboard:
1. Checks for token in localStorage
2. Sends token to backend for verification
3. If valid: shows dashboard
4. If invalid: redirects to login

## 💰 Cost Estimate

### Azure Cosmos DB
- **Free Tier**: 1000 RU/s + 25GB storage (free forever)
- **Beyond Free**: ~$0.25 per million operations
- **For this app**: Should stay in free tier for development

### Serverless Option
- Pay only for what you use
- No minimum cost
- Perfect for development and testing

## ❓ Troubleshooting

### Can't connect to Cosmos DB
- Double-check COSMOS_ENDPOINT and COSMOS_KEY in `.env`
- Make sure there are no extra spaces
- Ensure Cosmos DB account is active in Azure Portal

### Backend won't start
- Run: `pip install -r requirements.txt` again
- Check Python version (3.8+ required)
- Make sure `.env` file exists

### Frontend errors
- Make sure backend is running on port 8000
- Check browser console for specific errors
- Clear browser localStorage and try again

### "Email already registered"
- That email is already in the database
- Use a different email or login with existing account
- Or delete user from Cosmos DB in Azure Portal

## 📚 Documentation

- Full Backend Setup: `backend/docs/AUTHENTICATION_SETUP.md`
- Full Frontend Integration: `frontend/AUTHENTICATION_INTEGRATION.md`
- Backend API Summary: `backend/docs/AUTH_SUMMARY.md`
- API Documentation: http://localhost:8000/docs (when running)

## 🎉 You're All Set!

Once you provide those 2 strings and follow the steps above, you'll have:
- ✅ Fully functional user registration
- ✅ Secure login system
- ✅ Protected dashboard
- ✅ User session management
- ✅ Professional authentication flow

**Just give me your Cosmos DB endpoint and key, and you're ready to go!** 🚀
