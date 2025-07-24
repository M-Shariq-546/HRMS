---
noteId: "e2be96b067b811f08fe3d3ffceccbe14"
tags: []

---

# Horilla Integrations React App

A modern React.js implementation of the Horilla integrations management system, providing an enhanced user interface while maintaining full compatibility with the existing Django backend.

## 🌟 Features

- **Modern React UI**: Beautiful, responsive card-based interface
- **Environment-Based URLs**: Configurable base URLs from environment variables
- **Full Django Integration**: Seamless communication with existing Django APIs
- **Real-time Updates**: Dynamic status updates and form handling
- **Modal Dialogs**: Interactive settings and transaction views
- **CSRF Protection**: Secure form submissions with Django CSRF tokens
- **Responsive Design**: Mobile-friendly interface
- **Error Handling**: Comprehensive error states and user feedback

## 🚀 Quick Start

### Option 1: Development Setup (No Webpack Required)

1. **Run the development setup script:**
   ```bash
   setup_integrations_dev.bat
   ```

2. **Start your Django server:**
   ```bash
   python manage.py runserver
   ```

3. **Access the development version:**
   ```
   http://localhost:8000/integrations/integrations_react_dev/
   ```

### Option 2: Production Setup (With Webpack)

1. **Install Node.js dependencies:**
   ```bash
   npm install
   ```

2. **Build the React application:**
   ```bash
   npm run build
   ```

3. **Start your Django server:**
   ```bash
   python manage.py runserver
   ```

4. **Access the production version:**
   ```
   http://localhost:8000/integrations/integrations_react/
   ```

## 📁 Project Structure

```
static/src/js/integrations/
├── config/
│   └── api.js                    # API configuration and URL management
├── components/
│   ├── IntegrationCard.jsx       # Individual integration card component
│   ├── IntegrationModal.jsx      # Generic modal for forms
│   ├── DocumensoSettingsModal.jsx # Documenso-specific settings
│   ├── WiseSettingsModal.jsx     # Wise recipients management
│   ├── WiseTransfersModal.jsx    # Wise transfers display
│   ├── Alert.jsx                 # Notification component
│   └── *.css                     # Component-specific styles
├── styles/
│   └── IntegrationsApp.css       # Main app styles
└── IntegrationsApp.jsx           # Main React application

integrations/templates/integrations/
├── integrations_react.html        # Production React template
└── integrations_react_dev.html    # Development React template
```

## 🔧 Environment Configuration

### API Base URL Configuration

The React app automatically detects the base URL using the following priority:

1. **Django Configuration** (Recommended):
   ```javascript
   // Automatically set from Django template
   window.DJANGO_CONFIG = {
     staticUrl: '{% static "" %}',
     csrfToken: '{{ csrf_token }}',
     // ... other Django settings
   };
   ```

2. **Environment Variable**:
   ```bash
   # Set in your environment
   REACT_APP_API_BASE_URL=https://your-domain.com
   ```

3. **Fallback**: Uses `window.location.origin`

### CSRF Token Management

The app automatically handles CSRF tokens:

1. **Primary**: Uses Django's CSRF token from template
2. **Fallback**: Extracts from browser cookies

## 🌐 Available URLs

| URL | Description | Requirements |
|-----|-------------|--------------|
| `/integrations/integrations_react_dev/` | Development version | None |
| `/integrations/integrations_react/` | Production version | Webpack build |
| `/integrations/integrations_list/` | Original Django template | None |

## 🔌 API Endpoints

The React app communicates with these Django endpoints:

### Integration Management
- `GET /integrations/integrations_list/` - Fetch integration status
- `GET /integrations/connect-integration/{service}/` - Load connection forms
- `POST /integrations/integrations/{service}/disconnect/` - Disconnect integration

### Documenso Integration
- `GET /integrations/documenso-templates-fields/` - Fetch templates and mappings
- `POST /integrations/save-documenso-mappings/` - Save template mappings

### Wise Integration
- `GET /integrations/wise-recipients/` - Fetch Wise recipients
- `POST /integrations/wise-add-recipient/` - Add new recipient
- `GET /integrations/wise-recent-transfers/` - Fetch recent transfers

## 🎨 Components

### IntegrationCard
Displays individual integration status with connect/disconnect actions.

**Props:**
- `service`: Integration service name
- `name`: Display name
- `description`: Integration description
- `isConnected`: Connection status
- `onConnect`: Connect handler
- `onDisconnect`: Disconnect handler
- `onSettings`: Settings handler (optional)
- `onTransactions`: Transactions handler (optional)
- `logoClass`: CSS class for logo styling
- `icon`: Ionicon name

