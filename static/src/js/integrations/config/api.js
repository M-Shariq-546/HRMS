// API Configuration for React Integrations App

// Get base URL from environment or use default
const getBaseUrl = () => {
  // Check for Django configuration first
  if (typeof window !== 'undefined' && window.DJANGO_CONFIG) {
    // Use Django's static URL or current origin
    return window.location.origin;
  }
  
  // Check for custom environment variable
  if (typeof process !== 'undefined' && process.env.REACT_APP_API_BASE_URL) {
    return process.env.REACT_APP_API_BASE_URL;
  }
  
  // Default to current origin
  return window.location.origin;
};

// Get CSRF token from Django configuration
const getCSRFTokenFromDjango = () => {
  if (typeof window !== 'undefined' && window.DJANGO_CONFIG) {
    return window.DJANGO_CONFIG.csrfToken;
  }
  return null;
};

// API endpoints configuration
export const API_CONFIG = {
  baseUrl: getBaseUrl(),
  endpoints: {
    // Integration management
    integrations: '/integrations/integrations_react/',
    connectIntegration: (service) => `/integrations/connect-integration/${service}/`,
    disconnectIntegration: (service) => `/integrations/integrations/${service}/disconnect/`,
    
    // Documenso
    documensoTemplates: '/integrations/documenso-templates-fields/',
    saveDocumensoMappings: '/integrations/save-documenso-mappings/',
    
    // Wise
    wiseRecipients: '/integrations/wise-recipients/',
    wiseAddRecipient: '/integrations/wise-add-recipient/',
    wiseTransfers: '/integrations/wise-recent-transfers/',
    
    // Test
    testApi: '/integrations/test-api/',
  }
};

// Helper function to build full URLs
export const buildApiUrl = (endpoint) => {
  return `${API_CONFIG.baseUrl}${endpoint}`;
};

// Helper function to get CSRF token
export const getCSRFToken = () => {
  // First try Django configuration
  const djangoToken = getCSRFTokenFromDjango();
  if (djangoToken) {
    return djangoToken;
  }
  
  // Fallback to cookie
  const match = document.cookie.match(/csrftoken=([^;]+)/);
  return match ? match[1] : "";
};

// Helper function for API requests
export const apiRequest = async (url, options = {}) => {
  const defaultOptions = {
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': getCSRFToken(),
    },
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  return fetch(url, finalOptions);
};

// Helper function for form data requests
export const formDataRequest = async (url, formData, options = {}) => {
  const defaultOptions = {
    headers: {
      'X-CSRFToken': getCSRFToken(),
    },
  };

  const finalOptions = {
    ...defaultOptions,
    ...options,
    headers: {
      ...defaultOptions.headers,
      ...options.headers,
    },
  };

  return fetch(url, {
    ...finalOptions,
    body: formData,
  });
};

// Helper function to get Django configuration
export const getDjangoConfig = () => {
  if (typeof window !== 'undefined' && window.DJANGO_CONFIG) {
    return window.DJANGO_CONFIG;
  }
  return null;
};

// Helper function to check if we're in debug mode
export const isDebugMode = () => {
  const config = getDjangoConfig();
  return config ? config.debug : false;
}; 