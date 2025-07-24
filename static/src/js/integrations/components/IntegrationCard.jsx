import React from 'react';
import './IntegrationCard.css';

const IntegrationCard = ({
  service,
  name,
  description,
  isConnected,
  onConnect,
  onDisconnect,
  onSettings,
  onTransactions,
  logoClass,
  icon
}) => {
  return (
    <div className="integration-card">
      <div className="integration-header">
        <div className={`integration-logo ${logoClass}`}>
          <ion-icon name={icon}></ion-icon>
        </div>
        
        <div className="integration-info">
          <div className="integration-name">{name}</div>
          <div className={`integration-status ${isConnected ? 'status-connected' : 'status-disconnected'}`}>
            {isConnected ? 'Connected' : 'Disconnected'}
          </div>
        </div>
      </div>

      <div className="integration-description">
        {description}
      </div>

      <div className="integration-actions">
        {isConnected ? (
          <>
            <button 
              className="btn-disconnect" 
              onClick={onDisconnect}
              title={`Disconnect ${name}`}
            >
              <ion-icon name="close-circle-outline"></ion-icon>
              Disconnect
            </button>
            
            {onSettings && (
              <button 
                className="btn-settings" 
                onClick={onSettings}
                title="Settings"
              >
                <ion-icon name="settings-outline"></ion-icon>
              </button>
            )}
            
            {onTransactions && (
              <button 
                className="btn-transactions" 
                onClick={onTransactions}
                title="See Transactions"
              >
                <ion-icon name="cash-outline"></ion-icon>
                Transactions
              </button>
            )}
          </>
        ) : (
          <button 
            className="btn-connect" 
            onClick={onConnect}
            title={`Connect ${name}`}
          >
            <ion-icon name="link-outline"></ion-icon>
            Connect
          </button>
        )}
      </div>
    </div>
  );
};

export default IntegrationCard; 