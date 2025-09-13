# Android Server Integration Plan
## Server-Side Changes Required for Android Client Support

> **Status**: Planning document - to be implemented after Android client development
> 
> **Context**: This document consolidates all server-side changes needed to support the InfoAgent Android client. Implement these changes when ready to integrate with the mobile app.

### Overview
This document outlines the complete server-side implementation plan for supporting the InfoAgent Android client, including API extensions, database changes, and processing pipeline enhancements.

## 1. API Extensions Required

### 1.1 Authentication for Mobile Clients

**Update Authentication Section in API Specification:**
```markdown
## Authentication

**MVP**: No authentication required
**Android Client**: Device-based authentication with API keys
**Future**: JWT token authentication with user accounts
```

### 1.2 Enhanced Memory Creation API

**Extend POST /memories endpoint:**
```json
{
  "content": "Meeting with Sarah about project timeline",
  "title": "Custom Title", // optional
  "source": {             // optional, for mobile clients
    "type": "sms|screenshot|share|notification|manual",
    "app": "messages|camera|chrome|etc",
    "device_id": "unique_device_identifier", 
    "timestamp": "2024-01-15T10:30:00Z"
  },
  "metadata": {           // optional, source-specific data
    "sender": "+1234567890",
    "message_type": "incoming",
    "image_path": "/storage/screenshots/img.png"
  }
}
```

### 1.3 New Mobile-Specific Endpoints

**Device Registration:**
```
POST /api/v1/devices/register
- Register Android device for authentication
- Generate and return API key
- Store device information
```

**Batch Memory Upload:**
```
POST /api/v1/memories/batch
- Create multiple memories efficiently
- Support mobile sync scenarios
- Handle partial success cases
```

**Device Status:**
```
GET /api/v1/devices/{device_id}/status
- Check sync status
- Return statistics
- Monitor device health
```

## 2. Database Schema Extensions

### 2.1 Memory Table Extensions
```sql
-- Add columns to existing memories table
ALTER TABLE memories ADD COLUMN source_type TEXT DEFAULT 'manual';
ALTER TABLE memories ADD COLUMN source_app TEXT;
ALTER TABLE memories ADD COLUMN device_id TEXT;  
ALTER TABLE memories ADD COLUMN source_timestamp TIMESTAMP;
ALTER TABLE memories ADD COLUMN source_metadata TEXT; -- JSON blob
```

### 2.2 New Device Registration Table
```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    api_key TEXT UNIQUE NOT NULL,
    device_info TEXT, -- JSON blob with model, OS version, etc.
    registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_sync TIMESTAMP,
    is_active BOOLEAN DEFAULT 1
);
```

## 3. Server-Side Development Tasks

### Phase 1: Core Infrastructure
- [ ] **Database Migration**: Create migration scripts for mobile support
- [ ] **Device Model**: Implement Device registration model and API key system
- [ ] **Authentication Middleware**: Add API key validation for mobile routes
- [ ] **Device Registration API**: POST /devices/register endpoint
- [ ] **Memory Model Updates**: Extend Memory model with source tracking

### Phase 2: Enhanced APIs
- [ ] **Extended Memory API**: Update POST /memories with source metadata
- [ ] **Batch Upload API**: Implement POST /memories/batch endpoint
- [ ] **Device Status API**: GET /devices/{id}/status endpoint
- [ ] **Source-Aware Processing**: AI processing based on data source type
- [ ] **Mobile Privacy Filtering**: Content filtering for mobile sources

### Phase 3: Processing Pipeline
- [ ] **OCR Integration**: Support for screenshot text extraction
- [ ] **SMS Processing**: Specialized handling for SMS metadata
- [ ] **Notification Processing**: Parse and categorize notification content
- [ ] **Share Intent Processing**: Handle shared URLs, text, files
- [ ] **Mobile-Specific Prompts**: AI extraction templates per source type

### Phase 4: Sync & Performance
- [ ] **Incremental Sync**: Timestamp-based sync API
- [ ] **Conflict Resolution**: Handle duplicate/conflicting memories
- [ ] **Queue Management**: Server-side retry logic for failed uploads
- [ ] **Compression**: Bandwidth optimization for mobile data
- [ ] **Rate Limiting**: Protect against mobile client abuse

### Phase 5: Security & Privacy  
- [ ] **End-to-End Encryption**: Encrypt mobile data transmission
- [ ] **Privacy Controls**: Granular settings per data source
- [ ] **Content Filtering**: Advanced filtering for sensitive information
- [ ] **Consent Tracking**: User consent management and compliance
- [ ] **Audit Logging**: Track all mobile data operations

### Phase 6: Testing & Documentation
- [ ] **API Tests**: Comprehensive tests for mobile endpoints
- [ ] **Integration Tests**: Android client simulation
- [ ] **Mock Server**: Development server for Android testing
- [ ] **API Documentation**: Update docs with mobile examples
- [ ] **SDK Documentation**: Mobile client integration guides

## 4. Code Structure Changes

