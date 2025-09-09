import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useNotification } from '../contexts/NotificationContext';
import { apiService } from '../services/api';
import { User } from '../types';
import { CalendarIcon, ClockIcon, UserIcon } from '@heroicons/react/24/outline';

const BookAppointment: React.FC = () => {
  const { user } = useAuth();
  const { addNotification } = useNotification();
  const navigate = useNavigate();
  const [doctors, setDoctors] = useState<User[]>([]);
  const [availableSlots, setAvailableSlots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    doctor_id: '',
    appointment_date: '',
    appointment_time: '',
    reason: '',
    notes: ''
  });

  useEffect(() => {
    fetchDoctors();
  }, []);

  const fetchDoctors = async () => {
    try {
      const response = await apiService.getDoctors();
      setDoctors(response.doctors || []);
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to load doctors'
      });
    }
  };

  const fetchAvailableSlots = async (doctorId: string, date: string) => {
    if (!doctorId || !date) return;
    
    console.log('Fetching available slots for doctor:', doctorId, 'date:', date); // Debug log
    
    try {
      const response = await apiService.getAvailableSlots(parseInt(doctorId), date);
      console.log('Available slots response:', response); // Debug log
      setAvailableSlots(response.available_slots || []);
    } catch (error: any) {
      console.error('Error fetching available slots:', error); // Debug log
      addNotification({
        type: 'error',
        title: 'Error',
        message: 'Failed to load available slots'
      });
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target;
    
    setFormData(prev => {
      const newData = {
        ...prev,
        [name]: value
      };
      
      // Schedule the fetchAvailableSlots call after state update
      setTimeout(() => {
        if (name === 'doctor_id' || name === 'appointment_date') {
          const currentDoctorId = name === 'doctor_id' ? value : newData.doctor_id;
          const currentDate = name === 'appointment_date' ? value : newData.appointment_date;
          
          console.log('Scheduling fetchAvailableSlots with:', currentDoctorId, currentDate);
          fetchAvailableSlots(currentDoctorId, currentDate);
        }
      }, 0);
      
      return newData;
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      await apiService.createAppointment(formData);
      addNotification({
        type: 'success',
        title: 'Success',
        message: 'Appointment booked successfully!'
      });
      navigate('/appointments');
    } catch (error: any) {
      addNotification({
        type: 'error',
        title: 'Error',
        message: error.response?.data?.error || 'Failed to book appointment'
      });
    } finally {
      setLoading(false);
    }
  };

  const selectedDoctor = doctors.find(d => d.id.toString() === formData.doctor_id);

  return (
    <div className="max-w-2xl mx-auto">
      <div className="space-y-6">
        {/* Header */}
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Book Appointment</h1>
          <p className="mt-1 text-sm text-gray-500">
            Schedule an appointment with a doctor
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="bg-white shadow rounded-lg p-6">
            <div className="space-y-4">
              {/* Doctor Selection */}
              <div>
                <label htmlFor="doctor_id" className="block text-sm font-medium text-gray-700">
                  Select Doctor
                </label>
                <select
                  id="doctor_id"
                  name="doctor_id"
                  required
                  value={formData.doctor_id}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 bg-white rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                >
                  <option value="">Choose a doctor</option>
                  {doctors.map((doctor) => (
                    <option key={doctor.id} value={doctor.id}>
                      Dr. {doctor.first_name} {doctor.last_name} - {doctor.specialty}
                    </option>
                  ))}
                </select>
              </div>

              {/* Doctor Info */}
              {selectedDoctor && (
                <div className="bg-gray-50 p-4 rounded-lg">
                  <div className="flex items-center">
                    <UserIcon className="h-8 w-8 text-gray-400 mr-3" />
                    <div>
                      <h3 className="text-sm font-medium text-gray-900">
                        Dr. {selectedDoctor.first_name} {selectedDoctor.last_name}
                      </h3>
                      <p className="text-sm text-gray-500">
                        {selectedDoctor.specialty} • {selectedDoctor.experience_years} years experience
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {/* Date Selection */}
              <div>
                <label htmlFor="appointment_date" className="block text-sm font-medium text-gray-700">
                  Appointment Date
                </label>
                <input
                  type="date"
                  id="appointment_date"
                  name="appointment_date"
                  required
                  min={new Date().toISOString().split('T')[0]}
                  value={formData.appointment_date}
                  onChange={(e) => {
                    console.log('Date input changed:', e.target.value); // Debug log
                    handleChange(e);
                  }}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                />
              </div>

              {/* Time Selection */}
              {formData.doctor_id && formData.appointment_date && (
                <div>
                  <label htmlFor="appointment_time" className="block text-sm font-medium text-gray-700">
                    Available Time Slots
                  </label>
                  {availableSlots.length === 0 ? (
                    <p className="mt-2 text-sm text-gray-500">No available slots for this date</p>
                  ) : (
                    <div className="mt-2 grid grid-cols-3 gap-2">
                      {availableSlots.map((slot) => (
                        <button
                          key={slot.time}
                          type="button"
                          onClick={() => setFormData(prev => ({ ...prev, appointment_time: slot.time }))}
                          className={`px-3 py-2 text-sm font-medium rounded-md border ${
                            formData.appointment_time === slot.time
                              ? 'bg-primary-100 border-primary-500 text-primary-700'
                              : 'bg-white border-gray-300 text-gray-700 hover:bg-gray-50'
                          }`}
                        >
                          {slot.display_time}
                        </button>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Reason */}
              <div>
                <label htmlFor="reason" className="block text-sm font-medium text-gray-700">
                  Reason for Visit
                </label>
                <textarea
                  id="reason"
                  name="reason"
                  rows={3}
                  value={formData.reason}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  placeholder="Please describe the reason for your visit"
                />
              </div>

              {/* Notes */}
              <div>
                <label htmlFor="notes" className="block text-sm font-medium text-gray-700">
                  Additional Notes (Optional)
                </label>
                <textarea
                  id="notes"
                  name="notes"
                  rows={2}
                  value={formData.notes}
                  onChange={handleChange}
                  className="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
                  placeholder="Any additional information you'd like to share"
                />
              </div>
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex justify-end space-x-3">
            <button
              type="button"
              onClick={() => navigate('/appointments')}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading || !formData.doctor_id || !formData.appointment_date || !formData.appointment_time}
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Booking...' : 'Book Appointment'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default BookAppointment;
