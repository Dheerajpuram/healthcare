# Healthcare Appointment & Resource Management System (HARMS)

A comprehensive healthcare management system built with React, Flask, and MySQL that streamlines hospital operations, improves patient care, and efficiently manages resources.

## 🚀 Features

### User Roles & Authentication
- **Patients**: Book and manage appointments
- **Doctors**: View and manage their schedules
- **Admins**: Manage hospital resources (beds, medicines, equipment)
- JWT-based authentication with role-based access control

### Appointment Management
- Search and book appointments with doctors
- Filter by doctor, specialty, date, and time
- Real-time slot validation to prevent double-booking
- Appointment status tracking (scheduled, confirmed, completed, cancelled)

### Resource Management
- Track beds, medicines, and equipment inventory
- Low stock alerts and expiry notifications
- Resource transaction history
- Occupancy rate monitoring

### Notifications & Alerts
- Real-time notifications for appointments
- Low stock alerts for medicines
- Expired medicine notifications
- Appointment reminders

## 🛠️ Technology Stack

### Frontend
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **React Router** for navigation
- **Axios** for API calls
- **React Hook Form** for form management

### Backend
- **Python Flask** with RESTful APIs
- **SQLAlchemy** ORM
- **Flask-JWT-Extended** for authentication
- **PyMySQL** for MySQL connectivity

### Database
- **MySQL** with comprehensive schema
- User management with role-based access
- Appointment scheduling system
- Resource inventory tracking
- Billing and transaction records

## 📋 Prerequisites

Before running this application, make sure you have the following installed:

- **Node.js** (v16 or higher)
- **Python** (v3.8 or higher)
- **MySQL** (v8.0 or higher)
- **npm** or **yarn**

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <repository-url>
cd healthcare
```

### 2. Database Setup

1. **Start MySQL service**:
   ```bash
   # On macOS with Homebrew
   brew services start mysql
   
   # On Ubuntu/Debian
   sudo systemctl start mysql
   
   # On Windows
   # Start MySQL service from Services or MySQL Workbench
   ```

2. **Create the database**:
   ```sql
   CREATE DATABASE harms_db;
   ```

3. **Update database configuration** in `backend/config.py` if needed:
   ```python
   SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:111111@localhost:3306/harms_db'
   ```

### 3. Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd backend
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   
   # Activate virtual environment
   # On macOS/Linux:
   source venv/bin/activate
   # On Windows:
   venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize the database**:
   ```bash
   python init_db.py
   ```

5. **Start the Flask server**:
   ```bash
   python app.py
   ```

   The backend will be available at `http://localhost:5000`

### 4. Frontend Setup

1. **Navigate to frontend directory** (in a new terminal):
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start the development server**:
   ```bash
   npm start
   ```

   The frontend will be available at `http://localhost:3000`

## 🔐 Demo Accounts

The system comes with pre-configured demo accounts:

| Role | Email | Password | Description |
|------|-------|----------|-------------|
| Admin | admin@harms.com | admin123 | Full system access |
| Doctor | dr.smith@harms.com | doctor123 | Cardiology specialist |
| Patient | patient1@harms.com | patient123 | Sample patient account |

## 📁 Project Structure

