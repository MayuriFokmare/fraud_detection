import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, tap } from 'rxjs';

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = 'http://127.0.0.1:8000/api/auth';  // backend base URL

  constructor(private http: HttpClient) {}

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/login/`, { email, password }).pipe(
      tap((res: any) => {
        if (res.access && res.refresh) {
          localStorage.setItem('access_token', res.access);
          localStorage.setItem('refresh_token', res.refresh);

          // ✅ Save full user object or fallback
          if (res.user) {
            localStorage.setItem('user', JSON.stringify(res.user));

            // store username (check both name and username)
            const uname = res.user.name || res.user.username;
            if (uname) {
              localStorage.setItem('username', uname);
            }
          } else if (res.name) {
            // some APIs send name directly
            localStorage.setItem('user', JSON.stringify({ name: res.name }));
            localStorage.setItem('username', res.name);
          }
        }
      })
    );
  }

  register(userData: any): Observable<any> {
    return this.http.post(`${this.apiUrl}/register/`, userData);
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