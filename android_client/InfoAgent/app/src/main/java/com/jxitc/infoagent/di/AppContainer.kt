package com.jxitc.infoagent.di

import android.content.Context
import com.jxitc.infoagent.data.database.InfoAgentDatabase
import com.jxitc.infoagent.data.repository.MemoryRepositoryImpl
import com.jxitc.infoagent.domain.repository.MemoryRepository
import com.jxitc.infoagent.domain.usecase.CreateMemoryUseCase
import com.jxitc.infoagent.domain.usecase.GetMemoriesUseCase
import com.jxitc.infoagent.data.local.AppPreferences
import com.jxitc.infoagent.data.remote.InfoAgentApiClient
import com.jxitc.infoagent.presentation.viewmodel.AddMemoryViewModel
import com.jxitc.infoagent.presentation.viewmodel.MemoryListViewModel
import com.jxitc.infoagent.presentation.viewmodel.SettingsViewModel

class AppContainer(private val context: Context) {
    
    private val database by lazy {
        InfoAgentDatabase.getDatabase(context.applicationContext)
    }
    
    val appPreferences by lazy {
        AppPreferences(context.applicationContext)
    }
    
    val apiClient by lazy {
        InfoAgentApiClient(appPreferences)
    }
    
    val memoryRepository: MemoryRepository by lazy {
        MemoryRepositoryImpl(database.memoryDao())
    }
    
    val createMemoryUseCase by lazy {
        CreateMemoryUseCase(memoryRepository)
    }
    
    val getMemoriesUseCase by lazy {
        GetMemoriesUseCase(memoryRepository)
    }
    
    fun createAddMemoryViewModel(): AddMemoryViewModel {
        return AddMemoryViewModel(createMemoryUseCase, apiClient, appPreferences)
    }
    
    fun createMemoryListViewModel(): MemoryListViewModel {
        return MemoryListViewModel(getMemoriesUseCase)
    }
    
    fun createSettingsViewModel(): SettingsViewModel {
        return SettingsViewModel(appPreferences, apiClient)
    }
}