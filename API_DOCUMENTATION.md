# VELORA Authentication API Documentation

## Base URL
```
http://localhost:8000/
```

## Available APIs

### 1. Registration Flow (3-Step Process)

#### Step 1: Initiate Registration
**Endpoint:** `POST /api/register/`
**Permission:** Public (no authentication required)

**Request Body:**
```json
{
    "email": "user@example.com"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Verification code sent to your email",
    "session_id": "abc123...",
    "email": "user@example.com",
    "expires_at": "2025-12-03T10:30:00Z"
}
```

#### Step 2: Verify OTP
**Endpoint:** `POST /api/register/verify/`
**Permission:** Public

**Request Body:**
```json
{
    "email": "user@example.com",
    "otp_code": "123456"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "OTP verified successfully",
    "session_id": "abc123..."
}
```

#### Step 3: Complete Registration
**Endpoint:** `POST /api/register/complete/`
**Permission:** Public

**Request Body:**
```json
{
    "session_id": "abc123...",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "password": "SecurePassword123!",
    "confirm_password": "SecurePassword123!",
    "phone_number": "+1234567890",
    "date_of_birth": "1990-01-01",
    "gender": "M",
    "height": 175.5,
    "weight": 70.0,
    "fitness_level": "intermediate",
    "timezone": "UTC",
    "primary_goal": "lose_weight",
    "activity_level": "moderately_active"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Registration completed successfully",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "membership_tier": "basic",
        "is_email_verified": true
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

### 2. Authentication

#### Login with OTP
**Endpoint:** `POST /api/login/`
**Permission:** Public

**Request Body:**
```json
{
    "email": "user@example.com",
    "otp_code": "123456"
}
```

**Response (Success):**
```json
{
    "success": true,
    "message": "Login successful",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "johndoe",
        "membership_tier": "premium"
    },
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
}
```

#### Logout
**Endpoint:** `POST /api/logout/`
**Permission:** Authenticated users only
**Headers:** `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

**Response:**
```json
{
    "success": true,
    "message": "Logged out successfully"
}
```

#### Demo Login (Development Only)
**Endpoint:** `POST /api/demo/login/`
**Permission:** Public

**Request Body:**
```json
{
    "email": "demo@wellness.app"
}
```

### 3. OTP Management

#### Resend OTP
**Endpoint:** `POST /api/resend-otp/`
**Permission:** Public

**Request Body:**
```json
{
    "email": "user@example.com",
    "purpose": "registration"
}
```

**Purposes:** `registration`, `login`, `password_reset`, `email_verification`

### 4. User Profile Management

#### Get User Profile
**Endpoint:** `GET /api/profile/`
**Permission:** Authenticated users only
**Headers:** `Authorization: Token 9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b`

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "full_name": "John Doe",
    "phone_number": "+1234567890",
    "membership_tier": "premium",
    "profile": {
        "primary_goal": "lose_weight",
        "target_weight": 65.0,
        "activity_level": "moderately_active"
    }
}
```

#### Update Profile
**Endpoint:** `PUT /api/profile/update/`
**Permission:** Authenticated users only

**Request Body (partial update allowed):**
```json
{
    "first_name": "John",
    "last_name": "Smith",
    "phone_number": "+1987654321",
    "bio": "Fitness enthusiast"
}
```

#### Complete Onboarding
**Endpoint:** `POST /api/onboarding/complete/`
**Permission:** Authenticated users only

**Response:**
```json
{
    "success": true,
    "message": "Onboarding completed successfully"
}
```

## Frontend Integration Guide

### 1. Registration Flow Implementation

```javascript
// Step 1: Initiate Registration
const initiateRegistration = async (email) => {
    const response = await fetch('/api/register/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email })
    });
    return await response.json();
};

// Step 2: Verify OTP
const verifyOTP = async (email, otpCode) => {
    const response = await fetch('/api/register/verify/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            otp_code: otpCode
        })
    });
    return await response.json();
};

// Step 3: Complete Registration
const completeRegistration = async (userData) => {
    const response = await fetch('/api/register/complete/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(userData)
    });
    return await response.json();
};
```

### 2. Authentication Flow

```javascript
// Login (Step 1: Send OTP)
const requestLoginOTP = async (email) => {
    const response = await fetch('/api/resend-otp/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            purpose: 'login'
        })
    });
    return await response.json();
};

// Login (Step 2: Verify OTP)
const loginWithOTP = async (email, otpCode) => {
    const response = await fetch('/api/login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            email: email,
            otp_code: otpCode
        })
    });
    const result = await response.json();
    
    if (result.success) {
        // Store token for future requests
        localStorage.setItem('authToken', result.token);
    }
    
    return result;
};
```

### 3. Making Authenticated Requests

```javascript
// Get user profile
const getUserProfile = async () => {
    const token = localStorage.getItem('authToken');
    const response = await fetch('/api/profile/', {
        method: 'GET',
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
        }
    });
    return await response.json();
};

// Update profile
const updateProfile = async (profileData) => {
    const token = localStorage.getItem('authToken');
    const response = await fetch('/api/profile/update/', {
        method: 'PUT',
        headers: {
            'Authorization': `Token ${token}`,
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData)
    });
    return await response.json();
};
```

### 4. Error Handling

```javascript
const handleAPIResponse = async (response) => {
    const data = await response.json();
    
    if (!response.ok) {
        // Handle different error types
        if (response.status === 400) {
            console.error('Validation errors:', data.errors || data.message);
        } else if (response.status === 401) {
            // Token expired or invalid
            localStorage.removeItem('authToken');
            window.location.href = '/login';
        } else if (response.status === 429) {
            console.error('Rate limited');
        }
    }
    
    return data;
};
```

## Status Codes

- **200**: Success
- **201**: Created
- **400**: Bad Request (validation errors)
- **401**: Unauthorized
- **403**: Forbidden
- **404**: Not Found
- **429**: Too Many Requests
- **500**: Internal Server Error

## Notes

1. All endpoints return JSON responses
2. Authentication uses Token-based authentication
3. OTP codes expire in 10 minutes by default
4. Registration sessions expire in 24 hours
5. Email notifications are sent for all OTP requests
6. The system supports demo mode with `demo@wellness.app`