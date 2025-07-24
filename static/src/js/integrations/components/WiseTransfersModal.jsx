import React, { useState, useEffect } from 'react';
import { buildApiUrl, apiRequest, API_CONFIG } from '../config/api';
import './WiseTransfersModal.css';

const WiseTransfersModal = ({ onClose }) => {
  const [transfers, setTransfers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchTransfers();
  }, []);

  const fetchTransfers = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await apiRequest(buildApiUrl(API_CONFIG.endpoints.wiseTransfers));
      const data = await response.json();
      
      if (data.status === 'success') {
        setTransfers(data.transfers || []);
      } else {
        setError(data.message || 'Failed to load transfers.');
      }
    } catch (error) {
      console.error('Failed to load transfers:', error);
      setError('Failed to load transfers.');
    } finally {
      setLoading(false);
    }
  };

  const formatDate = (dateString) => {
    if (!dateString) return '';
    try {
      return new Date(dateString).toLocaleString();
    } catch {
      return dateString;
    }
  };

  const getStatusColor = (status) => {
    switch (status?.toLowerCase()) {
      case 'completed':
        return 'status-completed';
      case 'pending':
        return 'status-pending';
      case 'failed':
        return 'status-failed';
      default:
        return 'status-unknown';
    }
  };

  return (
    <div className="modal">
      <div className="modal-content wise-transfers-modal-content">
        <button className="close-btn" onClick={onClose}>&times;</button>
        <hr style={{ margin: '32px 0 16px 0' }} />
        <h2 style={{ color: '#000', fontWeight: 'bold', marginBottom: '12px' }}>
          Recent Transfers
        </h2>
        
        <div id="wise-transfers-list">
          {loading ? (
            <div className="spinner" style={{ display: 'block' }}></div>
          ) : error ? (
            <div style={{ color: 'red', textAlign: 'center' }}>{error}</div>
          ) : transfers.length > 0 ? (
            <div className="wise-transfers-table-wrapper">
              <table id="wise-transfers-table">
                <thead>
                  <tr>
                    <th>Status</th>
                    <th>Transfer ID</th>
                    <th>Recipient</th>
                    <th>Date/Time</th>
                    <th>Amount</th>
                    <th>Payroll Ref</th>
                  </tr>
                </thead>
                <tbody>
                  {transfers.map((transfer, index) => (
                    <tr key={index}>
                      <td>
                        <span className={`status-badge ${getStatusColor(transfer.status)}`}>
                          {transfer.status || ''}
                        </span>
                      </td>
                      <td>{transfer.id || ''}</td>
                      <td>{transfer.recipient || ''}</td>
                      <td>{formatDate(transfer.created)}</td>
                      <td>
                        {transfer.amount ? `${transfer.amount} ${transfer.currency || ''}` : ''}
                      </td>
                      <td>
                        {transfer.payroll_reference ? (
                          <a 
                            href={`${buildApiUrl('/payroll/view-payslip/')}${transfer.payroll_reference}/`} 
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            {transfer.payroll_reference}
                          </a>
                        ) : ''}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div id="wise-transfers-empty" style={{ color: '#888', textAlign: 'center' }}>
              No transfers found.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default WiseTransfersModal; 