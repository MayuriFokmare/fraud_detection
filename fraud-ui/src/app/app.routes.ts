import { Routes } from '@angular/router';
import { MerchantDashboard } from './merchant-dashboard/merchant-dashboard';
import { AdminDashboard } from './admin-dashboard/admin-dashboard';
import { Login } from './user/login/login';
import { Register } from './user/register/register';
import { ForgotPassword } from './user/forgot-password/forgot-password';
import { Dashboard } from './dashboard/dashboard';

export const routes: Routes = [
  { path: 'login', component: Login },
  { path: 'register', component: Register },
  { path: 'forgotPassword', component: ForgotPassword },
  { path: 'merchant-dashboard', component: MerchantDashboard },
  { path: 'admin-dashboard', component: AdminDashboard },
  { path: 'dashboard', component: Dashboard },
  { path: '', redirectTo: '/login', pathMatch: 'full' }
];