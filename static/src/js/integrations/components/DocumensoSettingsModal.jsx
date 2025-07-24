import React, { useState, useEffect } from 'react';
import { buildApiUrl, apiRequest, API_CONFIG } from '../config/api';
import './DocumensoSettingsModal.css';

const DocumensoSettingsModal = ({ onClose, onSuccess }) => {
  const [templates, setTemplates] = useState([]);
  const [savedMappings, setSavedMappings] = useState({});
  const [notificationMessage, setNotificationMessage] = useState('');
  const [processingHours, setProcessingHours] = useState('12');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [apiKey, setApiKey] = useState(''); // NEW: API key state
  console.log('apiKey', apiKey);
  const availableVariables = [
    { id: 'company_id', label: 'Company ID' },
    { id: 'company_email', label: 'Company Email' },
    { id: 'company_name', label: 'Company Name' },
    { id: 'company_phone', label: 'Company Phone' },
    { id: 'company_address', label: 'Company Address' },
    { id: 'employee_name', label: 'Employee Name' },
    { id: 'email', label: 'Employee Email' },
    { id: 'phone', label: 'Employee Phone' },
    { id: 'address', label: 'Employee Address' },
    { id: 'city', label: 'Employee City' },
    { id: 'state', label: 'Employee State' },
    { id: 'zip', label: 'Employee Zip' },
    { id: 'country', label: 'Employee Country' },
    { id: 'date_of_birth', label: 'Employee Date of Birth' },
    { id: 'gender', label: 'Employee Gender' },
    { id: 'marital_status', label: 'Employee Marital Status' },
    { id: 'salary', label: 'Salary' },
    { id: 'department_id', label: 'Department ID' },
    { id: 'job_position', label: 'Job Position' },
    { id: 'work_type', label: 'Work Type' },
    { id: 'employee_type', label: 'Employee Type' },
    { id: 'shift', label: 'Shift' },
  ];

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const response = await apiRequest(buildApiUrl(API_CONFIG.endpoints.documensoTemplates));
      const data = await response.json();
      
      setTemplates(data.templates || []);
      setSavedMappings(data.saved_mappings || {});
      setNotificationMessage(data.notification_message || '');
      setProcessingHours(data.processing_hours || '12');
      setApiKey(data.documenso_api_key || ''); // NEW: prefill API key if available
    } catch (error) {
      console.error('Failed to load templates:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    if (!apiKey.trim()) {
      alert('Documenso API key is required.');
      return;
    }
    if (!notificationMessage.trim()) {
      alert('Notification message is required.');
      return;
    }

    const selectedMappings = [];
    let allFieldsMapped = true;

    templates.forEach((template, index) => {
      template.fields.forEach(field => {
        const select = document.getElementById(`map-${field.id}-${index}`);
        if (!select?.value) {
          allFieldsMapped = false;
        }
        if (select?.value) {
          selectedMappings.push({
            template: template.name,
            fieldId: field.id,
            fieldLabel: field.label,
            variable: select.value
          });
        }
      });
    });

    if (!allFieldsMapped) {
      alert('Please map all fields before saving.');
      return;
    }

    try {
      setSaving(true);
      const response = await apiRequest(
        buildApiUrl(API_CONFIG.endpoints.saveDocumensoMappings),
        {
          method: 'POST',
          body: JSON.stringify({
            documenso_api_key: apiKey, // NEW: include API key
            template_mappings: selectedMappings,
            notification_message: notificationMessage,
            processing_hours: processingHours
          })
        }
      );

      const data = await response.json();
      
      if (data.status === 'success') {
        onSuccess();
      } else {
        alert(data.message || 'An error occurred while saving mappings.');
      }
    } catch (error) {
      console.error('Error saving mappings:', error);
      alert('An error occurred while saving mappings.');
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="modal">
        <div className="modal-content">
          <div className="spinner"></div>
          <p>Loading templates...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="modal">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}>&times;</button>
        <h2 style={{ color: '#000', fontWeight: 'bold' }}>Select Documenso Fields</h2>
        
        {/* Notification Message Section */}
        <div style={{ marginBottom: '20px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
          <p style={{ marginBottom: '8px', color: 'black', fontSize: '16px', fontWeight: 'bold' }}>
            Enter a message that will be sent with document notifications.
          </p>
          <textarea
            value={notificationMessage}
            onChange={(e) => setNotificationMessage(e.target.value)}
            placeholder="Enter your notification message here..."
            style={{
              width: '100%',
              minHeight: '80px',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontFamily: 'inherit',
              resize: 'vertical'
            }}
          />
        </div>
        
        {/* Hours Selection Section */}
        <div style={{ marginBottom: '20px', padding: '16px', background: '#f8f9fa', borderRadius: '8px' }}>
          <p style={{ marginBottom: '8px', color: 'black', fontSize: '16px', fontWeight: 'bold' }}>
            Select the number of hours for document processing:
          </p>
          <select
            value={processingHours}
            onChange={(e) => setProcessingHours(e.target.value)}
            style={{
              width: '100%',
              padding: '12px',
              border: '1px solid #ddd',
              borderRadius: '4px',
              fontFamily: 'inherit'
            }}
          >
            <option value="12">12 hours</option>
            <option value="24">24 hours</option>
            <option value="48">48 hours</option>
            <option value="58">58 hours</option>
          </select>
        </div>

        {/* Templates */}
        {templates.map((template, index) => (
          <div key={template.name} className="template-section">
            <div className="template-header">
              {template.name}
              <span className="collapser-icon">&#9654;</span>
            </div>
            <div className="template-body">
              <table>
                <thead>
                  <tr>
                    <th>Field</th>
                    <th>Map to Variable</th>
                  </tr>
                </thead>
                <tbody>
                  {template.fields.map(field => {
                    const savedValue = savedMappings[template.name]?.[field.id];
                    return (
                      <tr key={field.id}>
                        <td>{field.label}</td>
                        <td>
                          <select id={`map-${field.id}-${index}`} defaultValue={savedValue || ''}>
                            <option value="">-- Select variable --</option>
                            {availableVariables.map(v => (
                              <option key={v.id} value={v.id}>
                                {v.label}
                              </option>
                            ))}
                          </select>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          </div>
        ))}

        {/* Save Button */}
        <div style={{ textAlign: 'right', marginTop: '20px' }}>
          <button
            className="oh-btn oh-btn--secondary oh-btn--shadow"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? 'Saving...' : 'Save'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default DocumensoSettingsModal; 