```
healthcare/
├── backend/
│   ├── app/
│   │   ├── models/          # Database models
│   │   ├── routes/          # API routes
│   │   ├── services/        # Business logic
│   │   └── utils/           # Utility functions
│   ├── config.py            # Configuration
│   ├── app.py              # Flask application
│   ├── init_db.py          # Database initialization
│   └── requirements.txt    # Python dependencies
├── frontend/
│   ├── src/
│   │   ├── components/      # React components
│   │   ├── contexts/        # React contexts
│   │   ├── pages/          # Page components
│   │   ├── services/       # API services
│   │   ├── types/          # TypeScript types
│   │   └── utils/          # Utility functions
│   ├── public/             # Static assets
│   └── package.json        # Node.js dependencies
└── README.md
```

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/refresh` - Refresh token
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - User logout

### Appointments
- `GET /api/appointments` - Get appointments (with filters)
- `POST /api/appointments` - Create appointment
- `GET /api/appointments/{id}` - Get specific appointment
- `PUT /api/appointments/{id}` - Update appointment
- `DELETE /api/appointments/{id}` - Cancel appointment
- `GET /api/appointments/doctors` - Get available doctors
- `GET /api/appointments/available-slots` - Get available time slots

### Resources (Admin only)
- `GET /api/resources` - Get resources
- `POST /api/resources` - Create resource
- `GET /api/resources/{id}` - Get specific resource
- `PUT /api/resources/{id}` - Update resource
- `DELETE /api/resources/{id}` - Delete resource
- `POST /api/resources/{id}/transactions` - Create transaction
- `GET /api/resources/{id}/transactions` - Get transactions
- `GET /api/resources/alerts` - Get resource alerts

### Users (Admin only)
- `GET /api/users` - Get users
- `GET /api/users/{id}` - Get specific user
- `PUT /api/users/{id}` - Update user
- `POST /api/users/{id}/deactivate` - Deactivate user
- `POST /api/users/{id}/activate` - Activate user

### Dashboard
- `GET /api/dashboard/stats` - Get dashboard statistics
- `GET /api/dashboard/notifications` - Get notifications

## 🎯 Key Features Explained

### Role-Based Access Control
- **Patients** can book appointments, view their schedule, and manage their profile
- **Doctors** can view their appointments, update appointment status, and manage their schedule
- **Admins** have full access to manage resources, users, and view system-wide statistics

### Appointment System
- Real-time availability checking prevents double-booking
- Flexible time slot management (30-minute intervals)
- Comprehensive appointment status tracking
- Doctor and patient-specific views

### Resource Management
- Inventory tracking for beds, medicines, and equipment
- Automated low stock alerts
- Expiry date monitoring for medicines
- Transaction history for audit trails

### Responsive Design
- Mobile-first approach with Tailwind CSS
- Responsive navigation and layouts
- Touch-friendly interface for mobile devices

## 🔧 Configuration

### Environment Variables

Create a `.env` file in the backend directory:

```env
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-in-production
JWT_SECRET_KEY=your-jwt-secret-key-change-in-production
DATABASE_URL=mysql+pymysql://root:111111@localhost:3306/harms_db
```

### Database Configuration

Update the database connection in `backend/config.py`:

```python
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://username:password@host:port/database_name'
```

## 🚀 Deployment

### Backend Deployment

1. **Production WSGI Server**:
   ```bash
   pip install gunicorn
   gunicorn -w 4 -b 0.0.0.0:5000 app:app
   ```

2. **Environment Variables**:
   Set production environment variables for security

### Frontend Deployment

1. **Build for Production**:
   ```bash
   npm run build
   ```

2. **Serve with Nginx**:
   Configure Nginx to serve the built files

### Database Migration

For production deployment, use proper database migration tools:

```bash
# Install Flask-Migrate
pip install Flask-Migrate

# Initialize migrations
flask db init

# Create migration
flask db migrate -m "Initial migration"

# Apply migration
flask db upgrade
```

## 🧪 Testing

### Backend Testing

```bash
cd backend
python -m pytest tests/
```

### Frontend Testing

```bash
cd frontend
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/your-repo/issues) page
2. Create a new issue with detailed information
3. Contact the development team

## 🔮 Future Enhancements

- [ ] Real-time notifications with WebSocket
- [ ] Email/SMS integration for notifications
- [ ] Advanced reporting and analytics
- [ ] Mobile app development
- [ ] Integration with external healthcare systems
- [ ] AI-powered appointment recommendations
- [ ] Telemedicine features
- [ ] Multi-language support

## 📊 Database Schema

The system includes the following main tables:

- **users** - User accounts with role-based access
- **appointments** - Appointment scheduling and management
- **resources** - Hospital resources (beds, medicines, equipment)
- **resource_transactions** - Resource inventory transactions
- **billing** - Appointment billing and payments

## 🎉 Acknowledgments

- React team for the amazing frontend framework
- Flask team for the lightweight Python web framework
- Tailwind CSS for the utility-first CSS framework
- All contributors and testers

---

**Happy Coding! 🚀**# healthcare
# healthcare
