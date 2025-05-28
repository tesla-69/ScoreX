import { useState } from 'react';
import { ChartBarIcon, DocumentTextIcon, UserGroupIcon, CalendarIcon } from '@heroicons/react/24/outline';

const stats = [
  { name: 'Total Job Descriptions', stat: '0', icon: DocumentTextIcon },
  { name: 'CVs Processed', stat: '0', icon: UserGroupIcon },
  { name: 'Matches Found', stat: '0', icon: ChartBarIcon },
  { name: 'Pending Interviews', stat: '0', icon: CalendarIcon },
];

export default function Dashboard() {
  return (
    <div>
      <h2 className="text-2xl font-semibold text-gray-900 mb-8">Recruitment Dashboard</h2>
      
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => (
          <div
            key={item.name}
            className="relative overflow-hidden rounded-lg bg-white px-4 py-5 shadow sm:px-6 sm:pt-6"
          >
            <dt>
              <div className="absolute rounded-md bg-indigo-500 p-3">
                <item.icon className="h-6 w-6 text-white" aria-hidden="true" />
              </div>
              <p className="ml-16 truncate text-sm font-medium text-gray-500">{item.name}</p>
            </dt>
            <dd className="ml-16 flex items-baseline pb-6 sm:pb-7">
              <p className="text-2xl font-semibold text-gray-900">{item.stat}</p>
            </dd>
          </div>
        ))}
      </div>

      <div className="mt-8 grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div className="rounded-lg bg-white shadow">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900">Recent Job Descriptions</h3>
            <div className="mt-6">
              <p className="text-center text-gray-500 py-4">No job descriptions added yet</p>
            </div>
          </div>
        </div>

        <div className="rounded-lg bg-white shadow">
          <div className="p-6">
            <h3 className="text-lg font-medium text-gray-900">Recent CV Matches</h3>
            <div className="mt-6">
              <p className="text-center text-gray-500 py-4">No matches found yet</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
} 