import { TestBed } from '@angular/core/testing';

import { FraudDetection } from './fraud-detection';

describe('FraudDetection', () => {
  let service: FraudDetection;

  beforeEach(() => {
    TestBed.configureTestingModule({});
    service = TestBed.inject(FraudDetection);
  });

  it('should be created', () => {
    expect(service).toBeTruthy();
  });
});
