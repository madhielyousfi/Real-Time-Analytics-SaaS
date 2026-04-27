'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { LayoutDashboard, Activity, GitGraph, Settings } from 'lucide-react';

interface LayoutProps {
  children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
  return (
    <div className="min-h-screen flex">
      <aside className="w-64 bg-gray-900 text-white">
        <div className="p-6">
          <h1 className="text-xl font-bold">Analytics</h1>
        </div>
        <nav className="mt-6">
          <Link
            href="/"
            className="flex items-center px-6 py-3 hover:bg-gray-800"
          >
            <LayoutDashboard className="w-5 h-5 mr-3" />
            Dashboard
          </Link>
          <Link
            href="/events"
            className="flex items-center px-6 py-3 hover:bg-gray-800"
          >
            <Activity className="w-5 h-5 mr-3" />
            Events
          </Link>
          <Link
            href="/funnels"
            className="flex items-center px-6 py-3 hover:bg-gray-800"
          >
            <GitGraph className="w-5 h-5 mr-3" />
            Funnels
          </Link>
          <Link
            href="/settings"
            className="flex items-center px-6 py-3 hover:bg-gray-800"
          >
            <Settings className="w-5 h-5 mr-3" />
            Settings
          </Link>
        </nav>
      </aside>
      <main className="flex-1 p-8">{children}</main>
    </div>
  );
}