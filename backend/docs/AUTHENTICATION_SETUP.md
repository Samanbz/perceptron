# Authentication Setup with Azure Cosmos DB

This guide will help you set up user authentication using Azure Cosmos DB.

## Prerequisites

1. **Azure Account**: You need an active Azure subscription
2. **Cosmos DB Account**: Create a Cosmos DB account in Azure Portal

## Step 1: Create Azure Cosmos DB Account

1. Go to [Azure Portal](https://portal.azure.com)
2. Click "Create a resource"
3. Search for "Azure Cosmos DB"
4. Select "Azure Cosmos DB" and click "Create"
5. Choose **Core (SQL)** API
6. Fill in the details:
   - **Subscription**: Your Azure subscription
   - **Resource Group**: Create new or use existing
   - **Account Name**: Choose a unique name (e.g., `perceptron-db`)
   - **Location**: Choose closest region
   - **Capacity mode**: Choose **Serverless** (for development) or **Provisioned throughput**
7. Click "Review + Create" and then "Create"
8. Wait for deployment to complete (5-10 minutes)

## Step 2: Get Your Cosmos DB Credentials

1. Go to your Cosmos DB account in Azure Portal
2. Click on **Keys** in the left sidebar
3. Copy the following values:
   - **URI** (e.g., `https://your-account.documents.azure.com:443/`)
   - **PRIMARY KEY** (long string)

## Step 3: Configure Backend

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Copy the example environment file:
   ```bash
   copy .env.example .env
   ```

3. Edit `.env` file and update these values:
   ```env
   COSMOS_ENDPOINT=https://your-cosmos-account.documents.azure.com:443/
   COSMOS_KEY=your-cosmos-primary-key-here
   COSMOS_DATABASE_NAME=perceptron
   COSMOS_USERS_CONTAINER=users
   ```

4. The SECRET_KEY is pre-generated, but you can change it for production:
   ```python
   # Generate a new secret key with:
   python -c "import secrets; print(secrets.token_hex(32))"
   ```

## Step 4: Install Dependencies

```bash
pip install -r requirements.txt
```

New packages for authentication:
- `azure-cosmos`: Azure Cosmos DB SDK
- `azure-identity`: Azure authentication
- `python-jose[cryptography]`: JWT token generation
- `passlib[bcrypt]`: Password hashing
- `python-multipart`: Form data parsing
- `python-dotenv`: Environment variable management

## Step 5: Initialize Cosmos DB

Run the setup script to create the database and container:

```bash
python scripts/setup_cosmos_db.py
```

This will:
- Connect to your Cosmos DB account
- Create the `perceptron` database (if it doesn't exist)
- Create the `users` container with email as partition key
- Set up throughput (400 RU/s for development)

## Step 6: Start the Backend Server

```bash
cd backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

## Step 7: Test the Authentication

### API Documentation
Visit `http://localhost:8000/docs` to see the interactive API documentation.

### Available Endpoints

1. **Signup**: `POST /auth/signup`
   ```json
   {
     "email": "user@example.com",
     "name": "John Doe",
     "password": "securepassword123"
   }
   ```

2. **Login (OAuth2 Form)**: `POST /auth/login`
   - Use form data with `username` (email) and `password`

3. **Login (JSON)**: `POST /auth/login/json`
   ```json
   {
     "email": "user@example.com",
     "password": "securepassword123"
   }
   ```

4. **Get Current User**: `GET /auth/me`
   - Requires Authorization header: `Bearer <token>`

5. **Verify Token**: `GET /auth/verify`
   - Requires Authorization header: `Bearer <token>`

## Frontend Integration

The frontend is already configured to use these endpoints. The Login and Signup pages will:

1. **Signup**: POST to `/auth/signup` with email, name, and password
2. **Login**: POST to `/auth/login/json` with email and password
3. **Store Token**: Save JWT token in localStorage
4. **Protected Routes**: Include token in Authorization header for authenticated requests
5. **Redirect**: After successful login, redirect to `/dashboard`

## Security Features

- **Password Hashing**: Using bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **Token Expiration**: Tokens expire after 24 hours (configurable)
- **HTTPS**: Use HTTPS in production
- **CORS**: Configured for frontend origin

## Cosmos DB Cost Management

### Serverless (Recommended for Development)
- Pay only for operations you use
- No minimum charge
- Good for development and light usage

### Provisioned Throughput
- 400 RU/s = ~$23/month (minimum)
- Can scale up/down as needed
- Better for production with predictable load

### Free Tier
- Azure offers 400 RU/s free tier
- Enough for development and testing
- [Apply for free tier](https://docs.microsoft.com/en-us/azure/cosmos-db/free-tier)

## Troubleshooting

### Connection Issues
- Verify COSMOS_ENDPOINT and COSMOS_KEY in .env
- Check firewall settings in Azure Portal (allow access from your IP)
- Ensure Cosmos DB account is active

### Authentication Errors
- Check SECRET_KEY is set in .env
- Verify token is included in Authorization header
- Token format: `Bearer <your-token>`

### Cosmos DB Errors
- Check quota limits in Azure Portal
- Verify partition key is set correctly (email)
- Ensure container exists (run setup script)

## Production Considerations

1. **Use Azure Key Vault** for storing secrets
2. **Enable Private Endpoint** for Cosmos DB
3. **Set up monitoring** with Application Insights
4. **Use managed identity** instead of connection strings
5. **Enable point-in-time restore** for data recovery
6. **Set up geo-replication** for high availability
7. **Use strong SECRET_KEY** (not the default one)
8. **Enable HTTPS** with valid SSL certificate
9. **Implement rate limiting** to prevent abuse
10. **Add input validation** for all user inputs

## Next Steps

1. Implement password reset functionality
2. Add email verification
3. Implement refresh tokens
4. Add social authentication (Google, Microsoft, etc.)
5. Implement role-based access control (RBAC)
6. Add audit logging
7. Implement session management
8. Add two-factor authentication (2FA)
