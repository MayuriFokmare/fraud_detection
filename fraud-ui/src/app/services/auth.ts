import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';
import { environment } from '../../environments/environment';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl;

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/login/`, { email, password }).pipe(
      tap((res: any) => {
        if (res.access && res.refresh) {
          localStorage.setItem('access_token', res.access);
          localStorage.setItem('refresh_token', res.refresh);

          if (res.user) {
            localStorage.setItem('user', JSON.stringify(res.user));
            const uname = res.user.name || res.user.username;
            if (uname) {
              localStorage.setItem('username', uname);
            }
          } else if (res.name) {
            localStorage.setItem('user', JSON.stringify({ name: res.name }));
            localStorage.setItem('username', res.name);
          }
        }
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/auth/register/`, userData);
  }

  logout(): void {
    localStorage.clear();
  }

  getAccessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  getUser(): any {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  getUsername(): string | null {
    return localStorage.getItem('username');
  }
}