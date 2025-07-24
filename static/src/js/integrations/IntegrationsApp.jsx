import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import IntegrationCard from './components/IntegrationCard';
import IntegrationModal from './components/IntegrationModal';
import DocumensoSettingsModal from './components/DocumensoSettingsModal';
import WiseSettingsModal from './components/WiseSettingsModal';
import WiseTransfersModal from './components/WiseTransfersModal';
import Alert from './components/Alert';
import './styles/IntegrationsApp.css';

const IntegrationsApp = () => {
  const [integrations, setIntegrations] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [modalContent, setModalContent] = useState(null);
  const [showDocumensoModal, setShowDocumensoModal] = useState(false);
  const [showWiseSettingsModal, setShowWiseSettingsModal] = useState(false);
  const [showWiseTransfersModal, setShowWiseTransfersModal] = useState(false);
  const [alert, setAlert] = useState(null);

  useEffect(() => {
    fetchIntegrations();
  }, []);

  const fetchIntegrations = async () => {
    try {
      console.log('Fetching integrations from:', '/integrations/integrations_list/');
      setLoading(true);
      console.log('Fetching integrations from:', '/integrations/integrations_list/');
      const response = await fetch('/integrations/integrations_list/', {
        headers: {
          'Accept': 'application/json',
        },
      });
      console.log('Response status:', response.status);
      if (response.ok) {
        const data = await response.json();
        console.log('Integration data:', data);
        setIntegrations(data.integration_status || {});
      } else {
        const errorText = await response.text();
        console.error('Response error:', errorText);
        try {
          const errorData = JSON.parse(errorText);
          if (errorData.error && errorData.error.includes('select a company')) {
            throw new Error('Please select a company to view integrations.');
          }
        } catch (e) {
          // If error text is not JSON, use the original error
        }
        throw new Error(`Failed to fetch integrations: ${response.status}`);
      }
    } catch (err) {
      console.error('Fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleConnect = async (service) => {
    try {
      if (service === 'slack') {
        // Use the new Slack API endpoint
        const response = await fetch('/integrations/slack-connect-api/', {
          method: 'GET',
          headers: {
            'Accept': 'application/json',
          },
        });
        
        if (response.ok) {
          const data = await response.json();
          if (data.success) {
            // Show a modal with the Slack configuration form
            setModalContent(`
              <div style="padding: 20px;">
                <h3 style="margin-bottom: 20px; color: #333;">Configure Slack Integration</h3>
                <form id="slack-config-form">
                  <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Client ID:</label>
                    <input type="text" name="client_id" value="${data.form_data.client_id}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                  </div>
                  <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Client Secret:</label>
                    <input type="password" name="client_secret" value="${data.form_data.client_secret}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                  </div>
                  <div style="margin-bottom: 15px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Redirect URI:</label>
                    <input type="text" name="redirect_uri" value="${data.form_data.redirect_uri}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                  </div>
                  <div style="margin-bottom: 20px;">
                    <label style="display: block; margin-bottom: 5px; font-weight: bold;">Scopes:</label>
                    <input type="text" name="scopes" value="${data.form_data.scopes}" style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;" required />
                  </div>
                  <button type="submit" style="background: #3b82f6; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer;">Save & Connect</button>
                </form>
              </div>
            `);
            setShowModal(true);
          } else {
            showAlert('error', data.error || 'Failed to load Slack configuration');
          }
        } else {
          showAlert('error', 'Failed to load Slack configuration');
        }
      } else {
        // For other integrations, use the existing modal approach
        const response = await fetch(`/integrations/connect-integration/${service}/`);
        if (response.ok) {
          const html = await response.text();
          setModalContent(html);
          setShowModal(true);
        } else {
          throw new Error('Failed to load connection form');
        }
      }
    } catch (err) {
      showAlert('error', 'Error loading connection form');
    }
  };

  const handleDisconnect = async (service) => {
    console.log('=== DISCONNECT DEBUG ===');
    console.log('Service to disconnect:', service);
    console.log('CSRF Token available:', !!getCSRFToken());
    console.log('CSRF Token length:', getCSRFToken().length);
    
    // Try to use SweetAlert if available, otherwise fallback to confirm
    let confirmed = false;
    if (typeof Swal !== 'undefined') {
      const result = await Swal.fire({
        title: 'Confirm Disconnect',
        text: `Are you sure you want to disconnect ${service}?`,
        icon: 'warning',
        showCancelButton: true,
        confirmButtonColor: '#d33',
        cancelButtonColor: '#3085d6',
        confirmButtonText: 'Yes, disconnect!',
        cancelButtonText: 'Cancel'
      });
      confirmed = result.isConfirmed;
    } else {
      confirmed = confirm(`Are you sure you want to disconnect ${service}?`);
    }
    
    if (!confirmed) {
      console.log('User cancelled disconnect');
      return;
    }

    console.log('User confirmed disconnect, making API call...');

    try {
      console.log('Disconnecting service:', service);
      
      // Get fresh CSRF token
      const csrfToken = await getFreshCSRFToken();
      console.log('Fresh CSRF Token:', csrfToken);
      console.log('CSRF Token length:', csrfToken.length);
      
      const url = `/integrations/integrations/${service}/disconnect/`;
      console.log('Disconnect URL:', url);
      
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          'X-CSRFToken': csrfToken,
          'Accept': 'application/json',
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          'service': service,
        }),
      });

      console.log('Disconnect response status:', response.status);
      console.log('Disconnect response headers:', response.headers);

      if (response.ok) {
        const data = await response.json();
        console.log('Disconnect response data:', data);
        if (data.success) {
          showAlert('success', data.message || `${service} integration has been disconnected.`);
          await fetchIntegrations(); // Refresh the integrations list
        } else {
          showAlert('error', data.error || 'Failed to disconnect integration');
        }
      } else {
        const errorData = await response.json().catch(() => ({}));
        console.error('Disconnect error response:', errorData);
        throw new Error(errorData.error || `Failed to disconnect integration (${response.status})`);
      }
    } catch (err) {
      console.error('Disconnect error:', err);
      if (err.name === 'TypeError' && err.message.includes('fetch')) {
        showAlert('error', 'Network error: Unable to connect to server. Please check your connection.');
      } else {
        showAlert('error', err.message || 'An error occurred while disconnecting the integration.');
      }
    }
  };

  const showAlert = (type, message) => {
    setAlert({ type, message });
    setTimeout(() => setAlert(null), 5000);
  };

  const getCSRFToken = () => {
    const match = document.cookie.match(/csrftoken=([^;]+)/);
    return match ? match[1] : "";
  };

  const getFreshCSRFToken = async () => {
    try {
      const response = await fetch('/integrations/get-csrf-token/', {
        method: 'GET',
        headers: {
          'Accept': 'application/json',
        },
      });
      if (response.ok) {
        const data = await response.json();
        return data.csrf_token;
      }
    } catch (error) {
      console.error('Error getting fresh CSRF token:', error);
    }
    return getCSRFToken();
  };

  if (loading) {
    return (
      <div className="integrations-loading">
        <div className="spinner"></div>
        <p>Loading integrations...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="integrations-error">
        <p>Error: {error}</p>
        <button onClick={fetchIntegrations}>Retry</button>
      </div>
    );
  }

  return (
    <div className="integrations-app">
      {alert && <Alert type={alert.type} message={alert.message} onClose={() => setAlert(null)} />}
      
      <div className="integrations-container">
        <div className="integrations-grid">
          <IntegrationCard
            service="slack"
            name="Slack"
            description="Connect your Slack workspace to receive notifications and manage team communications."
            isConnected={integrations.slack?.is_connected || false}
            onConnect={() => handleConnect('slack')}
            onDisconnect={() => handleDisconnect('slack')}
            logoClass="slack-logo"
            icon="logo-slack"
          />

          <IntegrationCard
            service="documenso"
            name="Documenso"
            description="Connect your Documenso account to enable document signing, approvals, and workflow automation."
            isConnected={integrations.documenso?.is_connected || false}
            onConnect={() => handleConnect('documenso')}
            onDisconnect={() => handleDisconnect('documenso')}
            onSettings={() => setShowDocumensoModal(true)}
            logoClass="documenso-logo"
            icon="document-text"
          />

          <IntegrationCard
            service="wise"
            name="Wise"
            description="Connect your Wise account to enable international payments, transfers, and payroll automation."
            isConnected={integrations.wise?.is_connected || false}
            onConnect={() => handleConnect('wise')}
            onDisconnect={() => handleDisconnect('wise')}
            onSettings={() => setShowWiseSettingsModal(true)}
            onTransactions={() => setShowWiseTransfersModal(true)}
            logoClass="logo-wise"
            icon="card-outline"
          />
        </div>
      </div>

      {showModal && (
        <IntegrationModal
          content={modalContent}
          onClose={() => setShowModal(false)}
          onSuccess={() => {
            setShowModal(false);
            fetchIntegrations();
          }}
        />
      )}

      {showDocumensoModal && (
        <DocumensoSettingsModal
          onClose={() => setShowDocumensoModal(false)}
          onSuccess={() => {
            setShowDocumensoModal(false);
            showAlert('success', 'Documenso settings saved successfully.');
            fetchIntegrations(); // Refresh the integrations list
          }}
        />
      )}

      {showWiseSettingsModal && (
        <WiseSettingsModal
          onClose={() => setShowWiseSettingsModal(false)}
          onSuccess={() => {
            setShowWiseSettingsModal(false);
            showAlert('success', 'Wise settings updated successfully.');
          }}
        />
      )}

      {showWiseTransfersModal && (
        <WiseTransfersModal
          onClose={() => setShowWiseTransfersModal(false)}
        />
      )}
    </div>
  );
};

// Initialize the React app
document.addEventListener('DOMContentLoaded', () => {
  const container = document.getElementById('integrations-react-app');
  if (container) {
    const root = createRoot(container);
    root.render(<IntegrationsApp />);
  }
});

export default IntegrationsApp; 