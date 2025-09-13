package com.jxitc.infoagent.data.local

import android.content.Context
import android.content.SharedPreferences
import com.jxitc.infoagent.utils.Logger

class AppPreferences(context: Context) {
    
    private val prefs: SharedPreferences = context.getSharedPreferences(
        PREFS_NAME, 
        Context.MODE_PRIVATE
    )
    
    var serverUrl: String
        get() = prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
        set(value) = prefs.edit().putString(KEY_SERVER_URL, value).apply()
    
    var autoSync: Boolean
        get() = prefs.getBoolean(KEY_AUTO_SYNC, DEFAULT_AUTO_SYNC)
        set(value) = prefs.edit().putBoolean(KEY_AUTO_SYNC, value).apply()
    
    var syncOnlyOnWifi: Boolean
        get() = prefs.getBoolean(KEY_SYNC_WIFI_ONLY, DEFAULT_SYNC_WIFI_ONLY)
        set(value) = prefs.edit().putBoolean(KEY_SYNC_WIFI_ONLY, value).apply()
    
    fun isServerConfigured(): Boolean {
        return serverUrl.isNotBlank() && serverUrl != DEFAULT_SERVER_URL
    }
    
    fun resetToDefaults() {
        prefs.edit().clear().apply()
        Logger.i("App preferences reset to defaults")
    }
    
    companion object {
        private const val PREFS_NAME = "info_agent_prefs"
        
        // Keys
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_AUTO_SYNC = "auto_sync"
        private const val KEY_SYNC_WIFI_ONLY = "sync_wifi_only"
        
        // Default values
        const val DEFAULT_SERVER_URL = "http://10.0.2.2:8000" // Android emulator localhost
        private const val DEFAULT_AUTO_SYNC = true
        private const val DEFAULT_SYNC_WIFI_ONLY = false
    }
}