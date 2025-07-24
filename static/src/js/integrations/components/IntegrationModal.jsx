import React, { useEffect, useRef, useState } from 'react';
import { buildApiUrl, formDataRequest, API_CONFIG } from '../config/api';
import './IntegrationModal.css';

const IntegrationModal = ({ content, onClose, onSuccess }) => {
  const modalRef = useRef(null);
  const contentRef = useRef(null);
  const [hasSubmitted, setHasSubmitted] = useState(false); // NEW: local state

  const getCSRFToken = () => {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  };

  // This useEffect runs after hasSubmitted is set to true
  useEffect(() => {
    if (hasSubmitted) {
      // This runs after hasSubmitted is true and the component re-renders
      console.log('hasSubmitted is now true!');
    }
  }, [hasSubmitted]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (modalRef.current && !modalRef.current.contains(event.target)) {
        onClose();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  useEffect(() => {
    if (contentRef.current) {
      console.log('contentRef', contentRef.current);
      // Bind form submission events
      const form = contentRef.current.querySelector('form');
      if (form) {
        console.log('form', form);
        const handleSubmit = async (e) => {
          e.preventDefault();
          const form = e.target;
          const action = form.getAttribute('action') || window.location.pathname;
          console.log('action', action);
          
          // Check if this is the Slack configuration form
          if (form.id === 'slack-config-form') {
            const formData = new FormData(form);
            try {
              const response = await fetch('/integrations/slack-connect-api/', {
                method: 'POST',
                headers: {
                  'X-CSRFToken': getCSRFToken(),
                  'Accept': 'application/json',
                },
                body: formData,
              });
              
              const data = await response.json();
              if (data.success && data.oauth_url) {
                setHasSubmitted(true);
                onClose();
                console.log('Redirecting to Slack OAuth:', data.oauth_url);
                window.location.href = data.oauth_url;
                return;
              } else {
                alert(data.error || 'Failed to save Slack configuration');
                return;
              }
            } catch (error) {
              console.error('Slack configuration error:', error);
              alert('Failed to save Slack configuration');
              return;
            }
          }
          
          // Detect Slack integration by action URL
          if (action.includes('slack')) {
            setHasSubmitted(true); // Prevent re-render
            onClose(); // <-- Close the modal in React state
            console.log('close action ===');
            // For Slack OAuth, redirect the browser directly
            console.log('Redirecting to Slack OAuth:', action);
            window.location.href = action;
            return;
          }

          // For other integrations, use AJAX/fetch as before
          const formData = new FormData(form);
          for (let [key, value] of formData.entries()) {
            console.log(`${key}: ${value}`);
          }
          try {
            const response = await formDataRequest(
              buildApiUrl(action),
              formData,
              {
                method: 'POST'
                // Do NOT set Content-Type here!
              }
            );

            if (response.redirected) {
              window.location.href = response.url;
              return;
            }

            if (response.ok) {
              onSuccess();
            } else {
              throw new Error('Form submission failed');
            }
          } catch (error) {
            console.error('Form submission error:', error);
            alert('Submission failed. Please try again.');
          }
        };

        form.addEventListener('submit', handleSubmit);
        return () => form.removeEventListener('submit', handleSubmit);
      }
    }
  }, [content, onSuccess]);

  if (hasSubmitted) {
    return; // Don't render anything after submission
  }

  return (
    <div className="integration-modal">
      <div className="integration-modal-content" ref={modalRef}>
        <span className="integration-modal-close" onClick={onClose}>&times;</span>
        <div 
          id="integration-modal-body" 
          ref={contentRef}
          dangerouslySetInnerHTML={{ __html: content }}
        />
      </div>
    </div>
  );
};

export default IntegrationModal; 