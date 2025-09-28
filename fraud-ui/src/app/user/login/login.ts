import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './login.html',
  styleUrls: ['./login.css']
})
export class Login {
  role: string = 'merchant';   // default role selected
  email: string = '';
  password: string = '';

  constructor(
    private router: Router,
    private authService: AuthService
  ) {}

  onLogin() {
    if (!this.email || !this.password) {
      alert('Please enter email and password');
      return;
    }

    console.log('Attempting login with:', {
      email: this.email,
      role: this.role
    });

    this.authService.login(this.email, this.password).subscribe({
      next: (res) => {
        console.log(' Login success:', res);

        //  Save username and role from backend if provided
        if (res.username) {
          localStorage.setItem('username', res.username);
        }

        if (res.role) {
          // If backend sends role → trust backend
          localStorage.setItem('role', res.role);
          this.role = res.role;  // overwrite frontend toggle
        } else {
          // fallback → use frontend toggle
          localStorage.setItem('role', this.role);
        }

        //  Redirect based on role
        if (this.role === 'merchant') {
          console.log(' Redirecting to /dashboard');
          this.router.navigate(['/dashboard']);
        } else if (this.role === 'admin') {
          console.log(' Redirecting to /admin-dashboard');
          this.router.navigate(['/admin-dashboard']);
        } else {
          console.log(' Redirecting to default /dashboard');
          this.router.navigate(['/dashboard']);
        }
      },
      error: (err) => {
        console.error(' Login error:', err);
        alert('Invalid email or password');
      }
    });
  }
}
