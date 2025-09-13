package com.jxitc.infoagent.presentation.viewmodel

import androidx.lifecycle.viewModelScope
import com.jxitc.infoagent.data.local.AppPreferences
import com.jxitc.infoagent.data.remote.InfoAgentApiClient
import com.jxitc.infoagent.domain.model.MemoryCreationRequest
import com.jxitc.infoagent.domain.model.ProcessingResult
import com.jxitc.infoagent.domain.model.SourceType
import com.jxitc.infoagent.domain.usecase.CreateMemoryUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AddMemoryViewModel(
    private val createMemoryUseCase: CreateMemoryUseCase,
    private val apiClient: InfoAgentApiClient,
    private val appPreferences: AppPreferences
) : BaseViewModel() {
    
    private val _content = MutableStateFlow("")
    val content: StateFlow<String> = _content.asStateFlow()
    
    private val _isSubmitted = MutableStateFlow(false)
    val isSubmitted: StateFlow<Boolean> = _isSubmitted.asStateFlow()
    
    fun updateContent(newContent: String) {
        _content.value = newContent
        clearError()
    }
    
    fun submitMemory() {
        val contentText = _content.value.trim()
        
        if (contentText.isEmpty()) {
            handleError("Please enter some content")
            return
        }
        
        val request = MemoryCreationRequest(
            content = contentText,
            sourceType = SourceType.MANUAL,
            metadata = mapOf("input_method" to "manual_text_input")
        )
        
        // Try server first if auto-sync is enabled, then fall back to local
        if (appPreferences.autoSync) {
            submitToServerWithFallback(request)
        } else {
            submitToLocalOnly(request)
        }
    }
    
    private fun submitToServerWithFallback(request: MemoryCreationRequest) {
        launchWithLoading(
            block = { 
                // Try server first
                when (val serverResult = apiClient.createMemory(request)) {
                    is ProcessingResult.Success -> {
                        // Server success - also save locally for offline access
                        val localMemory = serverResult.data.copy(isUploaded = true)
                        val localRequest = MemoryCreationRequest(
                            content = localMemory.content,
                            sourceType = localMemory.sourceType,
                            metadata = localMemory.metadata
                        )
                        createMemoryUseCase.execute(localRequest) // Save locally but ignore result
                        serverResult // Return server result
                    }
                    is ProcessingResult.Error -> {
                        // Server failed - save locally for later sync
                        createMemoryUseCase.execute(request)
                    }
                    ProcessingResult.Loading -> ProcessingResult.Loading
                }
            },
            onSuccess = { memory ->
                _isSubmitted.value = true
                _content.value = ""
            }
        )
    }
    
    private fun submitToLocalOnly(request: MemoryCreationRequest) {
        launchWithLoading(
            block = { createMemoryUseCase.execute(request) },
            onSuccess = { memory ->
                _isSubmitted.value = true
                _content.value = ""
            }
        )
    }
    
    fun resetSubmissionState() {
        _isSubmitted.value = false
    }
}