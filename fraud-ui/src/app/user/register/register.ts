import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { Router, RouterModule } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterModule],
  templateUrl: './register.html',
  styleUrls: ['./register.css']
})
export class Register {
  name: string = '';
  email: string = '';
  password: string = '';
  confirmPassword: string = '';
  role: string = 'merchant';  // 👈 backend ignores this, all self-registrations are merchant
  address: string = '';
  pincode: string = '';
  mobile_no: string = '';

  constructor(private authService: AuthService, private router: Router) {}

  onRegister() {
    if (this.password !== this.confirmPassword) {
      alert('Passwords do not match!');
      return;
    }

    const data = {
      name: this.name,
      email: this.email,
      password: this.password,
      address: this.address,
      pincode: this.pincode,
      mobile_no: this.mobile_no,
    };

    this.authService.register(data).subscribe({
      next: () => {
        alert('Registered successfully. Please login.');
        this.router.navigate(['/login']);
      },
      error: (err) => {
        console.error('Register error:', err);
        alert('Registration failed. Email may already exist.');
      }
    });
  }
}