### IntegrationModal
Generic modal for displaying Django forms.

**Props:**
- `content`: HTML content to display
- `onClose`: Close handler
- `onSuccess`: Success handler

### DocumensoSettingsModal
Specialized modal for Documenso template mapping.

**Features:**
- Template field mapping
- Notification message configuration
- Processing hours selection
- Auto-save functionality

### WiseSettingsModal
Wise recipients management interface.

**Features:**
- List existing recipients
- Add new recipients
- Form validation
- Real-time feedback

### WiseTransfersModal
Display recent Wise transfers in table format.

**Features:**
- Transfer status display
- Date formatting
- Payroll reference links
- Error handling

## 🛠️ Development

### Adding New Integrations

1. **Update API Configuration:**
   ```javascript
   // In static/src/js/integrations/config/api.js
   endpoints: {
     // Add your new endpoints
     newIntegration: '/integrations/new-integration/',
   }
   ```

2. **Add Integration Card:**
   ```javascript
   // In IntegrationsApp.jsx
   <IntegrationCard
     service="new-service"
     name="New Service"
     description="Description of the new service"
     isConnected={integrations.newService?.is_connected || false}
     onConnect={() => handleConnect('new-service')}
     onDisconnect={() => handleDisconnect('new-service')}
     logoClass="new-service-logo"
     icon="new-icon"
   />
   ```

3. **Add Django View:**
   ```python
   # In integrations/views.py
   def new_integration_view(request):
       # Your view logic
       pass
   ```

### Styling

Component-specific styles are in separate CSS files:
- `IntegrationCard.css` - Card styling
- `IntegrationModal.css` - Modal styling
- `DocumensoSettingsModal.css` - Settings modal
- `WiseSettingsModal.css` - Wise settings
- `WiseTransfersModal.css` - Transfers table
- `Alert.css` - Notification styling

## 🔒 Security

- **CSRF Protection**: All POST requests include Django CSRF tokens
- **Input Validation**: Client and server-side validation
- **Error Handling**: Comprehensive error states and user feedback
- **XSS Prevention**: Proper HTML sanitization in modals

## 🌍 Browser Support

- **Modern Browsers**: Chrome 80+, Firefox 75+, Safari 13+, Edge 80+
- **Mobile**: iOS Safari 13+, Chrome Mobile 80+
- **Fallback**: Graceful degradation for older browsers

## 📱 Responsive Design

The interface is fully responsive with:
- **Desktop**: Multi-column grid layout
- **Tablet**: Adjusted spacing and typography
- **Mobile**: Single-column layout with touch-friendly buttons

## 🚨 Troubleshooting

### Common Issues

1. **Webpack not found:**
   ```bash
   npm install -g webpack webpack-cli
   ```

2. **CSRF token errors:**
   - Ensure Django's CSRF middleware is enabled
   - Check that cookies are enabled in browser

3. **API endpoint errors:**
   - Verify Django URLs are correctly configured
   - Check browser network tab for 404/500 errors

4. **React components not loading:**
   - Check browser console for JavaScript errors
   - Ensure all CDN links are accessible

### Debug Mode

Enable debug mode in Django settings:
```python
DEBUG = True
```

The React app will show additional logging when `window.DJANGO_CONFIG.debug` is true.

## 📈 Performance

### Optimization Tips

1. **Production Build**: Always use `npm run build` for production
2. **CDN Usage**: React and Babel are loaded from CDN for faster development
3. **Lazy Loading**: Consider implementing lazy loading for modals
4. **Caching**: Django's static file caching is utilized

### Bundle Size

- **Development**: ~2MB (includes React dev tools)
- **Production**: ~500KB (minified and optimized)

## 🔄 Migration from Django Templates

The React app maintains full compatibility with existing Django functionality:

1. **Same API Endpoints**: All existing Django views work unchanged
2. **Same Authentication**: Uses Django's session management
3. **Same Permissions**: Respects Django's permission system
4. **Same Data Models**: Uses existing Django models and serializers

## 📝 License

This project is part of the Horilla HR Management System.

## 🤝 Contributing

1. Follow the existing code style
2. Add tests for new features
3. Update documentation for API changes
4. Test on multiple browsers and devices

---

**Note**: This React implementation provides a modern, interactive interface while maintaining full compatibility with the existing Django backend. The development version (`integrations_react_dev.html`) allows for quick testing without requiring webpack setup. 