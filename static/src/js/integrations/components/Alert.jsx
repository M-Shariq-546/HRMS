import React, { useEffect } from 'react';
import './Alert.css';

const Alert = ({ type, message, onClose }) => {
  useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 5000);

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="oh-wrapper">
      <div className="oh-alert-container">
        <div className={`oh-alert oh-alert--animated ${type === 'success' ? 'oh-alert--success' : 'oh-alert--error'}`}>
          {message}
          <button 
            className="alert-close-btn" 
            onClick={onClose}
            aria-label="Close alert"
          >
            &times;
          </button>
        </div>
      </div>
    </div>
  );
};

export default Alert; 