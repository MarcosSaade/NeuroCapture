// frontend/renderer/src/components/PatientDetail.test.jsx
import React from 'react';
import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event'; // If interactions are needed for form
import PatientDetail from '../PatientDetail';
import * as assessmentApi from '../../api/assessment'; // To mock
import { NotificationProvider } from '../../context/NotificationContext'; // To wrap
import * as patientApi from '../../api/patient'; // To mock patientApi

// Mock the API module
jest.mock('../../api/assessment');
jest.mock('../../api/patient'); 
jest.mock('../../api/recording', () => ({
  uploadRecording: jest.fn().mockResolvedValue({}),
  // Add other recording functions if PatientDetail calls them directly during this flow
}));


// Mock useNotifications if not using NotificationProvider wrapper or if it causes issues
// jest.mock('../context/NotificationContext', () => ({
//   useNotifications: () => ({
//     addToast: jest.fn(),
//   }),
// }));

// Mock AssessmentForm to capture its onSaved prop and to avoid deep rendering issues
let capturedOnSaved;
jest.mock('../AssessmentForm', () => (props) => {
  capturedOnSaved = props.onSaved; // Capture the function
  // console.log("Mock AssessmentForm rendered, onSaved captured:", !!capturedOnSaved);
  return <div data-testid="mock-assessment-form">Mock Assessment Form</div>;
});

// Mock AssessmentList to check props passed to it
let capturedAssessmentsForList;
jest.mock('../AssessmentList', () => (props) => {
  capturedAssessmentsForList = props.assessments;
  // console.log("Mock AssessmentList rendered, assessments captured:", capturedAssessmentsForList);
  return <div data-testid="mock-assessment-list">Mock Assessment List ({props.assessments?.length || 0} items)</div>;
});


describe('PatientDetail Component - Assessment Handling', () => {
  const mockPatientId = 1;
  const mockNewAssessmentPayload = {
    assessment_type: 'MoCA',
    score: 25,
    max_possible_score: 30,
    assessment_date: new Date('2023-01-15T10:00:00.000Z').toISOString(),
    diagnosis: 'Mild Cognitive Impairment',
    notes: 'Test notes for new assessment',
    subscores: [
      { name: 'Visuospatial/Executive', score: 4, max_score: 5 },
      { name: 'Naming', score: 2, max_score: 3 },
    ],
  };
  const savedNewAssessmentWithId = {
    ...mockNewAssessmentPayload,
    assessment_id: 101,
    patient_id: mockPatientId,
    created_at: new Date('2023-01-15T10:00:00.000Z').toISOString(),
    updated_at: new Date('2023-01-15T10:00:00.000Z').toISOString(),
    // Ensure subscores in the response are structured as expected by PatientDetail/AssessmentList
    subscores: mockNewAssessmentPayload.subscores.map(s => ({ ...s, subscore_id: Math.random() * 1000 })),
  };

  beforeEach(() => {
    // Reset mocks before each test
    jest.clearAllMocks();
    
    // Default mock implementations
    patientApi.getPatient.mockResolvedValue({ 
      patient_id: mockPatientId, 
      study_identifier: 'P001', 
      demographics: { name: 'John Doe' } // Add any other required fields by DemographicForm
    });
    patientApi.updatePatient.mockResolvedValue({});
    patientApi.deletePatient.mockResolvedValue({});

    assessmentApi.createAssessment.mockResolvedValue(savedNewAssessmentWithId);
    assessmentApi.updateAssessment.mockResolvedValue(savedNewAssessmentWithId); // Or a different one for updates
    assessmentApi.fetchAssessments.mockResolvedValue([]); // Start with no assessments by default

    // Reset captured variables from mocks
    capturedOnSaved = undefined;
    capturedAssessmentsForList = undefined;
  });

  test('should call createAssessment and reload data when a new assessment is saved via AssessmentForm', async () => {
    // Initial fetch returns no assessments
    assessmentApi.fetchAssessments.mockResolvedValueOnce([]);
    
    // Second fetch (after create) returns the new assessment
    assessmentApi.fetchAssessments.mockResolvedValueOnce([savedNewAssessmentWithId]);

    render(
      <NotificationProvider>
        <PatientDetail patientId={mockPatientId} onSuccess={() => {}} onDeleted={() => {}} />
      </NotificationProvider>
    );

    // Wait for initial data loading to complete (patient and initial assessments)
    await act(async () => {
      await screen.findByText('Info & Demographics'); // Ensure PatientDetail has rendered past loading
    });
    
    expect(patientApi.getPatient).toHaveBeenCalledWith(mockPatientId);
    expect(assessmentApi.fetchAssessments).toHaveBeenCalledWith(mockPatientId);
    // Initially, AssessmentList should receive an empty array or undefined
    expect(screen.getByTestId('mock-assessment-list')).toHaveTextContent('Mock Assessment List (0 items)');


    // Ensure AssessmentForm's onSaved (handleAssessmentSaved in PatientDetail) is captured
    if (!capturedOnSaved) {
        // This might happen if PatientDetail hasn't rendered AssessmentForm yet,
        // or if the active tab isn't 'cognitive'. Let's switch tabs.
        const cognitiveTab = screen.getByRole('button', { name: /Cognitive Assessments/i });
        await act(async () => {
            userEvent.click(cognitiveTab);
        });
        // Wait for AssessmentForm to be rendered and onSaved captured
        await screen.findByTestId('mock-assessment-form'); 
    }
    
    if (!capturedOnSaved) {
        throw new Error("onSaved prop was not captured from AssessmentForm. Check mock and component logic.");
    }
    
    // Simulate AssessmentForm submitting new data by calling the captured onSaved function
    await act(async () => {
      // console.log("Calling capturedOnSaved with payload:", mockNewAssessmentPayload);
      capturedOnSaved(mockNewAssessmentPayload, null); // null for assessmentId means new assessment
    });

    // Check that createAssessment was called
    expect(assessmentApi.createAssessment).toHaveBeenCalledTimes(1);
    expect(assessmentApi.createAssessment).toHaveBeenCalledWith(mockPatientId, mockNewAssessmentPayload);

    // Check that assessments were re-fetched after saving
    // fetchAssessments was called once initially, and once after createAssessment
    expect(assessmentApi.fetchAssessments).toHaveBeenCalledTimes(2);
    expect(assessmentApi.fetchAssessments).toHaveBeenNthCalledWith(2, mockPatientId);
    
    // Verify AssessmentList receives the new data
    // Need to wait for the re-render after data fetching and state update
    await act(async () => {
      await new Promise(resolve => setTimeout(resolve, 0)); // allow state updates and re-renders
    });

    // Check the text content of the mock list or the captured prop
    expect(screen.getByTestId('mock-assessment-list')).toHaveTextContent('Mock Assessment List (1 items)');
    expect(capturedAssessmentsForList).toEqual([savedNewAssessmentWithId]);
    
    // If AssessmentList was not mocked, you could do:
    // expect(await screen.findByText(savedNewAssessmentWithId.assessment_type)).toBeInTheDocument();
    // expect(await screen.findByText(`Score: ${savedNewAssessmentWithId.score}`)).toBeInTheDocument();
    // savedNewAssessmentWithId.subscores.forEach(async subscore => {
    //   expect(await screen.findByText(subscore.name)).toBeInTheDocument();
    // });
  });
});
```
