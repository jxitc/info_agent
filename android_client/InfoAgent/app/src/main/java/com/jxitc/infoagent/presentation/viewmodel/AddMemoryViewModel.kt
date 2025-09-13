package com.jxitc.infoagent.presentation.viewmodel

import androidx.lifecycle.viewModelScope
import com.jxitc.infoagent.domain.model.MemoryCreationRequest
import com.jxitc.infoagent.domain.model.SourceType
import com.jxitc.infoagent.domain.usecase.CreateMemoryUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class AddMemoryViewModel(
    private val createMemoryUseCase: CreateMemoryUseCase
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