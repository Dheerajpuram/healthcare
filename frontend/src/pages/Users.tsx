import React from 'react';
import { UserGroupIcon } from '@heroicons/react/24/outline';

const Users: React.FC = () => {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">User Management</h1>
        <p className="mt-1 text-sm text-gray-500">
          Manage users, doctors, and patients
        </p>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <div className="text-center">
          <UserGroupIcon className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">User Management</h3>
          <p className="mt-1 text-sm text-gray-500">
            This feature is available for admin users only. Manage user accounts and permissions.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Users;
