import React from 'react';
import { UserCircleIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Profile: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Profile</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage your account information
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center">
          <UserCircleIcon className="h-16 w-16 text-gray-400 mr-4" />
          <div>
            <h3 className="text-lg font-medium text-gray-900">
              {user?.first_name} {user?.last_name}
            </h3>
            <p className="text-sm text-gray-500 capitalize">{user?.role}</p>
            <p className="text-sm text-gray-500">{user?.email}</p>
          </div>
        </div>
        
        <div className="mt-6">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Profile Information</h4>
          <dl className="grid grid-cols-1 gap-x-4 gap-y-2 sm:grid-cols-2">
            <div>
              <dt className="text-sm font-medium text-gray-500">Phone</dt>
              <dd className="text-sm text-gray-900">{user?.phone || 'Not provided'}</dd>
            </div>
            {user?.role === 'doctor' && (
              <>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Specialty</dt>
                  <dd className="text-sm text-gray-900">{user?.specialty || 'Not specified'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Experience</dt>
                  <dd className="text-sm text-gray-900">{user?.experience_years || 0} years</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">License Number</dt>
                  <dd className="text-sm text-gray-900">{user?.license_number || 'Not provided'}</dd>
                </div>
              </>
            )}
            {user?.role === 'patient' && (
              <>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Date of Birth</dt>
                  <dd className="text-sm text-gray-900">
                    {user?.date_of_birth ? new Date(user.date_of_birth).toLocaleDateString() : 'Not provided'}
                  </dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Gender</dt>
                  <dd className="text-sm text-gray-900 capitalize">{user?.gender || 'Not specified'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Address</dt>
                  <dd className="text-sm text-gray-900">{user?.address || 'Not provided'}</dd>
                </div>
                <div>
                  <dt className="text-sm font-medium text-gray-500">Emergency Contact</dt>
                  <dd className="text-sm text-gray-900">{user?.emergency_contact || 'Not provided'}</dd>
                </div>
              </>
            )}
          </dl>
        </div>
      </div>
    </div>
  );
};

export default Profile;
