import React, { useState, useEffect } from 'react';
import { buildApiUrl, apiRequest, API_CONFIG } from '../config/api';
import './WiseSettingsModal.css';

const WiseSettingsModal = ({ onClose, onSuccess }) => {
  const [recipients, setRecipients] = useState([]);
  const [loading, setLoading] = useState(true);
  const [addingRecipient, setAddingRecipient] = useState(false);
  const [message, setMessage] = useState('');
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    iban: '',
    country: '',
    currency: ''
  });

  useEffect(() => {
    fetchRecipients();
  }, []);

  const fetchRecipients = async () => {
    try {
      setLoading(true);
      const response = await apiRequest(buildApiUrl(API_CONFIG.endpoints.wiseRecipients));
      const data = await response.json();
      
      if (data.status === 'success') {
        setRecipients(data.recipients || []);
      } else {
        setMessage('Failed to load recipients.');
      }
    } catch (error) {
      console.error('Failed to load recipients:', error);
      setMessage('Failed to load recipients.');
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const { name, email, iban, country, currency } = formData;
    
    if (!name.trim() || !email.trim() || !iban.trim() || !country.trim() || !currency.trim()) {
      setMessage('All fields are required.');
      return;
    }

    try {
      setAddingRecipient(true);
      setMessage('');

      const response = await apiRequest(
        buildApiUrl(API_CONFIG.endpoints.wiseAddRecipient),
        {
          method: 'POST',
          body: JSON.stringify({ name, email, iban, country, currency })
        }
      );

      const data = await response.json();

      if (data.status === 'success') {
        setMessage('Recipient added successfully.');
        setFormData({
          name: '',
          email: '',
          iban: '',
          country: '',
          currency: ''
        });
        fetchRecipients();
        onSuccess();
      } else if (data.status === 'exists') {
        setMessage('Recipient with this IBAN already exists.');
      } else {
        setMessage(data.message || 'Something went wrong.');
      }
    } catch (error) {
      console.error('Failed to add recipient:', error);
      setMessage('Server error. Please try again later.');
    } finally {
      setAddingRecipient(false);
    }
  };

  return (
    <div className="modal">
      <div className="modal-content">
        <button className="close-btn" onClick={onClose}>&times;</button>
        <h2 style={{ color: '#000', fontWeight: 'bold' }}>Wise Recipients</h2>
        
        <div id="wise-recipients-list" style={{ marginBottom: '24px' }}>
          {loading ? (
            <div className="spinner" style={{ display: 'block' }}></div>
          ) : (
            <ul id="wise-recipients-ul">
              {recipients.length > 0 ? (
                recipients.map((recipient, index) => (
                  <li key={index}>
                    {recipient.name} ({recipient.email})
                  </li>
                ))
              ) : (
                <li>No recipients found.</li>
              )}
            </ul>
          )}
        </div>

        <form id="wise-add-recipient-form" onSubmit={handleSubmit}>
          <div id="wise-recipient-message" style={{ marginTop: '12px' }}>
            {message && (
              <div className={`alert ${message.includes('successfully') ? 'alert-success' : 'alert-error'}`}>
                {message}
                <span className="close-alert" onClick={() => setMessage('')}>&times;</span>
              </div>
            )}
          </div>
          
          <h3>Add New Recipient</h3>
          
          <label htmlFor="wise-name">Name:</label>
          <input
            type="text"
            id="wise-name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
            className="oh-input w-100"
          />
          
          <label htmlFor="wise-email">Email:</label>
          <input
            type="email"
            id="wise-email"
            name="email"
            value={formData.email}
            onChange={handleInputChange}
            required
            className="oh-input w-100"
          />
          
          <label htmlFor="wise-iban">IBAN:</label>
          <input
            type="text"
            id="wise-iban"
            name="iban"
            value={formData.iban}
            onChange={handleInputChange}
            required
            className="oh-input w-100"
          />
          
          <label htmlFor="wise-country">Country Code:</label>
          <input
            type="text"
            id="wise-country"
            name="country"
            value={formData.country}
            onChange={handleInputChange}
            required
            className="oh-input w-100"
          />
          
          <label htmlFor="wise-currency">Currency:</label>
          <input
            type="text"
            id="wise-currency"
            name="currency"
            value={formData.currency}
            onChange={handleInputChange}
            required
            className="oh-input w-100"
          />
          
          <button
            type="submit"
            className="oh-btn oh-btn--secondary oh-btn--shadow"
            style={{ marginTop: '12px' }}
            disabled={addingRecipient}
          >
            {addingRecipient ? 'Adding...' : 'Add Recipient'}
          </button>
        </form>
      </div>
    </div>
  );
};

export default WiseSettingsModal; 