### 4.1 New API Routes
```python
# info_agent/api/routes/devices.py
from flask import Blueprint, request
from info_agent.services.mobile_service import MobileService

devices_bp = Blueprint('devices', __name__)

@devices_bp.route('/register', methods=['POST'])
def register_device():
    """Register new Android device and return API key"""
    device_info = request.get_json()
    # Generate API key and register device
    pass

@devices_bp.route('/<device_id>/status', methods=['GET'])  
def get_device_status(device_id):
    """Get device sync status and statistics"""
    # Return device sync information
    pass

# info_agent/api/routes/memories.py  
@memories_bp.route('/batch', methods=['POST'])
def create_memories_batch():
    """Create multiple memories in batch"""
    memories_data = request.get_json()['memories']
    # Process batch of memories efficiently
    pass
```

### 4.2 Enhanced Models
```python
# info_agent/core/models.py
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime

@dataclass
class MemorySource:
    type: str  # sms, screenshot, share, notification, manual
    app: Optional[str]
    device_id: Optional[str] 
    timestamp: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

@dataclass
class Device:
    id: Optional[int]
    device_id: str
    device_name: str
    api_key: str
    device_info: Dict[str, Any]
    registered_at: datetime
    last_sync: Optional[datetime]
    is_active: bool

@dataclass  
class Memory:
    # ... existing fields ...
    source: Optional[MemorySource] = None
```

### 4.3 Mobile Service Layer
```python
# info_agent/services/mobile_service.py
class MobileService:
    def __init__(self, repository, ai_client):
        self.repository = repository
        self.ai_client = ai_client
    
    def register_device(self, device_info: Dict) -> str:
        """Generate API key and register device"""
        pass
    
    def process_mobile_memory(self, content: str, source: MemorySource) -> Memory:
        """Source-aware memory processing with specialized AI prompts"""
        pass
    
    def batch_create_memories(self, memories_data: List[Dict]) -> BatchResult:
        """Efficient batch processing with transaction support"""
        pass
    
    def get_device_status(self, device_id: str) -> DeviceStatus:
        """Get device sync statistics and status"""
        pass
```

## 5. Configuration & Environment

### 5.1 Environment Variables
```bash
# Mobile client configuration  
MOBILE_CLIENTS_ENABLED=true
API_KEY_EXPIRY_DAYS=365
MAX_BATCH_SIZE=50
MOBILE_UPLOAD_RATE_LIMIT=100  # requests per hour per device

# Privacy settings
DEFAULT_PRIVACY_LEVEL=medium
ENABLE_OCR_PROCESSING=true
CONTENT_FILTERING_ENABLED=true
```

### 5.2 Privacy Configuration
```python
# Default privacy settings for mobile clients
MOBILE_PRIVACY_DEFAULTS = {
    "sms": {
        "enabled": True,
        "filter_sensitive": True, 
        "include_metadata": True
    },
    "screenshots": {
        "enabled": False,  # Requires explicit consent
        "ocr_enabled": True,
        "filter_sensitive": True
    },
    "notifications": {
        "enabled": False,
        "whitelist_apps": [],
        "filter_sensitive": True  
    }
}
```

## 6. Testing Strategy

### 6.1 Development Testing
- **Mock Android Client**: Simulate mobile requests for development
- **Postman Collection**: API testing collection for mobile endpoints
- **Unit Tests**: Core mobile service functionality
- **Integration Tests**: End-to-end mobile workflow testing

### 6.2 Android Integration Testing
- **Device Registration Flow**: Test complete device onboarding
- **Batch Upload Performance**: Test with varying batch sizes
- **Network Failure Scenarios**: Test offline/retry functionality
- **Privacy Filter Validation**: Ensure sensitive data filtering

## 7. Implementation Timeline

### Recommended Implementation Order:
1. **Start with Phase 1** - Core infrastructure and database changes
2. **Phase 2** - Basic API extensions for memory creation
3. **Test with simple Android prototype** - Validate basic functionality
4. **Phase 3** - Enhanced processing for different source types
5. **Phase 4 & 5** - Advanced features, security, performance
6. **Phase 6** - Testing, documentation, production readiness

### Dependencies:
- **Android Client MVP** should be developed in parallel
- **Server integration** can begin once Android client has basic data collection
- **Advanced features** require bidirectional development (client + server)

## 8. Future Considerations

### Scalability Enhancements:
- **Multi-user Support**: User accounts and device management
- **Cross-device Sync**: Sync memories across user's devices
- **Advanced Analytics**: Usage patterns and insights
- **Real-time Features**: Push notifications, live sync

### Platform Expansion:
- **iOS Client Support**: Reuse same API infrastructure
- **Desktop Integration**: Companion apps using same endpoints
- **Web Extension**: Browser-based memory collection

---

**Next Steps**: 
1. Complete Android client MVP development
2. Begin Phase 1 server implementation 
3. Test integration with iterative development approach
4. Scale up features based on usage and feedback

**Reference Documents**:
- `android_client/design.md` - Android client architecture
- `android_client/tasks.md` - Android client development plan
- `docs/android_integration.md` - Detailed server integration specs