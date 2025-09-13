package com.jxitc.infoagent.presentation.viewmodel

import androidx.lifecycle.viewModelScope
import com.jxitc.infoagent.domain.model.Memory
import com.jxitc.infoagent.domain.usecase.GetMemoriesUseCase
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

class MemoryListViewModel(
    private val getMemoriesUseCase: GetMemoriesUseCase
) : BaseViewModel() {
    
    private val _memories = MutableStateFlow<List<Memory>>(emptyList())
    val memories: StateFlow<List<Memory>> = _memories.asStateFlow()
    
    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()
    
    init {
        loadMemories()
    }
    
    fun loadMemories() {
        viewModelScope.launch(exceptionHandler) {
            setLoading(true)
            try {
                getMemoriesUseCase.getRecentMemories(50).collect { memoriesList ->
                    _memories.value = memoriesList
                    setLoading(false)
                }
            } catch (e: Exception) {
                handleError("Failed to load memories: ${e.message}")
            }
        }
    }
    
    fun searchMemories(query: String) {
        _searchQuery.value = query
        
        viewModelScope.launch(exceptionHandler) {
            setLoading(true)
            try {
                getMemoriesUseCase.searchMemories(query).collect { memoriesList ->
                    _memories.value = memoriesList
                    setLoading(false)
                }
            } catch (e: Exception) {
                handleError("Failed to search memories: ${e.message}")
            }
        }
    }
    
    fun clearSearch() {
        _searchQuery.value = ""
        loadMemories()
    }
    
    fun refreshMemories() {
        clearError()
        if (_searchQuery.value.isBlank()) {
            loadMemories()
        } else {
            searchMemories(_searchQuery.value)
        }
    }
}