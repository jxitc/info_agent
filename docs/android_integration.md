# Android Client Integration
## InfoAgent Server Extensions for Mobile Data Collection

### Overview
This document outlines the server-side changes required to support the InfoAgent Android client for automatic data collection from mobile devices.

### Integration Requirements

#### 1. Database Schema Extensions
The existing Memory table needs enhancement to support mobile device context and source tracking.

**New Columns for Memory Table:**
```sql
ALTER TABLE memories ADD COLUMN source_type TEXT DEFAULT 'manual';
ALTER TABLE memories ADD COLUMN source_app TEXT;
ALTER TABLE memories ADD COLUMN device_id TEXT;
ALTER TABLE memories ADD COLUMN source_timestamp TIMESTAMP;
ALTER TABLE memories ADD COLUMN source_metadata TEXT; -- JSON blob
```

**New Device Registration Table:**
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

#### 2. API Authentication System
**Device Registration Flow:**
1. Android app generates unique device ID
2. App calls `/api/v1/devices/register` with device info
3. Server generates API key and stores device registration
4. App stores API key securely for future requests

**Request Authentication:**
- All mobile requests include `X-API-Key` header
- Server validates API key against devices table
- Invalid/expired keys return 401 Unauthorized

#### 3. Enhanced Memory Processing Pipeline
**Source-Aware Processing:**
- Different AI prompts based on source type (SMS vs screenshot vs share)
- Source-specific metadata extraction and storage
- Privacy filtering based on source and content type

**Batch Processing Support:**
- `/api/v1/memories/batch` endpoint for efficient mobile sync
- Transaction-based batch inserts for data consistency
- Partial success handling with detailed error reporting

#### 4. Mobile-Specific Features
**Privacy Controls:**
- Device-level privacy settings
- Content filtering rules per source type
- User consent tracking and management

**Sync Management:**
- Offline queue support with conflict resolution
- Incremental sync based on timestamps
- Device status tracking and reporting

### Implementation Tasks

#### Phase 1: Core Infrastructure
1. **Database Migrations**
   - Create migration scripts for new schema
   - Update model classes for source tracking
   - Add device registration model

2. **Authentication Layer**
   - Implement API key generation and validation
   - Create device registration endpoint
   - Add authentication middleware for mobile routes

3. **Enhanced API Endpoints**
   - Extend POST /memories for source metadata
   - Create POST /memories/batch endpoint
   - Add device management endpoints

#### Phase 2: Processing Enhancements
4. **Source-Aware AI Processing**
   - Update extraction prompts for different sources
   - Add source-specific metadata processing
   - Implement privacy filtering pipeline

5. **Mobile Data Formats**
   - Support image/OCR content processing
   - Handle SMS-specific metadata (sender, type)
   - Process notification content and context

#### Phase 3: Advanced Features
6. **Sync & Conflict Resolution**
   - Implement incremental sync logic
   - Add conflict detection and resolution
   - Create sync status tracking

7. **Privacy & Security**
   - Add end-to-end encryption support
   - Implement granular privacy controls
   - Create audit logging for mobile data

### Code Structure Changes

#### New API Routes
```python
# info_agent/api/routes/devices.py
@devices_bp.route('/register', methods=['POST'])
def register_device():
    # Device registration logic
    pass

@devices_bp.route('/<device_id>/status', methods=['GET'])
def get_device_status(device_id):
    # Device sync status
    pass

# info_agent/api/routes/memories.py
@memories_bp.route('/batch', methods=['POST'])
def create_memories_batch():
    # Batch memory creation
    pass
```

#### Enhanced Models
```python
# info_agent/core/models.py
@dataclass
class MemorySource:
    type: str  # sms, screenshot, share, notification, manual
    app: Optional[str]
    device_id: Optional[str]
    timestamp: Optional[datetime]
    metadata: Optional[Dict[str, Any]]

@dataclass
class Memory:
    # ... existing fields ...
    source: Optional[MemorySource] = None
```

#### Mobile Service Layer
```python
# info_agent/services/mobile_service.py
class MobileService:
    def register_device(self, device_info: Dict) -> str:
        # Generate API key and register device
        pass
    
    def process_mobile_memory(self, content: str, source: MemorySource) -> Memory:
        # Source-aware memory processing
        pass
    
    def batch_create_memories(self, memories_data: List[Dict]) -> BatchResult:
        # Efficient batch processing
        pass
```

### Testing Strategy

#### Unit Tests
- Device registration and authentication
- Source-aware memory processing
- Batch operation handling
- Privacy filtering logic

#### Integration Tests
- End-to-end mobile client simulation
- API authentication flow testing
- Batch sync performance testing
- Error handling and resilience

#### Mobile Client Testing
- Mock server for Android development
- Real device testing scenarios
- Network failure and retry testing
- Privacy control validation

### Configuration Changes

#### Environment Variables
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

#### Privacy Settings Schema
```python
# Default privacy configuration for mobile clients
MOBILE_PRIVACY_DEFAULTS = {
    "sms": {
        "enabled": True,
        "filter_sensitive": True,
        "include_metadata": True
    },
    "screenshots": {
        "enabled": False,  # Requires explicit user consent
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

### Security Considerations

#### Data Protection
- All mobile data encrypted in transit (HTTPS)
- API keys stored securely with rotation capability
- Privacy-sensitive content filtered before storage
- User consent tracked for all data collection types

#### Access Control
- Device-specific API keys with limited scope
- Rate limiting per device to prevent abuse
- Audit logging for all mobile data operations
- Ability to revoke device access remotely

#### Compliance
- GDPR-compliant data handling and deletion
- Clear consent mechanisms for each data type
- User data export and deletion capabilities
- Transparency in data collection and processing

### Performance Considerations

#### Batch Processing
- Optimize database bulk inserts for mobile sync
- Implement queue-based processing for large batches
- Add compression for network efficiency
- Cache frequently accessed device information

#### Scaling
- Database indexing for device and source queries
- Connection pooling for mobile client requests
- Background job processing for heavy AI operations
- Monitoring and alerting for mobile client health

### Future Enhancements

#### Advanced Features
- Multi-device user accounts and sync
- Cross-device memory correlation
- Advanced AI processing with device context
- Real-time push notifications for important memories

#### Platform Expansion
- iOS client support with same API
- Desktop companion app integration
- Browser extension for web content capture
- Smart home device integration (voice assistants)

---

This integration plan provides a comprehensive foundation for supporting Android clients while maintaining the existing InfoAgent server functionality and ensuring user privacy and security.