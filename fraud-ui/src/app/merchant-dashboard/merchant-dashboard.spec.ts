import { ComponentFixture, TestBed } from '@angular/core/testing';

import { MerchantDashboard } from './merchant-dashboard';

describe('MerchantDashboard', () => {
  let component: MerchantDashboard;
  let fixture: ComponentFixture<MerchantDashboard>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [MerchantDashboard]
    })
    .compileComponents();

    fixture = TestBed.createComponent(MerchantDashboard);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
